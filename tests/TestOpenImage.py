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
        self.open_button = self.app.child('splash_open_button')
        self.main_image = self.app.child('image_container')

    def test_openImage(self):
        self.open_button.grab_focus()
        self.open_button.click()
        
        doDelay(2)

        self.open_file_button = self.app.child('OK')
        self.picture_label = self.app.child('Pictures') # actionable / toggle button
        self.test_image_cell = self.app.child('test.jpg') # table cell
        
        # Click on Pictures label
        self.picture_label.click()
        # put focus on the desired image (this in case it's not the first on on the list)
        self.test_image_cell.grab_focus()
        #self.test_image_cell.click()
        
        # Click OK from the file chooser
        self.open_file_button.click()
        self.assertTrue(self.main_image.showing)


if __name__ == '__main__':
    unittest.main()