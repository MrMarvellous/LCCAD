# coding=utf-8
import os
import torch
import torch.nn as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader


from config_tracer import config_tracer
from resnet import ResNet18
from model_cover import COVER_NET
from mydataset import MyDataset
import util
import numpy as np
import cv2
import shutil
import torch.nn.functional as F
import math
import random


def train():
    class_net = ResNet18()
    class_net.cuda().train()

    cover_net = COVER_NET()
    cover_net.cuda().train()

    ckpt_cover_path = "./ckpt_cover/"
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    ckpt_class_path = "./ckpt_class/"
    data_path, step = util.load_weight(ckpt_class_path)
    if step:
        class_net.load_state_dict(torch.load(data_path))

    batch = 64
    lr = 7e-5
    weight_decay = 0

    optimizer = torch.optim.Adam(util.models_parameters([cover_net, class_net]), lr, weight_decay=weight_decay)

    ckpt_optimizer_path = "./optimizer_ckpt/"
    # data_path, step_optimizer = util.load_weight(ckpt_optimizer_path)
    # if step_optimizer != step:
    #     print 'optimizer step error'
    #     return
    # else:
    #     if step_optimizer:
    #         optimizer.load_state_dict(torch.load(data_path))

    data_path = '/media/gdh-95/data/CT/CT_2d_note_slice2/train/'
    transform = transforms.Compose([transforms.RandomHorizontalFlip(),
                                    transforms.RandomVerticalFlip(),
                                    transforms.ToTensor(), ])
    train_set = datasets.ImageFolder(data_path, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch, shuffle=True, num_workers=2)

    dataiter = iter(train_loader)
    lenth_iter = len(dataiter)
    read_num = 0

    height = 64
    width = 64
    torchHorizontal = torch.linspace(-width / 2, width / 2, width).cuda().view(1, 1, 1, width).expand(1, 1, height,
                                                                                                      width)
    torchVertical = torch.linspace(-height / 2, -height / 2, height).cuda().view(1, 1, height, 1).expand(1, 1, height,
                                                                                                         width)
    grid = torchHorizontal * torchHorizontal + torchVertical * torchVertical
    grid_max = torch.max(grid)
    grid = grid / grid_max

    step0 = 100000001

    start = step
    for step in range(start + 1, step0):
        print("step0-", step)
        images, labels = next(dataiter)
        read_num += 1
        if read_num == lenth_iter - 1:
            dataiter = iter(train_loader)
            read_num = 0
        images = images.cuda()
        labels = labels.float().cuda()

        batch_one, _, _, _ = images.size()
        grid_one = grid.expand(batch_one, 1, height, width)

        cover_mask = cover_net(images)

        class_out = class_net(images, cover_mask)
        class_out = torch.mean(class_out, dim=1)

        loss_class = (class_out - labels)
        loss_class = (loss_class * loss_class).mean()
        loss_cover = torch.mean(cover_mask)
        loss = loss_class + loss_cover * 0.5

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        loss_class_c = loss_class.cpu().data.numpy()
        loss_cover_c = loss_cover.cpu().data.numpy()
        print("            loss_class:", loss_class_c, "   loss_cover:", loss_cover_c)

        if step % 5000 == 0:
            print("save weight at step:%d" % (step))
            util.save_weight(class_net, step, ckpt_class_path)
            print("save weight at step:%d" % (step))
            util.save_weight(cover_net, step, ckpt_cover_path)
            print("save optimizer weight at step:%d" % (step))
            util.save_weight(optimizer, step, ckpt_optimizer_path)


