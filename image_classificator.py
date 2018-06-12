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


class ImageClassificator:

    def __init__(self):
        self.sorting_dir = 'C:\\Users\\Haimin\\Dicom\\DICOM2'
        self.dir_from = 'C:\\Users\\Haimin\\Dicom\\test'
        self.dir_to = 'C:\\Users\\Haimin\\Dicom\\DICOM2'
        self.dir_to0 = 'C:\\Users\\Haimin\\Dicom\\01'
        self.dir_to1 = 'C:\\Users\\Haimin\\Dicom\\11'

    def image_sort(self):

        os.chdir(self.sorting_dir)
        for p1 in os.listdir(self.sorting_dir):
            ds = pydicom.dcmread(p1)
            if ds.ImageType[0] == 'ORIGINAL' or ds.ViewPosition == 'CC':
                print("deleting ", p1)
                os.remove(p1)

    def recursive_list(self):
        n = 1
        for root, dirs, files in os.walk(self.dir_from):
            for name in files:
                print("copy {} to {}".format(name, n))
                sh.copyfile(os.path.join(root, name),
                            os.path.join(self.dir_to, str(n)))
                n += 1

    def print_image(self, im):

        ds = pydicom.dcmread(im)
        plt.figure(figsize=(5, 10))  # displaying image size
        plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
        plt.ylabel(im)
        plt.show()

    def image_classifier(self):

        # print(os.listdir(dir_from))
        os.chdir(self.dir_to)
        # plt.ion()
        for p1 in os.listdir(self.dir_to):
            self.print_image(p1)
            a = input('for image {} 0 - bad or 1 - good pics, 2 - I dont know: '.format(p1))
            if a == '0':
                print('sended to dir 0')
                sh.copyfile(p1, os.path.join(self.dir_to0, p1))


            elif a == '1':
                print('sended to dir 1')
                sh.copyfile(p1, os.path.join(self.dir_to1, p1))
            elif a == '2':
                print('not classified')


if __name__ == "__main__":
    sorting = ImageClassificator()
    sorting.image_classifier()
