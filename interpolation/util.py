# coding=utf-8
import torch
import torch.nn.functional as F
import numpy as np
import os
import random

def reverse_img_and_flow(img_a,img_b,flow,mask = None,lr=True,ud=True):
    with torch.no_grad():
        b,c,h,w = img_a.size()

        torchHorizontal = torch.linspace(-1.0, 1.0, w,device=torch.device('cuda')).view(1, 1, 1, w).expand(b, 1, h, w)
        torchVertical = torch.linspace(-1.0, 1.0, h,device=torch.device('cuda')).view(1, 1, h, 1).expand(b, 1, h, w)
        grid = torch.cat([torchHorizontal, torchVertical], 1)
        if lr:
            grid[:, 0, :, :] = -1*grid[:, 0, :, :]
        if ud:
            grid[:, 1, :, :] = -1*grid[:, 1, :, :]

        img_a = F.grid_sample(img_a, grid.permute(0, 2, 3, 1), padding_mode='border')
        img_b = F.grid_sample(img_b, grid.permute(0, 2, 3, 1), padding_mode='border')
        flow = F.grid_sample(flow, grid.permute(0, 2, 3, 1), padding_mode='border')
        if not (mask is None):
            mask = F.grid_sample(mask, grid.permute(0, 2, 3, 1), padding_mode='border')


        if lr:
            flow[:, 0, :, :] = -1 * flow[:, 0, :, :]
        if ud:
            flow[:, 1, :, :] = -1 * flow[:, 1, :, :]
    if mask is None:
        return img_a,img_b,flow
    else:
        return img_a, img_b, flow,mask



def color_random(img_list,pmin=0.,pmax=1.):
    ch_order = [0, 1, 2]
    reverse_flag = random.randint(0,1)
    random.shuffle(ch_order)
    img_out = []
    with torch.no_grad():
        for img in img_list:
            img_ch0 = img[:, ch_order[0]]
            img_ch1 = img[:, ch_order[1]]
            img_ch2 = img[:, ch_order[2]]
            img_new = torch.stack([img_ch0,img_ch1,img_ch2],dim=1)
            if reverse_flag:
                img_new = (pmax-img_new)+pmin
            img_out.append(img_new)
    return img_out



def flow_resize(flow0, size_out):
    ho, wo = size_out
    flow = flow0 * 1
    hf = flow.size(2)
    wf = flow.size(3)
    flow[:, 0, :, :] = flow[:, 0, :, :] / wf * wo
    flow[:, 1, :, :] = flow[:, 1, :, :] / hf * ho
    flow = F.interpolate(flow, size_out, mode='bilinear')
    return flow

def numpy2torch(npy):
    npy0 = npy[np.newaxis, :, :, :]
    ter = torch.from_numpy(npy0)
    ter = ter.cuda()
    ter = torch.transpose(ter, dim0=1, dim1=3)
    ter = torch.transpose(ter, dim0=2, dim1=3).float()
    return ter

def torch2numpy(ter):
    ter = torch.squeeze(ter, dim=0)
    ter = torch.transpose(ter, dim0=0, dim1=2)
    ter = torch.transpose(ter, dim0=0, dim1=1)
    npy = ter.cpu().data.numpy()
    return npy

def models_parameters(model_list):
    for model in model_list:
        for name, param in model.named_parameters():
            yield param

def psnr(img1,img2,peak=255):
    error = img1-img2
    mse = (error*error).mean()
    psnr = 10*torch.log10(peak*peak/mse)
    return psnr

def bwarp(pic_in, flow0):
    flow = flow0 * 1
    hp = pic_in.size(2)
    wp = pic_in.size(3)
    hf = flow.size(2)
    wf = flow.size(3)
    b = pic_in.size(0)
    flow[:, 0, :, :] = flow[:, 0, :, :] / wf * 2
    flow[:, 1, :, :] = flow[:, 1, :, :] / hf * 2

    flow = resize(flow, [hp, wp])
    torchHorizontal = torch.linspace(-1.0, 1.0, wp,device=torch.device('cuda')).view(1, 1, 1, wp).expand(b, 1, hp, wp)
    torchVertical = torch.linspace(-1.0, 1.0, hp,device=torch.device('cuda')).view(1, 1, hp, 1).expand(b, 1, hp, wp)
    grid = torch.cat([torchHorizontal, torchVertical], 1)
    pic_in = pic_in.float()
    pic_out = F.grid_sample(pic_in, (grid + flow).permute(0, 2, 3, 1), padding_mode='border')

    return pic_out

def resize(input,size_out):
    out_put = F.interpolate(input,size_out,mode='bilinear')
    return out_put

def plt_change(img_in):
    img_out = np.zeros_like(img_in)
    img_out[:, :, 0] = img_in[:, :, 2] * 1
    img_out[:, :, 1] = img_in[:, :, 1] * 1
    img_out[:, :, 2] = img_in[:, :, 0] * 1
    return img_out

def save_weight(model,epoch,step,path):
    if not os.path.exists(path):
        os.makedirs(path)
    save_path = path + "ckpt_" +str(epoch)+'_'+ str(step) + ".pkl"
    if torch.cuda.is_available():
        state = model.state_dict()
        torch.save(state, save_path)
    else:
        torch.save(model.state_dict(), save_path)
    step_path = path + "ckpt.txt"
    with open(step_path,'w') as f:
        f.write(str(epoch)+'\n')
        f.write(str(step)+'\n')
        f.close()

def load_weight(path):
    if not os.path.exists(path):
        os.makedirs(path)
    # step_path = path + "ckpt.txt"
    step_path =os.path.join(path, 'ckpt.txt')
    if os.path.exists(step_path):
        with open(step_path, 'r') as f:
            epoch = f.readline()
            place = epoch.find('\n')
            if place != -1:
                epoch = epoch[:place]
            step = f.readline()
            place = step.find('\n')
            if place != -1:
                step = step[:place]
            f.close()
        save_path = os.path.join(path, "ckpt_" + epoch+'_'+ step + ".pkl")
        # save_path = './ckpt/inter_2000.pkl'
        print("read weight:",save_path)
        return save_path,int(epoch),int(step),1
    else:
        print("new model:")
        return None,0,0,0

def adjust_num(input, output_num):

    input_num = input.size(1)
    rest = output_num%input_num
    cop = output_num/input_num
    if rest:
        con_list = [input[:,0:rest,:,:]]
    else:
        con_list = []
    for i in range(cop):
        con_list.append(input)
    out_put = torch.cat(con_list,dim=1)
    return out_put

def get_parameters(key_word_list,model):
    for name, param in model.named_parameters():
        for key_word in key_word_list:
            if key_word in name:
                yield param
                break