def view():
    class_net = ResNet18()
    class_net.cuda().eval()

    cover_net = COVER_NET()
    cover_net.cuda().eval()

    ckpt_cover_path = "./ckpt_cover/"
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    ckpt_class_path = "./ckpt_class/"
    data_path, step = util.load_weight(ckpt_class_path)
    if step:
        class_net.load_state_dict(torch.load(data_path))

    batch = 64
    criterion = nn.CrossEntropyLoss()

    # data_path = '/media/gdh-95/data/CT_2d_note_slice/train/'
    data_path = '/home/guanzhilin/app/new_result_for_feat/'
    transform = transforms.Compose([transforms.ToTensor()])
    train_set = datasets.ImageFolder(data_path, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch, shuffle=True, num_workers=2)

    dataiter = iter(train_loader)
    lenth = len(train_set)
    print('img_num', lenth)
    out_path = './cover_2d_out/'

    if os.path.exists(out_path):
        shutil.rmtree(out_path)

    save_num = 0
    error_num = 0
    break_flag = 0
    area_add = 0
    batch_num = 0
    for images0, labels in dataiter:
        print('DEBUG images0 shape: ',images0.shape)
        # print('labels: ',labels)
        if break_flag:
            break
        batch_num += 1
        images0 = images0.cuda()
        labels0 = labels.cpu().data.numpy()

        images = images0 * 1
        labels = labels.float().cuda()
        cover_mask = cover_net(images)

        class_out = class_net(images, cover_mask)
        class_out = torch.mean(class_out, dim=1)
        loss_class = (class_out - labels)
        loss_class = (loss_class * loss_class).mean()
        loss_cover = torch.mean(cover_mask)

        area_add += loss_cover.cpu().data.numpy()

        error_b = (class_out - labels).abs().sum().cpu().data.numpy()
        error_num += error_b
        loss_class_c = loss_class.cpu().data.numpy()
        loss_cover_c = loss_cover.cpu().data.numpy()

        print("loss_class:", loss_class_c, "  loss_cover:", loss_cover_c)
        batch_max = images.size(0)
        for b in range(batch_max):
            image_one = images0[b:b + 1, :, :, :]
            cover_one = cover_mask[b:b + 1, :, :, :]
            overlay_one = image_one * 1
            overlay_one[:, 1, :, :] = overlay_one[:, 1, :, :] * (1 - cover_one)
            image_one = util.torch2numpy(image_one * 255)
            cover_one = np.squeeze(util.torch2numpy(cover_one * 255))
            overlay_one = util.torch2numpy(overlay_one * 255)
            # print labels0[b]
            # print str(labels0[b])
            save_path = out_path + str(labels0[b]) + '/'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            cv2.imwrite(save_path + str(save_num) + '_a.jpg', image_one)
            cv2.imwrite(save_path + str(save_num) + '_b.jpg', overlay_one)
            cv2.imwrite(save_path + str(save_num) + '_c.jpg', cover_one)
            save_num += 1

    print("error:", float(error_num) / float(save_num))
    print("area:", area_add / float(batch_num))


def view_new(patientname,savename):
    class_net = ResNet18()
    class_net.cuda().eval()

    cover_net = COVER_NET()
    cover_net.cuda().eval()

    ckpt_cover_path = config_tracer['cover_model']
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    ckpt_class_path = config_tracer['class_model']
    data_path, step = util.load_weight(ckpt_class_path)
    if step:
        class_net.load_state_dict(torch.load(data_path))

    batch = 64
    criterion = nn.CrossEntropyLoss()

    # data_path = '/media/gdh-95/data/CT_2d_note_slice/train/'
    data_path = os.path.join(config_tracer['feat_save_path'], patientname)
    transform = transforms.Compose([transforms.ToTensor()])
    # train_set = datasets.ImageFolder(data_path, transform=transform)
    test_set = MyDataset(data_path, transform)
    test_loader = torch.utils.data.DataLoader(test_set, batch_size=1, shuffle=False)

    lenth = len(test_set)
    print('img_num', lenth)
    out_path = os.path.join(config_tracer['output_path'], patientname)

    if os.path.exists(out_path):
        flush_dir(out_path)
    else:
        os.mkdir(out_path)

    save_num = 0

    for i,(filename, image_tensor, label) in enumerate(test_loader):
        image_tensor = image_tensor.cuda()
        # image_tensor = torch.unsqueeze(image_tensor, 0)
        # label = label.cpu().data.numpy()
        image = image_tensor * 1
        # label = label.float().cuda()
        cover_mask = cover_net(image)

        overlay = image * 1
        overlay[:,1, :, :] = overlay[:,1, :, :] * (1 - cover_mask)
        image_one = util.torch2numpy(image * 255)
        cover_one = np.squeeze(util.torch2numpy(cover_mask * 255))
        overlay_one = util.torch2numpy(overlay * 255)
        # print labels0[b]
        if not savename:
            savename=patientname
        cv2.imencode('.png', image_one)[1].tofile(
            os.path.join(out_path, str(i) + '_origin.jpg'))
        cv2.imencode('.png', overlay_one)[1].tofile(
            os.path.join(out_path, str(i) + '_overlay.jpg'))
        cv2.imencode('.png', cover_one)[1].tofile(
            os.path.join(out_path, str(i) + '_cover.jpg'))
        # cv2.imwrite(os.path.join(out_path, savename + '_origin.jpg'), image_one)
        # cv2.imwrite(os.path.join(out_path, savename + '_overlay.jpg'), overlay_one)
        # cv2.imwrite(os.path.join(out_path, savename + '_cover.jpg'), cover_one)
        save_num += 1

    print('save num', save_num)
    print('view_new OK')


