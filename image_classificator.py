# -*- coding: utf-8 -*-
"""
Created on Tue May 29 18:42:54 2018

@author: Haimin
скрипт для сортировки
запускаешь в ipython или spyder
"""

import os
import matplotlib.pyplot as plt

import pydicom
import shutil as sh
import glob
import mvp



class ImageClassificator:

    def __init__(self):
        self.sorting_dir = '/home/haimin/Dicom/birads_3'
        self.dir_from = ''
        self.dir_to = 'C:\\Users\\Haimin\\Dicom\\DICOM2'
        self.dir_to0 = '/home/haimin/Dicom/birads_3/neg'
        self.dir_to1 = '/home/haimin/Dicom/birads_3/pos'

    def image_sort(self):

        os.chdir(self.sorting_dir)
        for p1 in os.listdir(self.sorting_dir):
            ds = pydicom.dcmread(p1)
            if ds.ImageType[0] == 'ORIGINAL' or ds.ViewPosition == 'CC':
                print("deleting ", p1)
                os.remove(p1)




    def print_image(self, im):

        ds = pydicom.dcmread(im)
        plt.figure(figsize=(5, 10))  # displaying image size
        plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
        plt.ylabel(im)
        plt.show()

    def image_classifier(self):

        dcm_paths = glob.glob(self.sorting_dir + '/*/*')

        print(len(dcm_paths))
        # print(os.listdir(dir_from))
        #os.chdir(self.dir_to)
        # plt.ion()
        for dcm in dcm_paths:
            if mvp.isdicom(dcm):
                self.print_image(dcm)
                a = input('for image {} 0 - bad or 1 - good pics, 2 - I dont know: '.format(p1))
                if a == '0':
                    print('sended to dir 0')
                    sh.copyfile(dcm, os.path.join(self.dir_to0, dcm.split('/')[-1]))


                elif a == '1':
                    print('sended to dir 1')
                    sh.copyfile(dcm, os.path.join(self.dir_to1, dcm.split('/')[-1]))
                elif a == '2':
                    print('not classified')


if __name__ == "__main__":
    sorting = ImageClassificator()
    sorting.image_classifier()
