# test_mvp.py
import unittest
import mvp
import pydicom as pyd


class MprojectTestCase(unittest.TestCase):
    # test method
    def test_predict(self):
        pred = mvp.make_predictition('img')
        print(len(pred))

        # validate the result of the code we're testing.
        self.assertIsNotNone(pred)

    def test_add_tag(self):
        mvp.add_tag('img', '1')
        self.assertEqual(pyd.dcmread('img').StudyID, '1')

