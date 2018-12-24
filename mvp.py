import asyncio
import glob
import os
from os.path import join

import cv2
import numpy as np
import pydicom as pyd
import pyinotify
from keras.models import load_model


def make_predictition(image, model_path='/home/haimin/PycharmProjects/Tensorflow/ddsm_YaroslavNet_s10.h5'):
    image = pyd.dcmread(image).pixel_array/14.5
    image = cv2.resize(image, (896, 1152), interpolation=cv2.INTER_AREA)
    image = np.expand_dims(image, -1)
    image = np.expand_dims(image, 0)
    model = load_model(model_path)
    res = model.predict(image)
    return res


def process_to_file(folder, img):
    # make predictition for new image and save it to csv
    csv_name = join(folder, folder.split('/')[-1])
    predict = str(make_predictition(img)[0][0])
    # print(predict[0][0])
    if os.path.isfile(csv_name):
        print('add result to file')
        with open(csv_name, 'a') as csv_file:
            csv_file.write(predict)
            csv_file.write('\n')

    else:
        print('create file for writing predict results')
        with open(csv_name, 'w') as csv_file:
            csv_file.write(predict)
            csv_file.write('\n')


def process_folder(uid_folder):
    # get predictions for folder from specific file, where they stored

    res_list = []
    path = join(uid_folder, uid_folder.split('/')[-1])
    print(path)
    with open(path) as f:
        for row in f:
            res_list.append(float(row))
    os.remove(path)
    print('--------file with predicts deleted------')
    return res_list


def add_tag(image, tag):
    # add tag and save in another folder (target)
    print(image, 'from add tag')
    img = pyd.dcmread(image)
    img.AccessionNumber = tag
    img.ImageComments = tag
    img.StudyID = tag
    pyd.dcmwrite(image, img)

    print('tag added {} to {}'.format(tag, image))


def add_tag_to_one_folder(folder, folder_name, tag1, tag2):
    # add given tag to same folder. No exchange folders
    # ????? is it nescessary to add tag to RAW image ????

    # find txt file with predictions and convert to list
    predict_list = []
    with open(glob.glob(folder + '/' + folder_name)[0], 'r') as f:
        for row in f:
            predict_list.append(float(row))

    if min(predict_list) < 0.6:
        print('mini predict is: {}, add tag: {}'.format(min(predict_list), tag1))

        for root, _, files in os.walk(folder):
            for f in files:
                if isdicom(join(root, f)):
                    print(f, tag1, '---- add tag to folder')
                    add_tag(join(root, f), tag1)

    else:

        for root, _, files in os.walk(folder):
            for f in files:
                if isdicom(join(root, f)):
                    print(f, tag2, '---- add tag to folder')
                    add_tag(join(root, f), tag2)


def isdicom(file_path):
    try:
        if pyd.dcmread(file_path).ImageType[0] != 'ORIGINAL':
            return True
        else:
            # print('RAW image acepted')
            return False
    except:
        return False


def send_folder_to_pacs(folder):
    # move processed folder to PACS
    # comand = 'dcmsend 127.0.0.1 4242 --scan-directories '
    # comand = 'dcmsend 3.120.139.162 4242 --scan-directories '
    dcm_paths = glob.glob(folder + '/*/*/*.dcm')
    for f in dcm_paths:
        comand = 'dcmsend 3.120.139.162 4242 ' + f
        print(f, '-- sended to pask')
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


class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, work_folder='/incoming/data'):
        self.last_uid = None
        self.work_folder = work_folder
        self.last_listdir = None
        self.proc_list = []

    def process_IN_CLOSE_WRITE(self, event):

        if not event.dir and isdicom(event.pathname):

            # remember current folder
            # print(event.__dict__)
            # print(event.path.split('/')[3])

            current_dir = event.path.split('/')[3]
            if self.last_listdir == None:  # if work just start
                process_to_file(join(self.work_folder, current_dir), event.pathname)
                self.proc_list.append(current_dir)

                self.last_listdir = current_dir

            elif self.last_listdir == current_dir:
                process_to_file(join(self.work_folder, current_dir), event.pathname)
                # print(event.name)
                if current_dir not in self.proc_list:
                    self.proc_list.append(current_dir)


            elif self.last_listdir != current_dir and current_dir not in self.proc_list:  # check if folder new

                # print('\n'*3, 'proc_list: ', self.proc_list, '\n', current_dir, '\n'*2, self.last_listdir)

                add_tag_to_one_folder(join(self.work_folder, self.last_listdir), self.last_listdir, '111', '000')
                send_folder_to_pacs(join(self.work_folder, self.last_listdir))
                print('send to pacs finished', self.last_listdir)
                process_to_file(join('/incoming/data', current_dir), event.pathname)

                self.last_listdir = current_dir
                self.proc_list.append(current_dir)


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
