# test_mvp.py
import unittest
import mvp
import pydicom as pyd
import os
import shutil as sh
import pandas as pd

class MprojectTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print("this will run before all test methods.")
        self.dcm_path = pyd.dcmread('img').SeriesInstanceUID
        os.mkdir(self.dcm_path)
        print(self.dcm_path)
        sh.copy('img', self.dcm_path)

    @classmethod
    def tearDownClass(self):
        print("-this will run after all test methods.---------------------------------------")
        sh.rmtree(self.dcm_path)

    '''
    def setUp(self):
        print("this will run before every test method.")

    def tearDown(self):
        print("this will run after every test method.")
    '''


    # test method
    @unittest.skip("skipping test because dont like to use tensorflow")
    def test_make_predict(self):
        print('test 1 start')
        pred = mvp.make_predictition('img')
        print(len(pred))

        # validate the result of the code we're testing.
        self.assertIsNotNone(pred)

    @unittest.skip('its OK, try another')
    def test_process_to_file(self):
        # find dicom and create texftpile to write its predict
        mvp.process_to_file(self.dcm_path, 'img')
        textfile_path = os.path.join(self.dcm_path, self.dcm_path.split('/')[-1])
        self.assertIsNotNone(pd.read_csv(textfile_path))





    def test_add_tag(self):
        mvp.add_tag('img', '1')
        self.assertEqual(pyd.dcmread('img').StudyID, '1')


    @unittest.skip('dont know!!')
    def test_add_tag_to_one_folder(self):
        abs_dcm_path = os.path.abspath(self.dcm_path)
        mvp.add_tag_to_one_folder(abs_dcm_path, self.dcm_path, 'test_tag_1', 'test_tag_2')
        dcm_tag = pyd.dcmread(os.path.join(self.dcm_path,'img').StudyID)
        self.assertEqual(dcm_tag, 'test_tag_1') or self.assertEqual(dcm_tag, 'test_tag_2')


    def test_isdicom(self):
        self.assertTrue(mvp.isdicom('/home/haimin/PycharmProjects/M-git/M-Project/img'))


