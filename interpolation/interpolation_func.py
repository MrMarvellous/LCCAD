# coding=utf-8
import os
import torch
import torch.nn as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import numpy as np
import cv2
import shutil
import torch.nn.functional as F
import math
import random
import time
import util
import flowlib
from PWCNet.PWCNet import PWCDCNet
from data_davis import DAVIS
from inter_model import INTER_NET
from config_interpolation import config_interpolation


def train_flow():
    data_path = "/home/gdh-95/ct_inter/new_data_squ/"
    dataset = DAVIS(data_path, shuffle=True)

    model = PWCDCNet().cuda().train()
    lr = 1e-5
    betas = (0.9, 0.999)
    wd = 4e-4

    weight_param = []
    other_param = []

    for name, param in model.named_parameters():
        # print(name)
        if 'weight' in name:
            # print(name)
            weight_param.append(param)
        else:
            # print(name)
            other_param.append(param)

    optimizer = torch.optim.Adam([{'params': weight_param, 'weight_decay': wd},
                                  {'params': other_param, 'weight_decay': 0}, ], lr, betas)

    ckpt_net_path = "./ckpt_net/"
    data_path, epoch0, step0, ckpt_opt_exist = util.load_weight(ckpt_net_path)
    if ckpt_opt_exist:
        model.load_state_dict(torch.load(data_path))

    ckpt_opt_path = "./ckpt_opt/"
    data_path, epoch0_optimizer, step0_optimizer, ckpt_exist = util.load_weight(ckpt_opt_path)
    # if epoch0_optimizer != epoch0 or step0_optimizer != step0:
    #     print('optimizer0 epoch0 error')
    #     return
    # else:
    #     if ckpt_exist:
    #         optimizer.load_state_dict(torch.load(data_path))

    random.seed(time.time())

    if ckpt_exist:
        step0 += 1
    batch_step = 1
    max_step = 5000 * 1000
    epe_filter = 0.004
    p_filter = 0.999

    for k in range(step0, max_step):
        with torch.no_grad():
            img_a, img_b, img_c, img_d = dataset[k]
            if random.randint(0, 1):
                img_a = img_b
                img_b = img_c
                img_c = img_d

            if random.randint(0, 1):
                change_img = img_a
                img_a = img_c
                img_c = change_img

            img_a = util.numpy2torch(img_a) / 255. - 0.5
            img_b = util.numpy2torch(img_b) / 255. - 0.5
            img_c = util.numpy2torch(img_c) / 255. - 0.5

        flow_a2c = model(img_a, img_c, False)
        flow_c2a = model(img_c, img_a, False)

        img_b2a = util.bwarp(img_b, flow_a2c * 0.5)
        img_b2c = util.bwarp(img_b, flow_c2a * 0.5)

        error_a = (img_b2a - img_a).abs().mean()
        error_c = (img_b2c - img_c).abs().mean()

        loss = (error_a + error_c) * 0.5

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        l1_c = error_a.cpu().data.numpy()
        l2_c = error_c.cpu().data.numpy()
        l_c = loss.cpu().data.numpy()
        epe_filter = (1 - p_filter) * l_c + p_filter * epe_filter

        print(
            "k-", k,
            " l1:", '%.5f' % float(l1_c),
            " l2:", '%.5f' % float(l2_c),
            " la:", '%.5f' % float(epe_filter),
        )
        if k % 5000 == 0:
            print("save weight at epoch:%d  step:%d" % (0, k))
            util.save_weight(model, 0, k, ckpt_net_path)
            util.save_weight(optimizer, 0, k, ckpt_opt_path)


