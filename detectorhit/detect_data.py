from torch.backends import cudnn
from torch.utils.data import DataLoader

from config_global import config_global
from full_prep import candidates_list
import net_detector as nodmodel
from data_detector import DataBowl3Detector, collate
from split_combine import SplitComb
from test_detect import test_detect
from utils import *


def detect_new_data(filename, has_info=True):

    config1, nod_net, loss, get_pbb = nodmodel.get_model()
    checkpoint = torch.load(config_global['detector_param'])
    nod_net.load_state_dict(checkpoint['state_dict'])
    nod_net = nod_net.cuda()
    cudnn.benchmark = True

    prep_result_path = config_global['preprocess_result_path']
    bbox_result_path = config_global['detect_result_path']

    if not has_info:
        prep_result_path = config_global['preprocess_result_path_no_info']
        bbox_result_path = config_global['detect_result_path_no_info']
    if not os.path.exists(bbox_result_path):
        os.mkdir(bbox_result_path)
    testsplit = [filename]
    print(testsplit)
    margin = 32
    sidelen = 80
    config1['datadir'] = prep_result_path
    split_comber = SplitComb(sidelen, config1['max_stride'], config1['stride'], margin, pad_value=config1['pad_value'])

    dataset = DataBowl3Detector(testsplit, config1, phase='test', split_comber=split_comber)
    test_loader = DataLoader(dataset, batch_size=1,
                             shuffle=False, num_workers=0, pin_memory=False, collate_fn=collate)

    test_detect(test_loader, nod_net, get_pbb, bbox_result_path, config1, n_gpu=config_global['n_gpu'])
    # TODO: NEED EXIT()?


def detect_data_main():
    all_data_path = '/home/guanzhilin/app/hit_lung_data'
    patient_list = candidates_list(all_data_path)
    for patient in patient_list:
        detect_new_data(patient['full_name'])


if __name__ == '__main__':
    detect_data_main()
