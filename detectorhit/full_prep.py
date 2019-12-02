import os
import warnings
from functools import partial
from multiprocessing import Pool
from os import walk

import SimpleITK as sitk
import numpy as np
from scipy.ndimage.interpolation import zoom
from scipy.ndimage.morphology import binary_dilation, generate_binary_structure
from skimage.morphology import convex_hull_image

from preprocess import step1_dicom
from config_global import config_global


def candidates_list(path):
    patient_list = []
    for root, subdirs, files in walk(path):
        if (not subdirs):
            patient = {}
            patient['path'] = root
            dirs = root.split('/')
            patient['name'] = str(dirs[-3]).replace('_', ' ')
            patient['date'] = str(dirs[-2]).replace('_', ' ')
            patient['window'] = str(dirs[-1]).replace('_', ' ')
            patient['full_name'] = str(dirs[-3]) + "_" + str(dirs[-2]) + "_" + str(dirs[-1])
            patient_list.append(patient)

    return patient_list



def process_mask(mask):
    convex_mask = np.copy(mask)
    for i_layer in range(convex_mask.shape[0]):
        mask1 = np.ascontiguousarray(mask[i_layer])
        if np.sum(mask1) > 0:
            mask2 = convex_hull_image(mask1)
            if np.sum(mask2) > 2 * np.sum(mask1):
                mask2 = mask1
        else:
            mask2 = mask1
        convex_mask[i_layer] = mask2
    struct = generate_binary_structure(3, 1)
    dilatedMask = binary_dilation(convex_mask, structure=struct, iterations=10)
    return dilatedMask


id = 1


def lumTrans(img):
    lungwin = np.array([-1200., 600.])
    newimg = (img - lungwin[0]) / (lungwin[1] - lungwin[0])
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    newimg = (newimg * 255).astype('uint8')
    return newimg


def resample(imgs, spacing, new_spacing, order=2):
    if len(imgs.shape) == 3:
        new_shape = np.round(imgs.shape * spacing / new_spacing)
        true_spacing = spacing * imgs.shape / new_shape
        resize_factor = new_shape / imgs.shape
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            imgs = zoom(imgs, resize_factor, mode='nearest', order=order)
        return imgs, true_spacing
    elif len(imgs.shape) == 4:
        n = imgs.shape[-1]
        newimg = []
        for i in range(n):
            slice = imgs[:, :, :, i]
            newslice, true_spacing = resample(slice, spacing, new_spacing)
            newimg.append(newslice)
        newimg = np.transpose(np.array(newimg), [1, 2, 3, 0])
        return newimg, true_spacing
    else:
        raise ValueError('wrong shape')


def savenpy(id, filelist, patient_name, prep_folder, data_path, use_existing=True):
    resolution = np.array([1, 1, 1])
    # name = filelist[id]

    try:
        im, m1, m2, spacing = step1_dicom(data_path)

        Mask = m1 + m2
        newshape = np.round(np.array(Mask.shape) * spacing / resolution)
        xx, yy, zz = np.where(Mask)
        box = np.array([[np.min(xx), np.max(xx)], [np.min(yy),
                                                   np.max(yy)], [np.min(zz), np.max(zz)]])
        box = box * np.expand_dims(spacing, 1) / np.expand_dims(resolution, 1)
        box = np.floor(box).astype('int')
        margin = 5
        extendbox = np.vstack(
            [np.max([[0, 0, 0], box[:, 0] - margin], 0), np.min([newshape, box[:, 1] + 2 * margin], axis=0).T]).T
        extendbox = extendbox.astype('int')

        convex_mask = m1
        dm1 = process_mask(m1)
        dm2 = process_mask(m2)
        dilatedMask = dm1 + dm2
        Mask = m1 + m2
        extramask = dilatedMask ^ Mask
        bone_thresh = 210
        pad_value = 170

        im[np.isnan(im)] = -2000
        sliceim = lumTrans(im)
        sliceim = sliceim * dilatedMask + pad_value * \
                  (1 - dilatedMask).astype('uint8')
        bones = sliceim * extramask > bone_thresh
        sliceim[bones] = pad_value
        x, y, z = sliceim.shape
        np.save(os.path.join(prep_folder, patient_name + '_clean'),
                sliceim.reshape(1, x, y, z))
        np.save(os.path.join(prep_folder, patient_name + '_label'),
                np.array([[0, 0, 0, 0]]))
    except Exception as e:
        print('bug in ' + data_path + ', last error is:'+str(e))

        reader = sitk.ImageSeriesReader()
        seriesID = reader.GetGDCMSeriesIDs(data_path)
        dicom_names = reader.GetGDCMSeriesFileNames(data_path, seriesID[0])
        print(seriesID)
        print(dicom_names)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        image_array = sitk.GetArrayFromImage(image)  # z, y, x
        origin = image.GetOrigin()  # x, y, z
        spacing = image.GetSpacing()  # x, y, z

        # itk_img = sitk.ReadImage(data_path)
        # im = sitk.GetArrayFromImage(itk_img)
        # tutorialLungSeg.lungSeg(im, prep_folder, name.split('.')[0])

        # raise
    print(patient_name + ' done')


def full_prep(data_path, patient_name, prep_folder, n_worker=None, use_existing=True):
    warnings.filterwarnings("ignore")
    if not os.path.exists(prep_folder):
        os.mkdir(prep_folder)

    print('starting preprocessing')
    pool = Pool(n_worker)
    # filelist = [f for f in os.listdir(data_path) if '.mhd' in f]
    partial_savenpy = partial(savenpy, filelist=[], prep_folder=prep_folder,
                              data_path=data_path, use_existing=use_existing, patient_name=patient_name)

    N = 1
    _ = pool.map(partial_savenpy, range(N))
    pool.close()
    pool.join()
    print('end preprocessing')
    return 0


def full_prep_main():
    all_data_path = '/home/guanzhilin/app/hit_lung_data'
    patient_list = candidates_list(all_data_path)

    prep_folder = './new_data'
    n_worker = 1
    use_existing = False
    for patient in patient_list:
        full_prep(patient['path'], patient['full_name'],
                  prep_folder, n_worker, use_existing)
    print('preprocess ok')


def full_prep_web(patient, has_info=False):
    #这里处理网页上接收到的CT文件

    prep_folder = os.path.join(config_global['ROOT_PATH'],'new_data')
    if not has_info:
        prep_folder=os.path.join(config_global['ROOT_PATH'],'new_data_no_info')
    if not os.path.exists(prep_folder):
        os.mkdir(prep_folder)
    n_worker = 1
    use_existing = False

    full_prep(patient['path'], patient['full_name'],prep_folder, n_worker, use_existing)
    print(patient['full_name']+' preprocess complete.')


if __name__ == '__main__':
    full_prep_main()  # 测试本地文件
