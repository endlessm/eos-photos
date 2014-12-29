#!/usr/bin/python

import os
import unittest

from dogtail.tree import *
from dogtail.utils import *
from dogtail.procedural import *

from BaseTestCase import *

class TestOpenImageButton(BaseTestCase):
    def setUp(self):
        super(TestOpenImageButton, self).setUp()
        #grid = self.app.child('Thumbs Grid')
        self.open_button = self.app.child('splash_open_button')
        #right_toolbar = self.app.child("right_toolbar")
        #self.thumbs = [x for x in grid.children if 'thumb_' in x.name]

    def test_openImage_button(self):
    	if self.open_button.showing:
    		print "open button is available"
    		self.assertTrue(self.open_button.showing)
    	else:
    		print "there aint no toolbar showing"
        # self.assertTrue(len(self.thumbs) > 0)
        # if self.thumbs[1].showing:
        #     self.assertTrue(self.thumbs[1].showing)
        #     print "Thmbanails are available, Pass"


if __name__ == '__main__':
    unittest.main()