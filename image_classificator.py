# -*- coding: utf-8 -*-
"""
Created on Tue May 29 18:42:54 2018

@author: Haimin
скрипт для сортировки
запускаешь в ipython или spyder
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import pydicom
import shutil as sh


#укажите сортируемую папку                   
def image_sort(sorting_dir = 'C:\\Users\\Haimin\\Dicom\\DICOM2'):
    
    os.chdir(sorting_dir)
    for p1 in os.listdir(sorting_dir):
        ds = pydicom.dcmread(p1)
        if ds.ImageType[0] == 'ORIGINAL' or ds.ViewPosition == 'CC':
            print("deleting ", p1)
            os.remove(p1)
        
def recursive_list(dir_from = 'C:\\Users\\Haimin\\Dicom\\test',
                   dir_to = 'C:\\Users\\Haimin\\Dicom\\DICOM2'):
   n=1
   for root, dirs, files in os.walk(dir_from):
       for name in files:
           print("copy {} to {}".format(name, n))
           sh.copyfile(os.path.join(root, name),
                       os.path.join(dir_to, str(n)))
           n+=1
           
    
def print_image(im):
    ds = pydicom.dcmread(im)
    plt.figure(figsize=(5, 10)) #displaying image size
    plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
    plt.show()

def image_classifier(dir_from='C:\\Users\\Haimin\\Dicom\\DICOM2',
                     dir_to0 = 'C:\\Users\\Haimin\\Dicom\\01',
                     dir_to1 ='C:\\Users\\Haimin\\Dicom\\11'):
    #print(os.listdir(dir_from))
    os.chdir(dir_from)
    plt.ion()
    for p1 in os.listdir(dir_from):
        print_image(p1)
        a = input('for image {} 0 - bad or 1 - good pics, 2 - I dont know: '.format(p1))
        if a == '0':
            print('sended to dir 0')
            sh.copyfile(p1, os.path.join(dir_to0, p1))
            
        elif a == '1':
            print('sended to dir 1')
            sh.copyfile(p1, os.path.join(dir_to1,p1))
        elif a =='2':
            print('not classified')
                                
            
        
if __name__ == "__main__":
    
    #recursive_list()
    #image_sort()
    
    image_classifier()   