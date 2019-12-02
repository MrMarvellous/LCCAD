import os

import SimpleITK as sitk
import numpy as np
import pandas
import scipy
from scipy.ndimage.interpolation import zoom
from scipy.ndimage.morphology import binary_dilation, generate_binary_structure
from skimage import measure
from skimage.morphology import convex_hull_image

local_path="D:/workspace/python/LCCAD/detector/"

def resample(imgs, spacing, new_spacing, order=2):
    if len(imgs.shape) == 3:
        new_shape = np.round(imgs.shape * spacing / new_spacing)
        true_spacing = spacing * imgs.shape / new_shape
        resize_factor = new_shape / imgs.shape
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


def worldToVoxelCoord(worldCoord, origin, spacing):
    stretchedVoxelCoord = np.absolute(worldCoord - origin)
    voxelCoord = stretchedVoxelCoord / spacing
    return voxelCoord


def load_itk_image(filename):
    with open(filename) as f:
        contents = f.readlines()
        line = [k for k in contents if k.startswith('TransformMatrix')][0]
        transformM = np.array(line.split(' = ')[1].split(' ')).astype('float')
        transformM = np.round(transformM)
        if np.any(transformM != np.array([1, 0, 0, 0, 1, 0, 0, 0, 1])):
            isflip = True
        else:
            isflip = False

    itkimage = sitk.ReadImage(filename)
    numpyImage = sitk.GetArrayFromImage(itkimage)

    numpyOrigin = np.array(list(reversed(itkimage.GetOrigin())))
    numpySpacing = np.array(list(reversed(itkimage.GetSpacing())))

    return numpyImage, numpyOrigin, numpySpacing, isflip


def process_mask(mask):
    convex_mask = np.copy(mask)
    for i_layer in range(convex_mask.shape[0]):
        mask1 = np.ascontiguousarray(mask[i_layer])
        if np.sum(mask1) > 0:
            mask2 = convex_hull_image(mask1)
            if np.sum(mask2) > 1.5 * np.sum(mask1):
                mask2 = mask1
        else:
            mask2 = mask1
        convex_mask[i_layer] = mask2
    struct = generate_binary_structure(3, 1)
    dilatedMask = binary_dilation(convex_mask, structure=struct, iterations=10)
    return dilatedMask


def lumTrans(img):
    # print("start trans..")
    lungwin = np.array([-1200., 600.])
    newimg = (img - lungwin[0]) / (lungwin[1] - lungwin[0])
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    # print("liner trans..")
    newimg = (newimg * 200).astype('uint8')
    # print("trans end...")
    return newimg


def binarize_per_slice(image, spacing, intensity_th=-600, sigma=1, area_th=30, eccen_th=0.99, bg_patch_size=10):
    bw = np.zeros(image.shape, dtype=bool)

    # prepare a mask, with all corner values set to nan
    image_size = image.shape[1]
    grid_axis = np.linspace(-image_size / 2 + 0.5, image_size / 2 - 0.5, image_size)
    x, y = np.meshgrid(grid_axis, grid_axis)
    d = (x ** 2 + y ** 2) ** 0.5
    nan_mask = (d < image_size / 2).astype(float)
    nan_mask[nan_mask == 0] = np.nan
    for i in range(image.shape[0]):
        # Check if corner pixels are identical, if so the slice  before Gaussian filtering
        if len(np.unique(image[i, 0:bg_patch_size, 0:bg_patch_size])) == 1:
            current_bw = scipy.ndimage.filters.gaussian_filter(np.multiply(image[i].astype('float32'), nan_mask), sigma,
                                                               truncate=2.0) < intensity_th
        else:
            current_bw = scipy.ndimage.filters.gaussian_filter(image[i].astype('float32'), sigma,
                                                               truncate=2.0) < intensity_th

        # select proper components
        label = measure.label(current_bw)
        properties = measure.regionprops(label)
        valid_label = set()
        for prop in properties:
            if prop.area * spacing[1] * spacing[2] > area_th and prop.eccentricity < eccen_th:
                valid_label.add(prop.label)
        current_bw = np.in1d(label, list(valid_label)).reshape(label.shape)
        bw[i] = current_bw

    return bw


