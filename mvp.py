import asyncio
import os
import shutil as sh
from os.path import join

import cv2
import numpy as np
import pydicom as pyd
import pyinotify
from keras.models import load_model


def make_predictition(image, model_path='/home/haimin/PycharmProjects/Tensorflow/ddsm_YaroslavNet_s10.h5'):
    image = pyd.dcmread(image).pixel_array
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


def add_tag_to_one_folder(folder, tag):
    # add given tag to same folder. No exchange folders

    for root, _, files in os.walk(folder):
        for f in files:
            if isdicom(join(root, f)):
                print(f, '---- add tag to folder')
                # add_tag(join(root, f), tag)
                add_tag(join(root, f), tag)


def isdicom(file_path):
    try:
        if pyd.dcmread(file_path).ImageType[0] != 'ORIGINAL':
            return True
        else:
            print('RAW image acepted')
            return False
    except:
        return False


def is_processed(processed_list, image):

    pass


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
        self.proc_list = []


    def process_IN_CLOSE_WRITE(self, event):


        if not event.dir and isdicom(event.pathname):
            # remember current folder
            #print(event.__dict__)
            #print(event.path.split('/')[3])
            current_dir = event.path.split('/')[3]
            if self.last_listdir == None: # if work just start
                process_to_file(join('/incoming/data', current_dir), event.pathname)

                self.last_listdir = current_dir

            elif self.last_listdir == current_dir:
                process_to_file(join('/incoming/data', current_dir), event.pathname)
                #print(event.name)

            elif self.last_listdir != current_dir:

                print('send to pacs', self.last_listdir)
                process_to_file(join('/incoming/data', current_dir), event.pathname)

                self.last_listdir = current_dir




    '''  
    
    def process_IN_CLOSE_WRITE(self, event):

        # !!!! change to exacly file system
        # if not event.dir:  # and event.name.endswith('.dcm'):  # only for new files, not folders
        if not event.dir and isdicom(event.pathname) and event.name not in self.last_listdir:

            # print(event.__dict__)

            # print('last uid: ', self.last_uid)
            print("Got new file: ", event.pathname)

            last_uid = self.last_uid
            if check_new_image(event.pathname, last_uid):
                # if existing series than copy new file to folder with name seriesUID
                print('image with UID: ', last_uid)

                uid_folder = join(self.work_folder, last_uid)
                sh.copy(event.pathname, uid_folder)
                # process if folder image
                process_to_file(uid_folder, join(uid_folder, event.name))
                print('copy {} to {} folder'.format(event.name, last_uid))
                self.last_listdir = os.listdir(join(self.work_folder, self.last_uid))  # save last folder state
                self.proc_list.append(event.name)
                print(self.last_listdir, '----')
                print('proc_list:', self.proc_list)

            elif last_uid is None:
                # if start working
                os.makedirs(join(self.work_folder, get_series_uid(event.pathname)))
                self.last_uid = get_series_uid(event.pathname)
                uid_folder = join(self.work_folder, self.last_uid) # path to folder with name SeriesinstanceUID

                sh.copy(event.pathname, uid_folder)
                process_to_file(uid_folder, join(uid_folder, event.name))
                print('---new folder created {} for file {}'.format(self.last_uid, event.name))
                self.last_listdir = os.listdir(join(self.work_folder, self.last_uid))
                self.proc_list.append(event.name)
                print(self.last_listdir, '----')
                print('proc_list:', self.proc_list)

            else:
                print('------not 2 first cases------------')
                if str(event.name) not in self.last_listdir:
                    #print('last listdir: ', self.last_listdir)
                    print('current dirlist: ', os.listdir(join(self.work_folder, self.last_uid)))
                    self.last_listdir = os.listdir(join(self.work_folder, self.last_uid))
                    new_uid = get_series_uid(event.pathname)
                    predict_list = process_folder(join(self.work_folder, self.last_uid))
                    # predict_list = [0.5, 0.7, 0.9]
                    # print(predict_list)
                    if min(predict_list) <= 0.7:
                        print('add tags 1')
                        add_tag_to_one_folder(join(self.work_folder, self.last_uid), tag='tag1')
                        move_folder_to_pacs(join(self.work_folder, self.last_uid))
                        print('folder moved to PACS {}'.format(self.last_uid))
                    else:
                        print('add tags 0')
                        add_tag_to_one_folder(join(self.work_folder, self.last_uid), 'tag2')
                        move_folder_to_pacs(join(self.work_folder, self.last_uid))
                        print('folder moved to PACS {}'.format(self.last_uid))

                    self.last_uid = new_uid

                    try:
                        print('---', self.last_listdir, '---', event.name)
                        os.makedirs(join(self.work_folder, self.last_uid))
                        sh.copy(event.pathname, join(self.work_folder, self.last_uid))
                    except Exception as e:
                        print(e)
                    print('new folder created {} for file {}'.format(self.last_uid, event.name))

        '''
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
