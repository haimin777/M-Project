import pydicom as pyd
import os
import matplotlib.pyplot as plt
import numpy as np
import cv2


def image_downsampling(im, work_dir='C:\\Users\\Haimin\\Dicom\\01'):
    # os.chdir(work_dir)
    ds = pyd.dcmread(im)
    data = ds.pixel_array
    data_downsampling = data[::8, ::8]
    ds.PixelData = data_downsampling.tostring()
    ds.Rows, ds.Columns = data_downsampling.shape
    pyd.dcmwrite(im, ds)
    print('convert from {} to {}'.format(data.shape, data_downsampling.shape))


# ---------------------------------------------------------------------------------------------------------------------
#                         adding classification tags and reshaping images
# ---------------------------------------------------------------------------------------------------------------------

class Preprocessing:

    def __init__(self):
        self.workdir = 'C:\\Users\\Haimin\\Dicom\\01'

    def preprocessing(self):
        os.chdir(self.workdir)
        for name in os.listdir(self.workdir):
            ds = pyd.dcmread(name)
            data = ds.pixel_array
            data_downsampling = data[::8, ::8]  # downsize in 8 times
            ds.PixelData = data_downsampling.tostring()
            ds.Rows, ds.Columns = data_downsampling.shape
            ds.AccessionNumber = '01'
            pyd.dcmwrite(name, ds)
            print('tag added and reshaped to', name)

    def show_tags(self, im):
        os.chdir(self.workdir)
        ds = pyd.dcmread(im)
        print(ds.AccessionNumber, '\n', ds.pixel_array.shape)
        # print(ds.dir('num'))

    def create_input(self): #create numpy arrays from taken dicom files
        os.chdir(self.workdir)
        array_x_list = list()
        array_y_list = list()
        for image in os.listdir(self.workdir):
            ds = pyd.dcmread(image)
            array_x_list.append(ds.pixel_array)
            array_y_list.append(ds.AccessionNumber)
        input_images = np.expand_dims(np.array(array_x_list), -1)
        print(input_images.shape)
        print(array_y_list)

    def create_input_image(self, dcm_img):   #create reshaped to 1152x896 image for using in NN

        ds = pyd.dcmread(dcm_img)
        data = ds.pixel_array
        d2 = cv2.resize(data, (896, 1152), interpolation=cv2.INTER_AREA)
        d2 = np.expand_dims(d2, -1)
        d2 = np.expand_dims(d2, 0)
        print('reshaped from {}, to {}'.format(data.shape, d2.shape))

        return d2




if __name__ == "__main__":
    start = Preprocessing()
    #start.preprocessing()
    #start.create_input()
    start.create_input_image('test')
