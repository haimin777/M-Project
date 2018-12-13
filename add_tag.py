import os
from os.path import join

import pydicom as pyd

import mvp


def add_tag(image, tag):
    # add tag and save in another folder (target)
    print(image, 'from add tag')
    img = pyd.dcmread(image)
    img.AccessionNumber = tag
    img.ImageComments = tag
    img.StudyID = tag
    # pyd.dcmwrite(target, img)
    pyd.dcmwrite(image, img)


    print('tag added {} to {}'.format(tag, image))



def add_tag_to_one_folder(folder, tag):
    # add given tag to same folder. No exchange folders

    for root, _, files in os.walk(folder):
        for f in files:
            print(f, '---- add tag to folder')
            # add_tag(os.path.join(root, f), tag)
            add_tag(join(root, f), tag)


def recognise_and_add_tag(image):
    res = mvp.make_predictition(image)
    if res[0][0] > 0.65:
        print('birads_1 with {}'.format(res[0][0]))
        add_tag(image, 'norm')


if __name__ == '__main__':
    # recognise_and_add_tag('/home/haimin/Dicom/mammograms/1')
    add_tag_to_folder('/home/haimin/Dicom/work/1.3.12.2.1107.5.12.7.4586.30000018080206270900000000017', 'tag--111')
