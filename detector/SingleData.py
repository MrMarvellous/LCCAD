import collections
import os
import time

import numpy as np
import torch
from torch.utils.data import Dataset


class SingleDataDetector(Dataset):
    def __init__(self, data_dir, patient_name, islabel, config, phase='test', split_comber=None):
        self.stride = config['stride']  # 4
        self.pad_value = config['pad_value']  # 170
        self.split_comber = split_comber
        self.islabel=islabel
        idx = patient_name
        self.filenames = [os.path.join(data_dir, '%s_clean.npy' % idx) ]
        labels = []
        if islabel:
            l = np.load(data_dir + idx + '_label.npy')
            if np.all(l == 0):
                l = np.array([])
            labels.append(l)
        self.sample_bboxes = labels


    def __getitem__(self, idx=0, split=None):
        t = time.time()
        np.random.seed(int(str(t % 1)[2:7]))  # seed according to time

        print("process file", self.filenames[idx])
        imgs = np.load(self.filenames[idx])
        if self.islabel:
            bboxes = self.sample_bboxes[idx]
        else:
            bboxes = np.array([])
        nz, nh, nw = imgs.shape[1:]
        pz = int(np.ceil(float(nz) / self.stride)) * self.stride
        ph = int(np.ceil(float(nh) / self.stride)) * self.stride
        pw = int(np.ceil(float(nw) / self.stride)) * self.stride
        imgs = np.pad(imgs, [[0, 0], [0, pz - nz], [0, ph - nh], [0, pw - nw]], 'constant',
                          constant_values=self.pad_value)

        xx, yy, zz = np.meshgrid(np.linspace(-0.5, 0.5, imgs.shape[1] / self.stride),
                                     np.linspace(-0.5, 0.5, imgs.shape[2] / self.stride),
                                     np.linspace(-0.5, 0.5, imgs.shape[3] / self.stride), indexing='ij')
        coord = np.concatenate([xx[np.newaxis, ...], yy[np.newaxis, ...], zz[np.newaxis, :]], 0).astype('float32')
        imgs, nzhw = self.split_comber.split(imgs)

        coord2, nzhw2 = self.split_comber.split(coord,
                                                    side_len=int(self.split_comber.side_len / self.stride),
                                                    max_stride=int(self.split_comber.max_stride / self.stride),
                                                    margin=int(self.split_comber.margin / self.stride))
        assert np.all(nzhw == nzhw2)
        imgs = (imgs.astype(np.float32) - 128) / 128

        print("has get item", self.filenames[idx])
        print("imgs shape", imgs.shape)  # islabel: (60, 1, 144, 144, 144) notlabel: (180, 1, 144, 144, 144)
        print("coord shape", coord2.shape)  # islabel: (60, 3, 36, 36, 36) notlabel: (180, 3, 36, 36, 36)
        return torch.from_numpy(imgs), bboxes, torch.from_numpy(coord2), np.array(nzhw)

    def __len__(self):
        return 1
        # return len(self.sample_bboxes)



def printLabel(label):
    print("<<<<<< print label start")
    print("label shape: ", label.shape)
    print("label[...,0]=0 nums=",len(label[label[...,0]==0]))
    print("label[...,0]=1 nums=",len(label[label[...,0]==1]))
    print("label[...,0]=-1 nums=",len(label[label[...,0]==-1]))
    print("print label end >>>>>>>>")



def collate(batch):
    if torch.is_tensor(batch[0]):
        return [b.unsqueeze(0) for b in batch]
    elif isinstance(batch[0], np.ndarray):
        return batch
    elif isinstance(batch[0], int):
        return torch.LongTensor(batch)
    elif isinstance(batch[0], collections.Iterable):
        transposed = list(zip(*batch))
        return [collate(samples) for samples in transposed]