def view_single(filename, savename):
    class_net = ResNet18()
    class_net.cuda().eval()

    cover_net = COVER_NET()
    cover_net.cuda().eval()

    ckpt_cover_path = config_tracer['cover_model']
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    ckpt_class_path = config_tracer['class_model']
    data_path, step = util.load_weight(ckpt_class_path)
    if step:
        class_net.load_state_dict(torch.load(data_path))

    input_path = config_tracer['input_path']
    out_path = config_tracer['output_path']
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    img_path = os.path.join(input_path, filename)
    transform = transforms.Compose([transforms.ToTensor()])
    img_tensor = transform(default_loader(img_path))

    print('DEBUG: SHAPE ', img_tensor.shape)

    image_tensor = img_tensor.cuda()
    # image_tensor = torch.unsqueeze(image_tensor, 0)

    image = image_tensor * 1
    cover_mask = cover_net(image)

    overlay = image * 1
    overlay[:, 1, :, :] = overlay[:, 1, :, :] * (1 - cover_mask)

    image_one = util.torch2numpy(image * 255)
    cover_one = np.squeeze(util.torch2numpy(cover_mask * 255))
    overlay_one = util.torch2numpy(overlay * 255)

    if not savename:
        savename = 'unkown'
    cv2.imwrite(os.path.join(out_path, savename+'_origin.jpg', image_one))
    cv2.imwrite(os.path.join(out_path, savename+'_overlay.jpg', overlay_one))
    cv2.imwrite(os.path.join(out_path, savename+'_cover.jpg', cover_one))

    print('view single ok')


