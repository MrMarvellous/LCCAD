# coding:utf-8
import torch
from torch.nn import DataParallel
from torch.backends import cudnn
from torch.utils.data import DataLoader
from torch import optim
from torch.autograd import Variable

from config_global import config_global
from layers import acc
from data_detector import DataBowl3Detector, collate
from data_classifier import DataBowl3Classifier

from utils import *
from split_combine import SplitComb
from test_detect import test_detect
from net_classifier import CaseNet, config
from data_singlePbb import SinglePbbSet
from importlib import import_module
import pandas as pd

config_submit = {
    'datapath': '../lunaData',
    'preprocess_result_path': './new_data',
    'skip_preprocessing': False,
    'skip_detect': False,
    'n_worker_preprocessing': 4,
    'use_exsiting_preprocessing': True,
    'detector_model': 'net_detector.py',
    'detector_param': 'smxfolder/detector.ckpt',
    'classifier_model': 'net_classifier.py',
    'classifier_param': 'smxfolder/cls.ckpt',
    'outputfile': 'cls_single.csv',
    'n_gpu': 1
}


# datapath = config_submit['datapath']
# skip_prep = config_submit['skip_preprocessing']
# skip_detect = config_submit['skip_detect']


def tt_casenet(model, testset):
    data_loader = DataLoader(
        testset,
        batch_size=1,
        shuffle=False,
        num_workers=32,
        pin_memory=True)
    # model = model.cuda()
    model.eval()
    predlist = []

    for i, (x, coord) in enumerate(data_loader):
        # print('DEBUG X:',x)
        # print('DEBUG X SHAPE:', x.shape)
        # print('DEBUG coord:',coord)
        # print('DEBUG coord shape:', coord.shape)
        coord = Variable(coord).cuda()
        x = Variable(x).cuda()
        nodulePred, casePred, outPred = model(x, coord)
        # print('DEBUG nodulePred shape:', nodulePred.shape)
        # print('DEBUG casePred shape:', casePred.shape)
        # print('DEBUG outPred:', outPred)
        # print('DEBUG outPred shape:', outPred.shape)
        predlist.append(casePred.data.cpu().numpy())
        # print([i,data_loader.dataset.split[i,1],casePred.data.cpu().numpy()])
    predlist = np.concatenate(predlist)
    return predlist


def tt_casenet_singlePbb(model, testset):
    data_loader = DataLoader(
        testset,
        batch_size=1,
        shuffle=False,
        pin_memory=True)
    model.eval()
    predlist = []

    for i, (name, indexlist, croplist, coordlist) in enumerate(data_loader):
        # print('DEBUG PATIENT NAME:', name)
        pred_single_list = []
        indexlist = indexlist.numpy().astype('int')[0]
        # print('indexlist: ',indexlist)
        # print('croplist shape:', croplist.shape)
        # print('coordlist shape:', coordlist.shape)
        # id 和检测出来的结果一一对应
        for id in indexlist:
            x = Variable(croplist[:, id:id + 1, :, :, :, :]).cuda()
            coord = Variable(coordlist[:, id:id + 1, :, :, :, :]).cuda()
            nodulePred, casePred, outPred = model(x, coord)
            pred_single_list.append((id, casePred.data.cpu().numpy()[0]))

        predlist.append((name, pred_single_list))

    return predlist


def class_data_web(patient_name, has_info=True, write_csv=False):
    casenet = CaseNet(topk=5)
    config2 = config
    checkpoint = torch.load(config_global['classifier_param'])
    casenet.load_state_dict(checkpoint['state_dict'])
    torch.cuda.set_device(0)
    casenet = casenet.cuda().eval()
    cudnn.benchmark = True
    casenet = DataParallel(casenet)

    testsplit = [patient_name]

    prep_result_path = config_global['preprocess_result_path']
    bbox_result_path = config_global['detect_result_path']
    if not has_info:
        bbox_result_path = config_global['detect_result_path_no_info']
        prep_result_path = config_global['preprocess_result_path_no_info']
    config2['bboxpath'] = bbox_result_path
    config2['datadir'] = prep_result_path

    dataset = SinglePbbSet(testsplit, config2, phase='test')
    predlist = tt_casenet_singlePbb(casenet, dataset)

    name_df = []
    pbb_df = []
    prob_df = []
    for index, (name, ele) in enumerate(predlist):
        print('index name ele:', index, name, ele)
        for (pbb_id, prob) in ele:
            name_df.append(str(name[0]))
            pbb_df.append(pbb_id)
            prob_df.append(prob)
    print('DEBUG START OVERALL COMPUTE')
    dataset_overall = DataBowl3Classifier(testsplit, config2, phase='test')
    predlist_overall = tt_casenet(casenet, dataset_overall)
    print('DEBUG OVERALL PREDLIST:', predlist_overall)
    if write_csv:
        filename = 'cls_single.csv'
        df = pd.DataFrame({'patient_id': name_df, 'pbb_id': pbb_df, 'malignant_probability': prob_df})
        df.to_csv(filename, index=False)


    return predlist_overall, len(prob_df), prob_df


def class_data_main():
    prep_result_path = config_submit['preprocess_result_path']
    bbox_result_path = './new_bbox_result'

    casenet = CaseNet(topk=5)
    config2 = config
    checkpoint = torch.load(config_submit['classifier_param'])
    casenet.load_state_dict(checkpoint['state_dict'])

    torch.cuda.set_device(0)
    casenet = casenet.cuda()
    cudnn.benchmark = True
    casenet = DataParallel(casenet)

    filename = config_submit['outputfile']
    testsplit = [f.split('_clean')[0] for f in os.listdir(prep_result_path) if '_clean' in f]

    config2['bboxpath'] = bbox_result_path
    config2['datadir'] = prep_result_path

    # print('DEBUG START................')
    # dataset = DataBowl3Classifier(testsplit, config2, phase='test')
    dataset = SinglePbbSet(testsplit, config2, phase='test')
    predlist = tt_casenet_singlePbb(casenet, dataset)
    # print('DEBUG predlist shape:', len(predlist))
    name_df = []
    pbb_df = []
    prob_df = []
    for index, (name, ele) in enumerate(predlist):
        print('index name ele:', index, name, ele)
        for (pbb_id, prob) in ele:
            name_df.append(str(name[0]))
            pbb_df.append(pbb_id)
            prob_df.append(prob)
    print('DEBUG START OVERALL COMPUTE')
    dataset_overall = DataBowl3Classifier(testsplit, config2, phase='test')
    predlist_overall = tt_casenet(casenet, dataset_overall)
    print('DEBUG OVERALL PREDLIST:', predlist_overall)

    # print('DEBUG MID..................')
    df = pd.DataFrame({'patient_id': name_df, 'pbb_id': pbb_df, 'malignant_probability': prob_df})
    df.to_csv(filename, index=False)

    # print('DEGBU END..................')


if __name__ == '__main__':
    class_data_main()
