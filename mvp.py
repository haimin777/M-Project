import asyncio
import os
import shutil as sh

import cv2
import numpy as np
import pydicom as pyd
import pyinotify
from keras.models import load_model

import add_tag


def make_predictition(image, model_path='/home/haimin/PycharmProjects/Tensorflow/ddsm_YaroslavNet_s10.h5'):
    image = pyd.dcmread(image).pixel_array
    image = cv2.resize(image, (896, 1152), interpolation=cv2.INTER_AREA)
    image = np.expand_dims(image, -1)
    image = np.expand_dims(image, 0)
    model = load_model(model_path)
    res = model.predict(image)
    return res


def process_folder(folder):
    # make predictition for folder
    res_list = []
    for root, dirs, images in os.walk(folder):
        for image in images:
            res = make_predictition(os.path.join(root, image))
            res_list.append(res[0][0])
            print('image processed, res_list: ', res_list)
    return res_list


def move_folder_to_pacs(folder):
    # move processed folder to PACS
    # comand = 'dcmsend 127.0.0.1 4242 --scan-directories '
    comand = 'dcmsend 3.120.139.162 4242 --scan-directories '

    comand += folder
    os.system(comand)


def get_series_uid(img):
    return (pyd.dcmread(img, force=True).SeriesInstanceUID)


def check_new_image(img, last_uid):
    # true if img from processing series
    # img - new image path
    # last_uid - series uid of previous image
    UID = get_series_uid(img)
    # print('----'*10, UID)
    return UID == last_uid



#
def get_total_files_number(self, folder):
    n = 0
    for root, dirs, files in os.walk(folder):
        print('total files: ', len(files))
        for f in files:
            # if f.endswith('.jp2'):
            if f:
                n += 1
    print('files number:', n)
    return n


class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, work_folder='/incoming/data'):
        self.last_uid = None
        self.work_folder = work_folder
        self.last_listdir = None


    def process_IN_CLOSE_WRITE(self, event):

        # !!!! change to exacly file system
        if not event.dir:  # and event.name.endswith('.dcm'):  # only for new files, not folders

            # print(event.__dict__)

            # print('last uid: ', self.last_uid)
            print("Got new file: ", event.pathname)

            last_uid = self.last_uid
            if check_new_image(event.pathname, last_uid):
                # if existing series than copy new file to folder with name seriesUID
                #print('image with UID: ', last_uid)
                sh.move(event.pathname, os.path.join(self.work_folder, last_uid))
                print('copy {} to {} folder'.format(event.name, last_uid))
                self.last_listdir = os.listdir(os.path.join(self.work_folder, self.last_uid))  #save last folder state

            elif last_uid is None:
                # if start working
                os.makedirs(os.path.join(self.work_folder, get_series_uid(event.pathname)))
                self.last_uid = get_series_uid(event.pathname)
                sh.move(event.pathname, os.path.join(self.work_folder, self.last_uid))
                print('---new folder created {} for file {}'.format(self.last_uid, event.name))
                self.last_listdir = os.listdir(os.path.join(self.work_folder, self.last_uid))

            else:
                if str(event.name) not in self.last_listdir:
                    print('event name', str(event.name))
                    print('last listdir: ', self.last_listdir)
                    print('current dirlist: ', os.listdir(os.path.join(self.work_folder, self.last_uid)))
                    self.last_listdir = os.listdir(os.path.join(self.work_folder, self.last_uid))
                    new_uid = get_series_uid(event.pathname)
                    # predict_list = process_folder(os.path.join(self.work_folder, self.last_uid))
                    predict_list = [0.5, 0.7, 0.9]
                    # print(predict_list)
                    if min(predict_list) <= 0.7:
                        print('add tags 1')
                        add_tag.add_tag_to_one_folder(os.path.join(self.work_folder, self.last_uid), tag='tag1')
                        #move_folder_to_pacs(os.path.join(self.work_folder, self.last_uid))
                        print('folder moved to PACS {}'.format(self.last_uid))
                    else:
                        print('add tags 0')
                        add_tag.add_tag_to_one_folder(os.path.join(self.work_folder, self.last_uid), 'tag2')
                        #move_folder_to_pacs(os.path.join(self.work_folder, self.last_uid))
                        print('folder moved to PACS {}'.format(self.last_uid))

                    self.last_uid = new_uid

                    try:
                        print('---', self.last_listdir, '---', event.name)
                        os.makedirs(os.path.join(self.work_folder, self.last_uid))
                        sh.move(event.pathname, os.path.join(self.work_folder, self.last_uid))
                    except Exception as e:
                        print(e)
                    print('new folder created {} for file {}'.format(self.last_uid, event.name))


if __name__ == '__main__':

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CLOSE_WRITE  # watched events

    loop = asyncio.get_event_loop()

    notifier = pyinotify.AsyncioNotifier(wm, loop, default_proc_fun=EventHandler())

    wdd = wm.add_watch('/incoming/data', mask, rec=True, auto_add=True)
    # wdd = wm.add_watch('/var/lib/orthanc/db-v6', mask, rec=True, auto_add=True)

    try:
        loop.run_forever()
    except:
        print('\nshutting down...')

    loop.stop()
    notifier.stop()
