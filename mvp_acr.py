import asyncio
import glob
import os
from os.path import join

import cv2
import numpy as np
import pydicom as pyd
import pyinotify
from keras.models import load_model
from keras import backend as K

import argparse
parser = argparse.ArgumentParser()

def make_predictition_acr(image, model_path='/home/haimin/PycharmProjects/Tensorflow/ddsm_YaroslavNet_s10.h5'):
    image = pyd.dcmread(image).pixel_array/14.5
    image = cv2.resize(image, (896, 1152), interpolation=cv2.INTER_AREA)
    image = np.expand_dims(image, -1)
    image = np.expand_dims(image, 0)
    model = load_model(model_path)
    res = model.predict(image)
    K.clear_session()
    return res
