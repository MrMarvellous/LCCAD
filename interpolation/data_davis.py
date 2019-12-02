# coding=utf-8
import cv2
import os
import random
import numpy as np
class DAVIS():
    def __init__(self, path,shuffle=True):
        self.path_pic = path
        pic_folder_list = os.listdir(self.path_pic)
        # print self.pic_folder_list
        folder_num = len(pic_folder_list)

        pic_list = []
        for folder in pic_folder_list:
            file_name = os.listdir(self.path_pic+folder)
            file_name = sorted(file_name)
            # print file_name
            pic_list.append(file_name)

        self.read_list = []
        for i in range(folder_num):
            pic_num = len(pic_list[i])
            for j in range(pic_num-3):
                pack = []
                pack.append(pic_folder_list[i])
                pack.append(pic_list[i][j])
                pack.append(pic_list[i][j+1])
                pack.append(pic_list[i][j+2])
                pack.append(pic_list[i][j+3])
                self.read_list.append(pack)
        self.simple_num = len(self.read_list)

        if shuffle:
            random.shuffle(self.read_list)

    def __getitem__(self, index):
        index = index%self.simple_num
        pack = self.read_list[index]
        # print pack
        frame_a = cv2.imread(self.path_pic+pack[0]+'/'+pack[1])
        frame_b = cv2.imread(self.path_pic+pack[0]+'/'+pack[2])
        frame_c = cv2.imread(self.path_pic+pack[0]+'/'+pack[3])
        frame_d = cv2.imread(self.path_pic + pack[0] + '/' + pack[4])
        return frame_a,frame_b,frame_c,frame_d

    def __len__(self):
        return self.simple_num
