import os
import sys
import time
from collections import OrderedDict

import numpy as np
import pandas as pd

from split_combine import SplitComb
from res18 import get_model
from preprocess import preprocess

import torch
from torch.utils.data import DataLoader
from torch.autograd import Variable
import matplotlib.pyplot as plt
plt.switch_backend('agg')

local_path = "D:/workspace/python/LCCAD/detector/"


def iou(box0, box1):
    r0 = box0[3] / 2
    s0 = box0[:3] - r0
    e0 = box0[:3] + r0
    r1 = box1[3] / 2
    s1 = box1[:3] - r1
    e1 = box1[:3] + r1
    overlap = []
    for i in range(len(s0)): overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))
    intersection = overlap[0] * overlap[1] * overlap[2]
    union = box0[3] * box0[3] * box0[3] + box1[3] * box1[3] * box1[3] - intersection
    return intersection / union


def nms(output, nms_th):
    if len(output) == 0: return output
    output = output[np.argsort(-output[:, 0])]
    bboxes = [output[0]]
    for i in np.arange(1, len(output)):
        bbox = output[i]
        flag = 1
        for j in range(len(bboxes)):
            if iou(bbox[1:5], bboxes[j][1:5]) >= nms_th:
                flag = -1
                break
        if flag == 1: bboxes.append(bbox)
    bboxes = np.asarray(bboxes, np.float32)
    return bboxes


def plt_result(name, islabel=True):
    result_save_path = local_path+"result_imgs/"+name+"/"
    if not os.path.exists(result_save_path):
        os.makedirs(result_save_path)
    CT_path = local_path + "temp/"
    detect_result_path = local_path + "pbbs/bbox/"
    patient_id = name
    patient_CT_data = CT_path + patient_id + "_clean.npy"
    if islabel:
        patient_CT_label = CT_path + patient_id + "_label.npy"
    patient_predict = detect_result_path + patient_id + "_pbb.npy"
    ctdat = np.load(patient_CT_data)
    if islabel:
        ctlab = np.load(patient_CT_label)
        print('Groundtruth')
        print(ctdat.shape, ctlab.shape)
        print(ctlab)
        result_save_label_path = result_save_path+'labels/'
        if not os.path.exists(result_save_label_path):
            os.makedirs(result_save_label_path)
        for idx in range(ctlab.shape[0]):
            if abs(ctlab[idx, 0]) + abs(ctlab[idx, 1]) + abs(ctlab[idx, 2]) + abs(ctlab[idx, 3]) == 0: continue
            fig = plt.figure()
            z, x, y = int(ctlab[idx, 0]), int(ctlab[idx, 1]), int(ctlab[idx, 2])
            print(z, x, y)
            dat0 = np.array(ctdat[0, z, :, :])
            dat0[max(0, x - 10):min(dat0.shape[0], x + 10), max(0, y - 10)] = 255
            dat0[max(0, x - 10):min(dat0.shape[0], x + 10), min(dat0.shape[1], y + 10)] = 255
            dat0[max(0, x - 10), max(0, y - 10):min(dat0.shape[1], y + 10)] = 255
            dat0[min(dat0.shape[0], x + 10), max(0, y - 10):min(dat0.shape[1], y + 10)] = 255
            plt.imshow(dat0,cmap='gray')
        plt.savefig(result_save_label_path + "label.jpg")

    pbb = np.load(patient_predict)
    # print("pbb origin: ")
    # print(pbb)
    # print(pbb[:,0])
    # print(pbb[pbb[:,1]>269 ])

    pbb = np.array(pbb[pbb[:, 0] > 0])
    print("pbb origin len: ", len(pbb))
    pbb = nms(pbb, 0.1)
    for idx in range(pbb.shape[0]):
        x=pbb[idx,0]
        s = 1 / (1 + np.exp(-x))
        pbb[idx,0]=s
    print("pbb after nms len: ", len(pbb))
    # print(pbb.shape, pbb)
    print('Detection Results according to confidence')
    result_save_predict_path = result_save_path+'predicts/'
    if not os.path.exists(result_save_predict_path):
        os.makedirs(result_save_predict_path)
    for idx in range(pbb.shape[0]):
        fig = plt.figure()
        z, x, y = int(pbb[idx, 1]), int(pbb[idx, 2]), int(pbb[idx, 3])
        if z >= ctdat.shape[1] or x >= ctdat.shape[2] or y >= ctdat.shape[3]:
            print("shape error")
            print("z, x, y is :", z, x, y, " ctshape is :", ctdat.shape)
            continue
        dat0 = np.array(ctdat[0, z, :, :])
        dat0[max(0, x - 10):min(dat0.shape[0] - 1, x + 10), max(0, y - 10)] = 255
        dat0[max(0, x - 10):min(dat0.shape[0] - 1, x + 10), min(dat0.shape[1] - 1, y + 10)] = 255
        dat0[max(0, x - 10), max(0, y - 10):min(dat0.shape[1] - 1, y + 10)] = 255
        dat0[min(dat0.shape[0] - 1, x + 10), max(0, y - 10):min(dat0.shape[1] - 1, y + 10)] = 255
        plt.imshow(dat0,cmap='gray')
        plt.savefig(result_save_predict_path + "predict" + str(idx).zfill(2) + ".jpg", bbox_inches='tight')
        print(idx, "pbb[idx,0]= ", pbb[idx, 0])
    plt.close()
    #
    df = pd.DataFrame(pbb,columns=['possibility','z','x','y','size'])
    df.to_csv(result_save_path+'predictResult.csv')