def savenpy_luna_single(name, savepath, luna_segment, luna_data, annos):
    islabel = annos is not None
    resolution = np.array([1, 1, 1])
    if os.path.exists(os.path.join(savepath, name + '_clean.npy')):
        print(name + " had been processed already")
        return
    print("name: ", name)
    sliceim, origin, spacing, isflip = load_itk_image(os.path.join(luna_data, name + '.mhd'))
    Mask, origin, spacing, isflip = load_itk_image(os.path.join(luna_segment, name + '.mhd'))
    if isflip:
        Mask = Mask[:, ::-1, ::-1]
    newshape = np.round(np.array(Mask.shape) * spacing / resolution).astype('int')
    m1 = Mask == 3
    m2 = Mask == 4
    Mask = m1 + m2
    xx, yy, zz = np.where(Mask)
    box = np.array([[np.min(xx), np.max(xx)], [np.min(yy), np.max(yy)], [np.min(zz), np.max(zz)]])
    box = box * np.expand_dims(spacing, 1) / np.expand_dims(resolution, 1)
    box = np.floor(box).astype('int')
    margin = 5
    extendbox = np.vstack(
        [np.max([[0, 0, 0], box[:, 0] - margin], 0), np.min([newshape, box[:, 1] + 2 * margin], axis=0).T]).T

    convex_mask = m1
    dm1 = process_mask(m1)
    dm2 = process_mask(m2)
    dilatedMask = dm1 + dm2
    Mask = m1 + m2

    extramask = dilatedMask ^ Mask
    bone_thresh = 210
    pad_value = 170

    if isflip:
        sliceim = sliceim[:, ::-1, ::-1]
        print('flip!')

    sliceim = lumTrans(sliceim)

    sliceim1, _ = resample(sliceim, spacing, resolution, order=1)
    sliceim2 = sliceim1[extendbox[0, 0]:extendbox[0, 1],
               extendbox[1, 0]:extendbox[1, 1],
               extendbox[2, 0]:extendbox[2, 1]]
    sliceim = sliceim2[np.newaxis, ...]

    print("img shape: ", sliceim.shape)
    np.save(os.path.join(savepath, name + '_clean.npy'), sliceim)
    np.save(os.path.join(savepath, name + '_spacing.npy'), spacing)
    np.save(os.path.join(savepath, name + '_extendbox.npy'), extendbox)
    np.save(os.path.join(savepath, name + '_origin.npy'), origin)
    np.save(os.path.join(savepath, name + '_mask.npy'), Mask)
    if islabel:
        this_annos = np.copy(annos[annos[:, 0] == (name)])
        label = []
        if len(this_annos) > 0:

            for c in this_annos:
                pos = worldToVoxelCoord(c[1:4][::-1], origin=origin, spacing=spacing)
                if isflip:
                    pos[1:] = Mask.shape[1:3] - pos[1:]
                label.append(np.concatenate([pos, [c[4] / spacing[1]]]))

        label = np.array(label)
        if len(label) == 0:
            label2 = np.array([[0, 0, 0, 0]])
        else:
            label2 = np.copy(label).T
            label2[:3] = label2[:3] * np.expand_dims(spacing, 1) / np.expand_dims(resolution, 1)
            label2[3] = label2[3] * spacing[1] / resolution[1]
            label2[:3] = label2[:3] - np.expand_dims(extendbox[:, 0], 1)
            label2 = label2[:4].T
        np.save(os.path.join(savepath, name + '_label.npy'), label2)
    # print("end.......")
    print(name, " end")


def savenpy_new(name, savepath, luna_data):
    resolution = np.array([1, 1, 1])
    if os.path.exists(os.path.join(savepath, name + '_clean.npy')):
        print(name + " had been processed already")
        return
    print("name: ", name)
    sliceim, origin, spacing, isflip = load_itk_image(os.path.join(luna_data, name + '.mhd'))
    if isflip:
        sliceim = sliceim[:, ::-1, ::-1]
        print('flip!')
    sliceim = lumTrans(sliceim)
    sliceim1, _ = resample(sliceim, spacing, resolution, order=1)
    sliceim = sliceim1[np.newaxis, ...]

    print("img shape: ", sliceim.shape)
    np.save(os.path.join(savepath, name + '_clean.npy'), sliceim)
    np.save(os.path.join(savepath, name + '_spacing.npy'), spacing)
    np.save(os.path.join(savepath, name + '_origin.npy'), origin)

    print(name, " end")


def preprocess_luna(patient_name):
    savepath = local_path+'temp/'
    luna_data = local_path+'files'
    luna_segment = 'E:/LUNA16/LUNA 2016/seg-lungs-LUNA16/'
    luna_label = 'E:/LUNA16/LUNA 2016/luna_raw/CSVFILES/annotations.csv'
    annos = np.array(pandas.read_csv(luna_label))

    patient = patient_name
    savenpy_luna_single(patient, savepath, luna_segment, luna_data, annos)

    print("end preprocess")


def preprocess_luna_new(patient_name):
    savepath = local_path+'temp/'
    luna_data = local_path+'files'
    patient = patient_name
    savenpy_new(patient, savepath, luna_data)

    print("end preprocess")


def compare_npy():
    batch_dir = "E:/LUNA16/LUNA 2016/preprocess/subset0/"
    single_dir = local_path+'temp/'
    filelist_single = [f for f in os.listdir(single_dir) if f.endswith('.npy')]
    for f in filelist_single:
        single_npy = np.load(os.path.join(single_dir, f))
        batch_npy = np.load(os.path.join(batch_dir, f))
        if single_npy.shape != batch_npy.shape:
            print(f, "is different")
        else:
            if (single_npy == batch_npy).all():
                print("is the same")
            else:
                print(f, "is different")


def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)

def preprocess(name, islabel=True):
    if islabel:
        preprocess_luna(name)  # shape: (1, 313, 240, 322)
    else:
        preprocess_luna_new(name)  # shape: (1, 358, 440, 440)


if __name__ == '__main__':
    patient_name = "1.3.6.1.4.1.14519.5.2.1.6279.6001.102681962408431413578140925249"
    preprocess(patient_name, False)
    # compare_npy()
    # flush_dir("./temp/")