def visual_back_prop():
    FEAT_KEEP = 8  # Feature Maps to show
    FEAT_SIZE = 64  # Size of feature maps to show

    def save_feature_maps(self, input, output):
        # The hook function that saves feature maps while forward propagate
        map = output.data
        maps.append(map)

    def add_hook(net, func):
        for index, m in enumerate(net.layer1):
            type_name = str(type(m)).replace("<'", '').replace("'>", '').split('.')[-1]
            name = 'features' + '-' + str(index) + '-' + type_name
            hook = m.register_forward_hook(func)
            layers.append((name, m))
            hooks.append(hook)
        for index, m in enumerate(net.layer2):
            type_name = str(type(m)).replace("<'", '').replace("'>", '').split('.')[-1]
            name = 'features' + '-' + str(index) + '-' + type_name
            hook = m.register_forward_hook(func)
            layers.append((name, m))
            hooks.append(hook)
        for index, m in enumerate(net.layer3):
            type_name = str(type(m)).replace("<'", '').replace("'>", '').split('.')[-1]
            name = 'features' + '-' + str(index) + '-' + type_name
            hook = m.register_forward_hook(func)
            layers.append((name, m))
            hooks.append(hook)
        for index, m in enumerate(net.layer4):
            type_name = str(type(m)).replace("<'", '').replace("'>", '').split('.')[-1]
            name = 'features' + '-' + str(index) + '-' + type_name
            hook = m.register_forward_hook(func)
            layers.append((name, m))
            hooks.append(hook)

        return net

    def normalize_gamma(image, gamma=1.0):
        # normalize data for display
        if image.max() != image.min():
            image = (image - image.min()) / (image.max() - image.min())
        else:
            image = (image - image.min()) / 1
        invGamma = 1.0 / gamma
        image = (image ** invGamma) * 255
        return image.astype("uint8")

    def plotFeatMaps(layers, maps):

        '''
        :param layers: the saved layers
        :param maps: the saved maps
        :return: top feat. maps of relu layers
        '''

        num_layers = len(maps)
        feat_collection = []
        # Show top FEAT_KEEP feature maps (after ReLU) starting from bottom layers

        for n in range(num_layers):
            cur_layer = layers[n][1]
            if type(cur_layer):
                ##########################
                # Get and set attributes #
                ##########################
                relu = maps[n]

                ###########################################
                # Sort Feat Maps based on energy of F.M. #
                ###########################################
                feat_energy = []
                # Get energy of each channel
                for channel_n in range(relu.shape[1]):
                    feat_energy.append(np.sum(relu[0][channel_n].cpu().numpy()))
                feat_energy = np.array(feat_energy)
                # Sort energy
                feat_rank = np.argsort(feat_energy)[::-1]

                # Empty background
                # Empty background
                back_len = int(math.ceil(math.sqrt(FEAT_SIZE * FEAT_SIZE * FEAT_KEEP * 2)))
                feat = np.zeros((back_len, back_len))
                col = 0
                row = 0
                for feat_n in range(FEAT_KEEP):
                    if col * FEAT_SIZE + FEAT_SIZE < back_len:
                        feat[row * FEAT_SIZE:row * FEAT_SIZE + FEAT_SIZE, col * FEAT_SIZE:col * FEAT_SIZE + FEAT_SIZE] = \
                            cv2.resize(normalize_gamma(relu[0][feat_rank[feat_n]].cpu().numpy(), 0.1),
                                       (FEAT_SIZE, FEAT_SIZE))
                        col = col + 1
                    else:
                        row = row + 1
                        col = 0
                        feat[row * FEAT_SIZE:row * FEAT_SIZE + FEAT_SIZE, col * FEAT_SIZE:col * FEAT_SIZE + FEAT_SIZE] = \
                            cv2.resize(normalize_gamma(relu[0][feat_rank[feat_n]].cpu().numpy(), 0.1),
                                       (FEAT_SIZE, FEAT_SIZE))
                        col = col + 1

                feat_collection.append(feat)

        return feat_collection

    def visualbackprop(layers, maps):

        '''
        :param layers: the saved layers
        :param maps: the saved maps
        :return: return the final mask
        '''

        num_layers = len(maps)
        avgs = []
        mask = None
        ups = []

        for n in range(num_layers - 1, -1, -1):
            cur_layer = layers[n][1]
            if True:
                # if type(cur_layer) in [torch.nn.MaxPool2d]:
                #     print type(cur_layer)
                # Average filters
                fea_one = maps[n]
                # fea_one = F.instance_norm(fea_one)
                # fea_one = fea_one-torch.min(fea_one)
                avg = fea_one.mean(dim=1)
                avg = avg.unsqueeze(0)
                avgs.append(avg)

                if mask is not None:
                    h, w = avg.size()[2:]

                    mask = F.interpolate(mask, [h, w]).data
                    mask = mask * avg
                    # mask = torch.pow(mask,0.5)
                else:
                    mask = avg

                # upsampling : see http://pytorch.org/docs/nn.html#convtranspose2d
                weight = torch.ones(1, 1, 3, 3).cuda()
                up = F.conv_transpose2d(mask, weight, stride=1, padding=1)
                mask = up.data
                ups.append(mask)

        return ups

    def show_VBP(label, image):
        """Take an array of shape (n, height, width) or (n, height, width, 3)
           and visualize each (height, width) thing in a grid of size approx. sqrt(n) by sqrt(n)"""
        image = image.cpu().numpy()
        # normalize data for display
        if image.max() != image.min():
            data = (image - image.min()) / (image.max() - image.min())
        else:
            data = (image - image.min()) / 1
        data = data[0, 0, :, :]
        data = cv2.resize(data, new_size)
        data = (data * 255).astype("uint8")
        cv2.imwrite(label, data)

    def save_VBP(label, image):
        image = image.cpu().numpy()
        # normalize data for display
        if image.max() != image.min():
            data = (image - image.min()) / (image.max() - image.min())
        else:
            data = (image - image.min()) / 1
        data = data[0, 0, :, :]
        data = cv2.resize(data, new_size)
        data = (data * 255).astype("uint8")
        cv2.imwrite(label, data)

    def overlay(image, mask):
        # normalize data for display
        mask = (mask - mask.min()) / (mask.max() - mask.min())
        mask = mask[0, 0, :, :]
        mask = cv2.resize(mask, new_size)
        mask = (mask * 255).astype("uint8")
        # pdb.set_trace()
        # assert image.shape == mask.shape, "image %r and mask %r must be of same shape" % (image.shape, mask.shape)
        # if image[:,:,2] + mask > 255:
        # image[:,:,2] = image[:,:,2] + mask
        # else:
        image[:, :, 2] = cv2.add(image[:, :, 2], mask)

        return image

    torch.set_grad_enabled(False)

    class_net = ResNet18()
    class_net.cuda().train()

    cover_net = COVER_NET()
    cover_net.cuda().train()

    ckpt_cover_path = "./ckpt_cover/"
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    ckpt_class_path = "./ckpt_class/"
    data_path, step = util.load_weight(ckpt_class_path)
    if step:
        class_net.load_state_dict(torch.load(data_path))

    layers = []
    hooks = []
    add_hook(class_net, save_feature_maps)

    img_path = '/media/gdh-95/data/CT/CT_2d_note_slice/train/'
    folder_list = sorted(os.listdir(img_path))
    # print folder_list

    out_path = '../cover_vbp_train/'

    if os.path.exists(out_path):
        shutil.rmtree(out_path)

    for folder in folder_list:
        folder_path = img_path + folder + '/'
        img_list = sorted(os.listdir(folder_path))

        for img_name in img_list:
            print(img_name)
            img_one_path = folder_path + img_name

            maps = []
            images0 = cv2.imread(img_one_path)

            save_one = img_name[:img_name.find('.jpg')]

            FEAT_MAPS_DIR = out_path + folder + '/' + save_one + '/feat_maps'  # dir. to save feat maps
            # VBP_DIR = real_path+'/'+real_img_path+'/VBP_results'  # dir. to save VBP results
            OVERLAY_DIR = out_path + folder + '/' + save_one + '/'  # dir. to save overlay results

            if not os.path.exists(FEAT_MAPS_DIR):
                os.makedirs(FEAT_MAPS_DIR)

            # if not os.path.exists(VBP_DIR):
            #     os.makedirs(VBP_DIR)

            if not os.path.exists(OVERLAY_DIR):
                os.makedirs(OVERLAY_DIR)
            try:
                h0 = images0.shape[0]
                w0 = images0.shape[1]
            except:
                continue
            input_w = 64
            if h0 > w0:
                w1 = input_w
                h1 = h0 * input_w / w0
            else:
                h1 = input_w
                w1 = w0 * input_w / h0
            new_size = (w1, h1)

            images0 = cv2.resize(images0, new_size)
            cv2.imwrite(OVERLAY_DIR + '/zimg0.png', images0)

            img = util.numpy2torch(images0 * 1)
            img = img / 255.
            cover_mask = cover_net(img)
            class_out = class_net(img, cover_mask)

            cover_mask = util.torch2numpy(cover_mask)
            overlay1 = images0 * 1
            cover_mask = np.squeeze(cover_mask)
            # overlay1[:,:,2] = overlay1[:, :, 2]+ cover_mask*255
            # overlay1 = np.minimum(overlay1, 255)
            cover_mask = (cover_mask * 255).astype("uint8")
            overlay1[:, :, 2] = cv2.add(overlay1[:, :, 2], cover_mask)
            cover_one = cover_mask

            cv2.imwrite(OVERLAY_DIR + 'overlay1.jpg', overlay1)
            cv2.imwrite(OVERLAY_DIR + 'cover_mask.jpg', cover_one)

            feat_collection = plotFeatMaps(layers, maps)

            for i in range(len(feat_collection)):
                cv2.imwrite(FEAT_MAPS_DIR + '/feat_' + str(i) + '.jpg', feat_collection[i] * 255)
            masks = visualbackprop(layers, maps)
            mask_num = len(masks)

            for i in range(mask_num):
                # save_VBP(VBP_DIR + '/out_' + str(i) + '.png', masks[i])
                show_VBP(OVERLAY_DIR + '/vbp_' + str(i) + '.png', masks[i])

            overlay_img = overlay(images0, masks[mask_num - 1].cpu().numpy())
            cv2.imwrite(OVERLAY_DIR + 'overlay' + '.png', overlay_img)


