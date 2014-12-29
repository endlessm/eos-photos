#!/usr/bin/python

import os
import unittest

from dogtail.tree import *
from dogtail.utils import *
from dogtail.procedural import *

from BaseTestCase import *

class TestOpenImage(BaseTestCase):
    def setUp(self):
        super(TestOpenImage, self).setUp()
        #grid = self.app.child('Thumbs Grid')
        self.open_button = self.app.child('splash-open-photos-button')
        self.open_file_button = self.app.child('OK')
        self.picture_label = self.app.child('Pictures') # actionable / toggle button
        self.test_image_cell = self.app.child('test.jpg') # table cell
        seld.main_image = self.app.child('image_container')
        #right_toolbar = self.app.child("right_toolbar")
        #self.thumbs = [x for x in grid.children if 'thumb_' in x.name]

    def test_openImage(self):
        print "Clicking on Pictures label"
        self.picture_label.click()
        print "Click on test image"
        self.test_image_cell.click()
        print "Click OK to open image"
        self.open_file_button.click()
        if self.main_image.showing:
            print "image loaded"
            self.assertTrue(self.main_image.showing)
        else:
            print "Test image failed to load"



if __name__ == '__main__':
    unittest.main()