def plt_raw(name):
    CT_path = local_path + "temp/"
    patient_CT_path = CT_path + name + '_clean.npy'
    raw_data = np.load(patient_CT_path)
    if raw_data.shape[0] != 1:
        return "shape error"
    save_dir = local_path + "patient_imgs/" + name + "/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for z in range(raw_data.shape[1]):
        fig = plt.figure()
        dat0 = np.array(raw_data[0, z, :, :])
        plt.imshow(dat0, cmap='gray')

        plt.savefig(save_dir + "img" + str(z).zfill(3) + ".jpg", bbox_inches='tight')
    plt.close()
    return 0


def process(data_loader, net, get_pbb, save_dir, config):
    start_time = time.time()
    save_dir = os.path.join(save_dir, 'bbox')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print(save_dir)
    net.eval()
    namelist = []
    split_comber = data_loader.dataset.split_comber
    for i_name, (data, target, coord, nzhw) in enumerate(data_loader):
        # print("data shape= ", np.array(data).shape)
        # print("coord shape= ", len(coord))
        s = time.time()
        target = [np.asarray(t, np.float32) for t in target]
        lbb = target[0]
        nzhw = nzhw[0]
        name = data_loader.dataset.filenames[i_name].split('/')[-1].split('_clean')[0]  # .split('-')[0]  wentao change
        data = data[0][0]
        coord = coord[0][0]
        isfeat = False

        n_per_run = 1

        splitlist = list(range(0, len(data) + 1, n_per_run))
        if splitlist[-1] != len(data):
            splitlist.append(len(data))

        outputlist = []

        for i in range(len(splitlist) - 1):
            with torch.no_grad():
                input = Variable(data[splitlist[i]:splitlist[i + 1]]).cuda()
                inputcoord = Variable(coord[splitlist[i]:splitlist[i + 1]]).cuda()

                output = net(input, inputcoord)
            outputlist.append(output.data.cpu().numpy())
        output = np.concatenate(outputlist, 0)

        output = split_comber.combine(output, nzhw=nzhw)

        thresh = -3  # -8 #-3
        print('pbb thresh', thresh)
        pbb, mask = get_pbb(output, thresh, ismask=True)

        print([i_name, name])
        e = time.time()
        np.save(os.path.join(save_dir, name + '_pbb.npy'), pbb)
        np.save(os.path.join(save_dir, name + '_lbb.npy'), lbb)
    np.save(os.path.join(save_dir, 'namelist.npy'), namelist)
    end_time = time.time()

    print(('elapsed time is %3.2f seconds' % (end_time - start_time)))
    print()
    print()


def singletest(testdatadir, testfilename, islabel, config, net, get_pbb, save_dir):
    margin = 32
    sidelen = 80
    import SingleData
    split_comber = SplitComb(sidelen, config['max_stride'], config['stride'], margin, config['pad_value'])
    dataset = SingleData.SingleDataDetector(
        testdatadir,
        testfilename,
        islabel,
        config,
        phase='test',
        split_comber=split_comber)
    test_loader = DataLoader(
        dataset,
        batch_size=1,
        shuffle=False,
        num_workers=0,
        collate_fn=SingleData.collate,
        pin_memory=True)

    process(test_loader, net, get_pbb, save_dir, config)
    return


def detect_main(request_name, islabel):
    torch.manual_seed(0)
    torch.cuda.set_device(0)

    model_path = local_path + "model/099.ckpt"
    patient_name = request_name

    config, net, loss, get_pbb = get_model()
    checkpoint = torch.load(model_path)
    pretrained_net_dict = checkpoint['state_dict']
    new_dict = OrderedDict()
    for k, v in pretrained_net_dict.items():
        if k.startswith('module'):
            flag = True
            break
        else:
            flag = False
            break
    for k, v in pretrained_net_dict.items():
        if flag:
            name = k[7:]  # remove 'module'
            new_dict[name] = v
        else:
            new_dict[k] = v
    net.load_state_dict(new_dict)

    net = net.cuda()

    testdatadir = local_path + "temp/"
    singletest(testdatadir, patient_name, islabel, config, net, get_pbb, local_path + "pbbs/")


def flush_dirs(dirs):
    for dirpath in dirs:
        for f in os.listdir(dirpath):
            f_path = os.path.join(dirpath, f)
            os.remove(f_path)


def detect_service(name, islabel):
    # flushold = False
    # if flushold:
    #     dirs = [local_path + "temp/", local_path + "result_imgs/labels/", local_path + "result_imgs/predicts/",
    #             local_path + "pbbs/bbox/"]
    #     flush_dirs(dirs)
    #     print("flush complete")

    if not os.path.exists(os.path.join(local_path + "temp/", name + "_clean.npy")):
        preprocess(name, islabel)
    detect_main(name, islabel)
    plt_result(name, islabel)


if __name__ == '__main__':
    name = "1.3.6.1.4.1.14519.5.2.1.6279.6001.102681962408431413578140925249"
    islabel = False
    flushold = True
    if flushold:
        dirs = [local_path + "temp/", local_path + "result_imgs/labels/", local_path + "result_imgs/predicts/",
                local_path + "pbbs/bbox/"]
        # dirs=["./result_imgs/labels/", "result_imgs/predicts/","./pbbs/bbox/"]
        flush_dirs(dirs)
        print("flush complete")

    if not os.path.exists(os.path.join(local_path + "temp/", name + "_clean.npy")):
        preprocess(name, islabel)
    detect_main(name, islabel)
    plt_result(name, islabel)
