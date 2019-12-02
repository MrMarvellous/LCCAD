# coding=utf-8
import torch
import torch.nn as nn
import torch.nn.functional as F
import time
import numpy as np
from util import bwarp, resize, flow_resize

from DepthFlowProjection.DepthFlowProjectionModule import DepthFlowProjectionModule
def FlowProject(inputs, depth):

    outputs = [DepthFlowProjectionModule(input.requires_grad)(input, depth) for input in inputs]

    return outputs

class INTER_NET(nn.Module):
    def __init__(self):
        super(INTER_NET, self).__init__()

        self.dep_net = DEP_NET()

        ch_num = [32, 64, 96, 128, 256]
        self.conv0 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(64, ch_num[0], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv1 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0], ch_num[1], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv2 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[1], ch_num[2], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv3 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[2], ch_num[3], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv4 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[3], ch_num[4], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv5 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[4], ch_num[4], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv6 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[3] + ch_num[4], ch_num[3], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv7 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[2] + ch_num[3], ch_num[2], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv8 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[1] + ch_num[2], ch_num[1], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv9 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0] + ch_num[1], ch_num[0], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv_img = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0], 1, kernel_size=3, stride=1, padding=0, bias=True),
        )

        self.conv_context = nn.Sequential(
            nn.ReplicationPad2d((3, 3, 3, 3)),
            nn.Conv2d(3, 32, kernel_size=7, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

    def forward(self, img_a, img_c, flow_a2c, flow_c2a, time):
        context_a = self.conv_context(img_a)
        context_c = self.conv_context(img_c)

        flow_a2b = flow_a2c * time
        flow_c2b = flow_c2a * (1 - time)
        dep_a = self.dep_net(img_a)
        dep_c = self.dep_net(img_c)

        flow_ba = FlowProject([flow_a2b], dep_a)[0]
        flow_bc = FlowProject([flow_c2b], dep_c)[0]

        warp_a = bwarp(context_a, flow_ba)
        warp_c = bwarp(context_c, flow_bc)
        conv0_imput = torch.cat([warp_a,warp_c],dim=1)
        conv0 = self.conv0(conv0_imput)
        conv1 = self.conv1(conv0)
        conv2 = self.conv2(conv1)
        conv3 = self.conv3(conv2)
        conv4 = self.conv4(conv3)
        conv5 = self.conv5(conv4)
        conv_cat = torch.cat([resize(conv5, [conv3.size(2), conv3.size(3)]), conv3], dim=1)
        conv6 = self.conv6(conv_cat)
        conv_cat = torch.cat([resize(conv6, [conv2.size(2), conv2.size(3)]), conv2], dim=1)
        conv7 = self.conv7(conv_cat)
        conv_cat = torch.cat([resize(conv7, [conv1.size(2), conv1.size(3)]), conv1], dim=1)
        conv8 = self.conv8(conv_cat)
        conv_cat = torch.cat([resize(conv8, [conv0.size(2), conv0.size(3)]), conv0], dim=1)
        conv9 = self.conv9(conv_cat)
        img = self.conv_img(conv9)
        img = torch.cat([img,img,img],dim=1)
        return img


class DEP_NET(nn.Module):
    def __init__(self):
        super(DEP_NET, self).__init__()
        ch_num = [4, 8, 16, 32, 64]
        self.conv0 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(3, ch_num[0], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv1 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0], ch_num[1], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv2 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[1], ch_num[2], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv3 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[2], ch_num[3], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )
        self.conv4 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[3], ch_num[4], kernel_size=3, stride=2, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv5 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[4], ch_num[4], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv6 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[3] + ch_num[4], ch_num[3], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv7 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[2] + ch_num[3], ch_num[2], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv8 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[1] + ch_num[2], ch_num[1], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv9 = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0] + ch_num[1], ch_num[0], kernel_size=3, stride=1, padding=0, bias=True),
            nn.ReLU(inplace=True),
        )

        self.conv_dep = nn.Sequential(
            nn.ReplicationPad2d((1, 1, 1, 1)),
            nn.Conv2d(ch_num[0], 1, kernel_size=3, stride=1, padding=0, bias=True),
        )

    def forward(self, img):
        conv0 = self.conv0(img)
        conv1 = self.conv1(conv0)
        conv2 = self.conv2(conv1)
        conv3 = self.conv3(conv2)
        conv4 = self.conv4(conv3)
        conv5 = self.conv5(conv4)
        conv_cat = torch.cat([resize(conv5, [conv3.size(2), conv3.size(3)]), conv3], dim=1)
        conv6 = self.conv6(conv_cat)
        conv_cat = torch.cat([resize(conv6, [conv2.size(2), conv2.size(3)]), conv2], dim=1)
        conv7 = self.conv7(conv_cat)
        conv_cat = torch.cat([resize(conv7, [conv1.size(2), conv1.size(3)]), conv1], dim=1)
        conv8 = self.conv8(conv_cat)
        conv_cat = torch.cat([resize(conv8, [conv0.size(2), conv0.size(3)]), conv0], dim=1)
        conv9 = self.conv9(conv_cat)
        dep = self.conv_dep(conv9)
        dep = 1e-6 + 1 / torch.exp(dep)
        return dep
