"""
implementation of the PWC-DC network for optical flow estimation by Sun et al., 2018

Jinwei Gu and Zhile Ren

"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import os
os.environ['PYTHON_EGG_CACHE'] = 'tmp/' # a writable directory

import numpy as np
from util import  bwarp,resize,flow_resize


def conv(in_planes, out_planes, kernel_size=3, stride=1, padding=1, dilation=1):
    return nn.Sequential(
            nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride,
                        padding=padding, dilation=dilation, bias=True),
            nn.LeakyReLU(0.1))

def predict_flow(in_planes):
    return nn.Conv2d(in_planes,2,kernel_size=3,stride=1,padding=1,bias=True)

def deconv(in_planes, out_planes, kernel_size=4, stride=2, padding=1):
    return nn.ConvTranspose2d(in_planes, out_planes, kernel_size, stride, padding, bias=True)

import time

def dense_warp(fea_a,fea_c,i_list,j_list,flow=None):
    bp, cp, hp, wp = fea_a.size()
    if flow is None:
        flow = torch.zeros([bp, 2, hp, wp], device=torch.device('cuda'))

    bf, cf, hf, wf = flow.size()
    assert fea_a.size() == fea_c.size(), 'feature must have same size'
    assert cf == 2, 'channel of flow must be 2'
    w_norm = torch.ones([bf, hf, wf], device=torch.device('cuda')) / wf * 2
    h_norm = torch.ones([bf, hf, wf], device=torch.device('cuda')) / hf * 2
    flow_norm = torch.stack([w_norm, h_norm], dim=1)
    flow = flow * flow_norm
    if hf != hp or wf != wp:
        flow = resize(flow, [hp, wp])

    torchHorizontal = torch.linspace(-1.0, 1.0, wp, device=torch.device('cuda')).view(1, 1, 1, wp).expand(bp, 1, hp,
                                                                                                          wp)
    torchVertical = torch.linspace(-1.0, 1.0, hp, device=torch.device('cuda')).view(1, 1, hp, 1).expand(bp, 1, hp,
                                                                                                        wp)
    grid = torch.cat([torchHorizontal, torchVertical], 1)

    grid_flow = (grid + flow)

    num = i_list.size(0)
    move_i = (i_list / hp).view(1, num, 1, 1).expand(bp, num, hp, wp).contiguous()
    move_j = (j_list / wp).view(1, num, 1, 1).expand(bp, num, hp, wp).contiguous()

    add = torch.stack([move_j, move_i], dim=2)

    grid_flow = grid_flow.view(bp, 1, 2, hp, wp)

    grid_flow_ex = grid_flow.view(bp, 1, 2, hp, wp).expand(bp, num, 2, hp, wp).contiguous()

    grid_flow_ex = grid_flow_ex + add

    grid_flow_ex = grid_flow_ex.view(bp * num , 2, hp, wp)

    fea_a = fea_a.view(bp, 1, cp, hp, wp).expand(bp, num, cp, hp, wp).contiguous().view(bp * num, cp,
                                                                                              hp, wp)
    fea_c = fea_c.view(bp, 1, cp, hp, wp).expand(bp, num, cp, hp, wp).contiguous().view(bp * num , cp,
                                                                                              hp, wp)


    fea_c_w = F.grid_sample(fea_c, grid_flow_ex.permute(0, 2, 3, 1), padding_mode='border')

    corr = (fea_a-fea_c_w).abs().mean(dim=1)
    corr = corr.view(bp, num, hp, wp)
    return corr



class PWCDCNet(nn.Module):
    """
    PWC-DC net. add dilation convolution and densenet connections

    """
    def __init__(self, md=4):
        """
        input: md --- maximum displacement (for correlation. default: 4), after warpping

        """

        super(PWCDCNet,self).__init__()

        self.conv1a  = conv(3,   16, kernel_size=3, stride=2)
        self.conv1aa = conv(16,  16, kernel_size=3, stride=1)
        self.conv1b  = conv(16,  16, kernel_size=3, stride=1)
        self.conv2a  = conv(16,  32, kernel_size=3, stride=2)
        self.conv2aa = conv(32,  32, kernel_size=3, stride=1)
        self.conv2b  = conv(32,  32, kernel_size=3, stride=1)
        self.conv3a  = conv(32,  64, kernel_size=3, stride=2)
        self.conv3aa = conv(64,  64, kernel_size=3, stride=1)
        self.conv3b  = conv(64,  64, kernel_size=3, stride=1)
        self.conv4a  = conv(64,  96, kernel_size=3, stride=2)
        self.conv4aa = conv(96,  96, kernel_size=3, stride=1)
        self.conv4b  = conv(96,  96, kernel_size=3, stride=1)
        self.conv5a  = conv(96, 128, kernel_size=3, stride=2)
        self.conv5aa = conv(128,128, kernel_size=3, stride=1)
        self.conv5b  = conv(128,128, kernel_size=3, stride=1)
        self.conv6aa = conv(128,192, kernel_size=3, stride=2)
        self.conv6a  = conv(192,192, kernel_size=3, stride=1)
        self.conv6b  = conv(192,192, kernel_size=3, stride=1)


        self.leakyRELU = nn.LeakyReLU(0.1)

        nd = (2*md+1)**2


        self.sr6_i = nn.Parameter(torch.randn(nd) * 3)
        self.sr6_j = nn.Parameter(torch.randn(nd) * 3)
        self.sr5_i = nn.Parameter(torch.randn(nd) * 3)
        self.sr5_j = nn.Parameter(torch.randn(nd) * 3)
        self.sr4_i = nn.Parameter(torch.randn(nd) * 3)
        self.sr4_j = nn.Parameter(torch.randn(nd) * 3)
        self.sr3_i = nn.Parameter(torch.randn(nd) * 3)
        self.sr3_j = nn.Parameter(torch.randn(nd) * 3)
        self.sr2_i = nn.Parameter(torch.randn(nd) * 3)
        self.sr2_j = nn.Parameter(torch.randn(nd) * 3)



        dd = np.cumsum([128,128,96,64,32],dtype=np.int32).astype(np.int)
        dd = [int(d) for d in dd]

        od = nd
        self.conv6_0 = conv(od,      128, kernel_size=3, stride=1)
        self.conv6_1 = conv(od+dd[0],128, kernel_size=3, stride=1)
        self.conv6_2 = conv(od+dd[1],96,  kernel_size=3, stride=1)
        self.conv6_3 = conv(od+dd[2],64,  kernel_size=3, stride=1)
        self.conv6_4 = conv(od+dd[3],32,  kernel_size=3, stride=1)
        self.predict_flow6 = predict_flow(od+dd[4])

        self.upfeat6 = conv(od+dd[4], 2, kernel_size=3, stride=1, padding=1)

        od = nd+128+4
        self.conv5_0 = conv(od,      128, kernel_size=3, stride=1)
        self.conv5_1 = conv(od+dd[0],128, kernel_size=3, stride=1)
        self.conv5_2 = conv(od+dd[1],96,  kernel_size=3, stride=1)
        self.conv5_3 = conv(od+dd[2],64,  kernel_size=3, stride=1)
        self.conv5_4 = conv(od+dd[3],32,  kernel_size=3, stride=1)
        self.predict_flow5 = predict_flow(od+dd[4])

        self.upfeat5 = conv(od+dd[4], 2, kernel_size=3, stride=1, padding=1)

        od = nd+96+4
        self.conv4_0 = conv(od,      128, kernel_size=3, stride=1)
        self.conv4_1 = conv(od+dd[0],128, kernel_size=3, stride=1)
        self.conv4_2 = conv(od+dd[1],96,  kernel_size=3, stride=1)
        self.conv4_3 = conv(od+dd[2],64,  kernel_size=3, stride=1)
        self.conv4_4 = conv(od+dd[3],32,  kernel_size=3, stride=1)
        self.predict_flow4 = predict_flow(od+dd[4])

        self.upfeat4 = conv(od+dd[4], 2, kernel_size=3, stride=1, padding=1)

        od = nd+64+4
        self.conv3_0 = conv(od,      128, kernel_size=3, stride=1)
        self.conv3_1 = conv(od+dd[0],128, kernel_size=3, stride=1)
        self.conv3_2 = conv(od+dd[1],96,  kernel_size=3, stride=1)
        self.conv3_3 = conv(od+dd[2],64,  kernel_size=3, stride=1)
        self.conv3_4 = conv(od+dd[3],32,  kernel_size=3, stride=1)
        self.predict_flow3 = predict_flow(od+dd[4])

        self.upfeat3 = conv(od+dd[4], 2, kernel_size=3, stride=1, padding=1)

        od = nd+32+4
        self.conv2_0 = conv(od,      128, kernel_size=3, stride=1)
        self.conv2_1 = conv(od+dd[0],128, kernel_size=3, stride=1)
        self.conv2_2 = conv(od+dd[1],96,  kernel_size=3, stride=1)
        self.conv2_3 = conv(od+dd[2],64,  kernel_size=3, stride=1)
        self.conv2_4 = conv(od+dd[3],32,  kernel_size=3, stride=1)
        self.predict_flow2 = predict_flow(od+dd[4])

        self.dc_conv1 = conv(od+dd[4], 128, kernel_size=3, stride=1, padding=1,  dilation=1)
        self.dc_conv2 = conv(128,      128, kernel_size=3, stride=1, padding=2,  dilation=2)
        self.dc_conv3 = conv(128,      128, kernel_size=3, stride=1, padding=4,  dilation=4)
        self.dc_conv4 = conv(128,      96,  kernel_size=3, stride=1, padding=8,  dilation=8)
        self.dc_conv5 = conv(96,       64,  kernel_size=3, stride=1, padding=16, dilation=16)
        self.dc_conv6 = conv(64,       32,  kernel_size=3, stride=1, padding=1,  dilation=1)
        self.dc_conv7 = predict_flow(32)

        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
                nn.init.kaiming_normal_(m.weight.data, mode='fan_in')
                if m.bias is not None:
                    m.bias.data.zero_()

        W_MAX = 2048
        H_MAX = 1024
        B_MAX = 8
        xx = torch.arange(0, W_MAX,device=torch.device('cuda') ).view(1,-1).repeat(H_MAX,1)
        yy = torch.arange(0, H_MAX,device=torch.device('cuda') ).view(-1,1).repeat(1,W_MAX)
        xx = xx.view(1,1,H_MAX,W_MAX).repeat(B_MAX,1,1,1)
        yy = yy.view(1,1,H_MAX,W_MAX).repeat(B_MAX,1,1,1)
        grid = torch.cat((xx,yy),1).float()

        ## for saving time on allocating a grid in forward
        self.W_MAX = W_MAX
        self.H_MAX = H_MAX
        self.B_MAX = B_MAX
        self.grid = Variable(grid, requires_grad=False)
        # self.mask_base = Variable(torch.cuda.FloatTensor().resize_(B_MAX,).zero_() + 1)

        self.div_flow = 0.05


    def warp(self, x, flo):

        return bwarp(x, flo)


    def forward(self,im1,im2, output_more = False):
        # print("\n\n***************************PWC Net details *************** \n\n")
        # start=  time.time()
        c11 = self.conv1b(self.conv1aa(self.conv1a(im1)))
        c21 = self.conv1b(self.conv1aa(self.conv1a(im2)))
        c12 = self.conv2b(self.conv2aa(self.conv2a(c11)))
        c22 = self.conv2b(self.conv2aa(self.conv2a(c21)))
        c13 = self.conv3b(self.conv3aa(self.conv3a(c12)))
        c23 = self.conv3b(self.conv3aa(self.conv3a(c22)))
        c14 = self.conv4b(self.conv4aa(self.conv4a(c13)))
        c24 = self.conv4b(self.conv4aa(self.conv4a(c23)))
        c15 = self.conv5b(self.conv5aa(self.conv5a(c14)))
        c25 = self.conv5b(self.conv5aa(self.conv5a(c24)))
        c16 = self.conv6b(self.conv6a(self.conv6aa(c15)))
        c26 = self.conv6b(self.conv6a(self.conv6aa(c25)))
        # print("features " +str(time.time()- start))
        # start=  time.time()
        corr6 = dense_warp(c16, c26, self.sr6_i, self.sr6_j)

        x = torch.cat((self.conv6_0(corr6), corr6),1)
        x = torch.cat((self.conv6_1(x), x),1)
        x = torch.cat((self.conv6_2(x), x),1)
        x = torch.cat((self.conv6_3(x), x),1)
        x = torch.cat((self.conv6_4(x), x),1)
        flow6 = self.predict_flow6(x)
        flow6 = flow6/self.div_flow


        up_flow6 = flow_resize(flow6,(c25.size(2),c25.size(3)))
        up_feat6 = resize(self.upfeat6(x),(c25.size(2),c25.size(3)))
        # print("level6 " +str(time.time()- start))
        # start=  time.time()


        # print("level5_1 " + str(time.time() - start))
        # start5 = time.time()
        corr5 = dense_warp(c15, c25, self.sr5_i, self.sr5_j, flow6)
        # print("level5_2 " + str(time.time() - start5))
        # start5 = time.time()


        x = torch.cat((corr5, c15, up_flow6*self.div_flow, up_feat6), 1)
        x = torch.cat((self.conv5_0(x), x),1)
        x = torch.cat((self.conv5_1(x), x),1)
        x = torch.cat((self.conv5_2(x), x),1)
        x = torch.cat((self.conv5_3(x), x),1)
        x = torch.cat((self.conv5_4(x), x),1)
        flow5 = self.predict_flow5(x)
        flow5 = flow5 / self.div_flow + up_flow6
        up_flow5 = flow_resize(flow5,(c24.size(2),c24.size(3)))
        up_feat5 = resize(self.upfeat5(x),(c24.size(2),c24.size(3)))

        # print("level5_3 " + str(time.time() - start5))
        # print("level5 " + str(time.time() - start))
        # start = time.time()

        corr4 = dense_warp(c14, c24, self.sr4_i, self.sr4_j, flow5)

        x = torch.cat((corr4, c14, up_flow5*self.div_flow, up_feat5), 1)
        x = torch.cat((self.conv4_0(x), x),1)
        x = torch.cat((self.conv4_1(x), x),1)
        x = torch.cat((self.conv4_2(x), x),1)
        x = torch.cat((self.conv4_3(x), x),1)
        x = torch.cat((self.conv4_4(x), x),1)
        flow4 = self.predict_flow4(x)
        flow4 = flow4 / self.div_flow + up_flow5
        up_flow4 = flow_resize(flow4,(c23.size(2),c23.size(3)))
        up_feat4 = resize(self.upfeat4(x),(c23.size(2),c23.size(3)))

        # print("level4 " + str(time.time() - start))
        # start = time.time()


        corr3 = dense_warp(c13, c23, self.sr3_i, self.sr3_j, flow4)



        x = torch.cat((corr3, c13, up_flow4*self.div_flow, up_feat4), 1)
        x = torch.cat((self.conv3_0(x), x),1)
        x = torch.cat((self.conv3_1(x), x),1)
        x = torch.cat((self.conv3_2(x), x),1)
        x = torch.cat((self.conv3_3(x), x),1)
        x = torch.cat((self.conv3_4(x), x),1)
        flow3 = self.predict_flow3(x)
        flow3 = flow3 / self.div_flow + up_flow4
        up_flow3 = flow_resize(flow3,(c22.size(2),c22.size(3)))
        up_feat3 = resize(self.upfeat3(x),(c22.size(2),c22.size(3)))

        # print("level3 " + str(time.time() - start))
        # start = time.time()

        corr2 = dense_warp(c12, c22, self.sr2_i, self.sr2_j, flow3)

        corr2 = self.leakyRELU(corr2)
        x = torch.cat((corr2, c12, up_flow3*self.div_flow, up_feat3), 1)
        x = torch.cat((self.conv2_0(x), x),1)
        x = torch.cat((self.conv2_1(x), x),1)
        x = torch.cat((self.conv2_2(x), x),1)
        x = torch.cat((self.conv2_3(x), x),1)
        x = torch.cat((self.conv2_4(x), x),1)
        flow2 = self.predict_flow2(x)
        flow2 = flow2 / self.div_flow + up_flow3
        # print("level2 " + str(time.time() - start))
        # start = time.time()

        x = self.dc_conv4(self.dc_conv3(self.dc_conv2(self.dc_conv1(x))))
        flow2 += self.dc_conv7(self.dc_conv6(self.dc_conv5(x)))
        # print("refine " + str(time.time() - start))
        # start = time.time()

        # we don't have the gt for flow, we just fine tune it on flownets

        if not output_more:
            return flow2
        else:
            return [flow2,flow3,flow4,flow5,flow6]
        # if self.training:
        #     return flow2,flow3,flow4,flow5,flow6
        # else:
        #     return flow2