def erasure_new_data():
    torch.set_grad_enabled(False)
    cover_net = COVER_NET()
    cover_net.cuda().train()

    random.seed(27)

    ckpt_cover_path = "./ckpt_cover/"
    data_path, step = util.load_weight(ckpt_cover_path)
    if step:
        cover_net.load_state_dict(torch.load(data_path))

    img_path = '/media/gdh-95/data/CT/CT_2d_note_slice2/train/'

    folder_list = sorted(os.listdir(img_path))
    # print folder_list
    out_path = '/media/gdh-95/data/CT/CT_2d_note_slice3/'
    train_path = out_path + 'train/'
    test_path = out_path + 'test/'

    test_rate = 0.1

    test_area = 0
    test_num = 0

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    for folder in folder_list:
        folder_path = img_path + folder + '/'
        img_list = sorted(os.listdir(folder_path))
        out_folder_train = train_path + folder + '/'
        out_folder_test = test_path + folder + '/'

        if not os.path.exists(out_folder_train):
            os.makedirs(out_folder_train)
        if not os.path.exists(out_folder_test):
            os.makedirs(out_folder_test)

        for img_name in img_list:
            print(img_name)
            img_one_path = folder_path + img_name
            images0 = cv2.imread(img_one_path)

            img = util.numpy2torch(images0 * 1)
            img = img / 255.
            cover_mask = cover_net(img)
            cover_mask = (cover_mask + 0.9).floor()
            new_img = (cover_mask * img) * 255
            new_img = util.torch2numpy(new_img)
            if random.uniform(0, 1) > test_rate:
                cover_mask_mean = cover_mask.mean().cpu().data.numpy()
                print('area:', cover_mask_mean)
                test_area += cover_mask_mean
                test_num += 1
                cv2.imwrite(out_folder_train + img_name, new_img)
            else:
                print("!!！!！!！!！!！!！")
                cv2.imwrite(out_folder_test + img_name, new_img)

    print('avg_mean:', test_area / test_num)


def new_data():
    random.seed(27)

    img_path = '/media/gdh-95/data/CT/CT_2d_note_slice2/train/'

    folder_list = sorted(os.listdir(img_path))
    # print folder_list
    out_path = '/media/gdh-95/data/CT/CT_2d_note_slice7/'
    train_path = out_path + 'train/'
    test_path = out_path + 'test/'

    test_rate = 0.1

    test_area = 0
    test_num = 0

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    for folder in folder_list:
        folder_path = img_path + folder + '/'
        img_list = sorted(os.listdir(folder_path))
        out_folder_train = train_path + folder + '/'
        out_folder_test = test_path + folder + '/'

        if not os.path.exists(out_folder_train):
            os.makedirs(out_folder_train)
        if not os.path.exists(out_folder_test):
            os.makedirs(out_folder_test)

        for img_name in img_list:
            print(img_name)
            img_one_path = folder_path + img_name
            images0 = cv2.imread(img_one_path)

            if random.uniform(0, 1) > test_rate:

                cv2.imwrite(out_folder_train + img_name, images0)
            else:
                print("!!！!！!！!！!！!！")
                cv2.imwrite(out_folder_test + img_name, images0)


def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)
    print("flush", dirpath, "complete")