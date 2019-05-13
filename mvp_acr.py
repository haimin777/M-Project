import argparse
import os
from os.path import join

from keras import backend as K
from keras.models import load_model

import pydicom as pyd
import numpy as np
import cv2
import pyinotify
import asyncio
import mvp


parser = argparse.ArgumentParser()

def make_predictition_acr(image, model_path='/home/haimin/PycharmProjects/xray_density/breast_dense_4.h5'):

    model = load_model(model_path)
    res = model.predict(image)
    K.clear_session()
    return res


def load_and_norm(path):
    ds = pyd.dcmread(path)
    image = ds.pixel_array
    #image = segment_breast(image)[0]

    image = cv2.resize(image, (2000, 2600), interpolation=cv2.INTER_AREA)
    image = image.astype(np.float32)
    # normalize
    image -= np.mean(image)
    image /= np.std(image)
    image = np.expand_dims(image, axis=0)
    image = np.expand_dims(image, axis=3)
    return image, ds

def preprocess_one_image(X, img_path):

    # recognize projection and generate input for model

    try:
        img, ds1 = load_and_norm(img_path)

        # print(ds1.ImageType[3], ds1.ViewPosition)
        # print(ds1.ImageType[3], ds1.ViewPosition)
        if ds1.ImageType[3] == 'LEFT' and ds1.ViewPosition == 'CC':

            X[0][0] = img
        elif ds1.ImageType[3] == 'RIGHT' and ds1.ViewPosition == 'CC':

            X[1][0] = img
        elif ds1.ImageType[3] == 'LEFT' and ds1.ViewPosition == 'MLO':

            X[2][0] = img

        elif ds1.ImageType[3] == 'RIGHT' and ds1.ViewPosition == 'MLO':

            X[3][0] = img

    except Exception as e:
        print(e)

    return X



class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, work_folder='/incoming/data'):
        self.last_uid = None
        self.work_folder = work_folder
        self.last_listdir = None
        self.proc_list = []
        self.image_count = 0
        self.X = None
        self.predict = None

    def add_tag_to_one_folder_acr(self, folder, tag_list):
        # add given tag to same folder. No exchange folders
        # ????? is it nescessary to add tag to RAW image ????
        tag_index = np.argmax(self.predict)
        for root, _, files in os.walk(folder):
            for f in files:
                if mvp.isdicom(join(root, f)):
                    print(f, tag_list[tag_index], '---- add tag to folder')
                    mvp.add_tag(join(root, f), tag_list[tag_index])


    def process_IN_CLOSE_WRITE(self, event):

        if not event.dir and mvp.isdicom(event.pathname):

            # remember current folder
            # print(event.__dict__)
            # print(event.path.split('/')[3])

            current_dir = event.path.split('/')[3]
            if self.last_listdir == None:  # if work just start
                #process_to_file(join(self.work_folder, current_dir), event.pathname)
                self.proc_list.append(current_dir)


                self.X = [np.empty((1, 2600, 2000, 1)),
                                np.empty((1, 2600, 2000, 1)),
                                np.empty((1, 2600, 2000, 1)),
                                np.empty((1, 2600, 2000, 1))]
                preprocess_one_image(self.X, event.pathname)

                self.last_listdir = current_dir
                self.image_count += 1
                print(self.image_count, 'with None')

            elif self.last_listdir == current_dir and self.image_count !=0:
                # if folder not new, but new image detected, than process it and add to self.X

                preprocess_one_image(self.X, event.pathname)

                self.image_count += 1
                print(self.image_count, 'inside loop')
                if current_dir not in self.proc_list:
                    self.proc_list.append(current_dir)

                elif self.image_count == 4:
                    # check if folder new or already 4 image processed

                    self.image_count = 0

                    self.predict = make_predictition_acr(self.X)[0]
                    print(self.predict)
                    self.add_tag_to_one_folder_acr(join(self.work_folder, self.last_listdir), ['ACR_1', 'ACR_2', 'ACR_3', 'ACR_4'])
                    mvp.send_folder_to_pacs(join(self.work_folder, self.last_listdir))
                    print('send to pacs finished', self.last_listdir)
                    #print(self.image_count, 'before reset')
                    #self.image_count += 1
                    #print(self.image_count, 'after reset')
                    #self.last_listdir = current_dir
                    #self.proc_list.append(current_dir)





            elif self.last_listdir != current_dir and current_dir not in self.proc_list:
                # check if folder new or already 4 image processed

                # print('\n'*3, 'proc_list: ', self.proc_list, '\n', current_dir, '\n'*2, self.last_listdir)
                if self.last_listdir not in self.proc_list:

                    #work in case if series have only 2 images, than just send it to PACS
                    mvp.send_folder_to_pacs(join(self.work_folder, self.last_listdir))
                    print('sended to PACS without tags')
                self.image_count = 0
                self.X = [np.empty((1, 2600, 2000, 1)),
                          np.empty((1, 2600, 2000, 1)),
                          np.empty((1, 2600, 2000, 1)),
                          np.empty((1, 2600, 2000, 1))]
                preprocess_one_image(self.X, event.pathname)
                self.image_count += 1

                self.last_listdir = current_dir
                self.proc_list.append(current_dir)


if __name__ == '__main__':

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CLOSE_WRITE  # watched events

    loop = asyncio.get_event_loop()

    notifier = pyinotify.AsyncioNotifier(wm, loop, default_proc_fun=EventHandler())

    wdd = wm.add_watch('/incoming/data', mask, rec=True, auto_add=True)

    try:
        loop.run_forever()
    except:
        print('\nshutting down...')

    loop.stop()
    notifier.stop()