def train_inter():
    inter_net = INTER_NET().cuda().train()
    flow_net = PWCDCNet().cuda().eval()

    lr = 5e-5
    betas = (0.9, 0.999)
    wd = 1e-4

    weight_param = []
    other_param = []

    for name, param in inter_net.named_parameters():
        # print(name)
        if 'weight' in name:
            # print(name)
            weight_param.append(param)
        else:
            # print(name)
            other_param.append(param)

    optimizer = torch.optim.Adam([{'params': weight_param, 'weight_decay': wd},
                                  {'params': other_param, 'weight_decay': 0}], lr=lr, betas=betas, weight_decay=wd)

    ckpt_net_path = "./ckpt_net/"
    data_path, epoch0, step0, ckpt_opt_exist = util.load_weight(ckpt_net_path)
    if ckpt_opt_exist:
        flow_net.load_state_dict(torch.load(data_path))

    ckpt_net_path = "./ckpt_inter/"
    data_path, epoch0, step0, ckpt_opt_exist = util.load_weight(ckpt_net_path)
    if ckpt_opt_exist:
        inter_net.load_state_dict(torch.load(data_path))

    ckpt_opt_path = "./ckpt_optinter/"
    data_path, epoch0_optimizer, step0_optimizer, ckpt_exist = util.load_weight(ckpt_opt_path)
    if epoch0_optimizer != epoch0 or step0_optimizer != step0:
        print('optimizer0 epoch0 error')
        return
    else:
        if ckpt_exist:
            optimizer.load_state_dict(torch.load(data_path))

    data_path = "/home/gdh-95/ct_inter/new_data_squ/"
    dataset = DAVIS(data_path, shuffle=True)

    lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,
                                                              T_max=50, eta_min=5e-6)

    if ckpt_exist:
        step0 += 1
    batch_step = 1
    max_step = 5000 * 51
    epe_filter = 0.1
    p_filter = 0.999
    step_epoch = 5000

    for k in range(step0 // step_epoch - 1):
        lr_scheduler.step()
    lr = lr_scheduler.get_lr()[0]

    for k in range(step0, max_step):
        print('step-', k, end=' ')
        if k % step_epoch == 0:
            lr_scheduler.step()
            lr = lr_scheduler.get_lr()[0]

        with torch.no_grad():
            img_a, img_b, img_c, img_d = dataset[k]
            if random.randint(0, 1):
                change_img = img_a
                img_a = img_d
                img_d = change_img

                change_img = img_b
                img_b = img_c
                img_c = change_img

            img_a = util.numpy2torch(img_a) / 255. - 0.5
            img_b = util.numpy2torch(img_b) / 255. - 0.5
            img_c = util.numpy2torch(img_c) / 255. - 0.5
            img_d = util.numpy2torch(img_d) / 255. - 0.5

            flow_a2d = flow_net(img_a, img_d, False)
            flow_d2a = flow_net(img_d, img_a, False)

        if k % 6 < 2:
            print('1/3', end=' ')
            inter_out = inter_net(img_a, img_d, flow_a2d, flow_d2a, time=1. / 3)
            error = (inter_out - img_b).abs().mean()
        elif k % 6 < 4:
            print('2/3', end=' ')
            inter_out = inter_net(img_a, img_d, flow_a2d, flow_d2a, time=2. / 3)
            error = (inter_out - img_c).abs().mean()
        elif k % 6 == 4:
            print('0/3', end=' ')
            inter_out = inter_net(img_a, img_d, flow_a2d, flow_d2a, time=0)
            error = (inter_out - img_a).abs().mean()
        else:
            print('3/3', end=' ')
            inter_out = inter_net(img_a, img_d, flow_a2d, flow_d2a, time=1)
            error = (inter_out - img_d).abs().mean()

        error_c = error.cpu().data.numpy()
        error.backward()
        epe_filter = (1 - p_filter) * error_c + p_filter * epe_filter
        optimizer.step()
        optimizer.zero_grad()
        print(" l:", '%.6f' % float(error_c),
              " le:", '%.6f' % float(epe_filter),
              " lr:", '%.5e' % float(lr)
              )
        if k % step_epoch == 0:
            print("save weight at epoch:%d  step:%d" % (0, k))
            util.save_weight(inter_net, 0, k, ckpt_net_path)
            util.save_weight(optimizer, 0, k, ckpt_opt_path)


def view_inter(dirname):
    torch.set_grad_enabled(False)
    inter_net = INTER_NET().cuda().eval()
    flow_net = PWCDCNet().cuda().eval()
    ckpt_net_path = config_interpolation['flow_model']
    data_path, epoch0, step0, ckpt_opt_exist = util.load_weight(ckpt_net_path)
    if ckpt_opt_exist:
        flow_net.load_state_dict(torch.load(data_path))

    ckpt_net_path = config_interpolation['inter_model']
    data_path, epoch0, step0, ckpt_opt_exist = util.load_weight(ckpt_net_path)
    if ckpt_opt_exist:
        inter_net.load_state_dict(torch.load(data_path))
    out_path = os.path.join(config_interpolation['out_path'], dirname)
    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    os.makedirs(out_path)

    # data_path = '/home/cuiyang/workspace/lung_cancer/ct_flow02_new/ct_data_png/gaoqiaoyu/'
    data_path = os.path.join(config_interpolation['data_path'], dirname, 'origin')
    print('data path: ', data_path)
    img_list = sorted(os.listdir(data_path))
    inter_num = 5  # 每两帧之间增加新帧的数量
    img_num = len(img_list)
    for k in range(img_num - 1):
        print(k)
        img_a = cv2.imread(os.path.join(data_path, img_list[k]))
        img_b = cv2.imread(os.path.join(data_path, img_list[k + 1]))
        cv2.imwrite(out_path + '/img_' + str(k).zfill(3) + '.jpg', img_a)
        if k == img_num - 2:
            cv2.imwrite(out_path + '/img_' + str(k + 1).zfill(3) + '.jpg', img_b)

        img_a = util.numpy2torch(img_a) / 255. - 0.5
        img_b = util.numpy2torch(img_b) / 255. - 0.5

        # img_a = resize(img_a, [480, 640])
        # img_b = resize(img_b, [480, 640])

        time0 = time.time()

        flow_a2b = flow_net(img_a, img_b, False)
        flow_b2a = flow_net(img_b, img_a, False)
        time1 = time.time()

        flow_a2b0 = util.torch2numpy(flow_a2b)
        flow_a2b0 = flowlib.flow_to_image(flow_a2b0)

        flow_b2a0 = util.torch2numpy(flow_b2a)
        flow_b2a0 = flowlib.flow_to_image(flow_b2a0)

        cv2.imwrite(out_path + '/flow_' + str(k).zfill(3) + '_f' + '.jpg', flow_a2b0)
        cv2.imwrite(out_path + '/flow_' + str(k).zfill(3) + '_b' + '.jpg', flow_b2a0)
        for kk in range(inter_num - 1):
            time2 = time.time()
            img_i = inter_net(img_a, img_b, flow_a2b, flow_b2a, time=float(kk + 1) / inter_num)
            time3 = time.time()
            img_i = (util.torch2numpy(img_i) + 0.5) * 255
            cv2.imwrite(out_path + '/img_' + str(k).zfill(3) + '_' + str(kk + 1) + '.jpg', img_i)

    print("inter complete.")
