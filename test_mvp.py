# test_mvp.py
import unittest
import mvp
import pydicom as pyd
import os


class MprojectTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print("this will run before all test methods.")
        dcm_path = pyd.dcmread('img').SeriesInstanceUID
        os.mkdir(dcm_path)

    @classmethod
    def tearDownClass(self):
        print("-this will run after all test methods.---------------------------------------")

    def setUp(self):
        print("this will run before every test method.")

    def tearDown(self):
        print("this will run after every test method.")


    # test method
    def test_predict(self):
        print('test 1 start')
        pred = mvp.make_predictition('img')
        print(len(pred))

        # validate the result of the code we're testing.
        self.assertIsNotNone(pred)

    def test_add_tag(self):
        mvp.add_tag('img', '1')
        self.assertEqual(pyd.dcmread('img').StudyID, '1')

