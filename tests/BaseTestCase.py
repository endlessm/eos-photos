#!/usr/bin/python

import os
import unittest

from dogtail.tree import *
from dogtail.utils import *
from dogtail.procedural import *

from dogtail.config import config

config.childrenLimit = 300

class BaseTestCase(unittest.TestCase):
    app_path = 'eos-photos'
    app_id = 'com.endlessm.photos'
    app = None
    print "finished basics"

    def setUp(self):
        # Wait for shell to finish loading
        print "Wait for shell to finish loading"
        doDelay(2)

        # Enable a11y in case it's disabled
        if not isA11yEnabled():
            print "Accessibility layer is not enabled. Will not load accessibility layer"
            enableA11y(True)

        # Launch the app going to be tested
        subprocess.Popen(self.app_path, shell=True)

        # Wait for 2 secs for the app to load
        print "Wait for app to finish loading"
        doDelay(3)

        self.app = root.application(self.app_id)
        focus.application(self.app_id)

    def tearDown(self):
        print "Killing %s process" %self.app_path
        os.system("kill -9 `ps ax | grep gjs | grep eos-photos | awk '{print $1}'`")
        print "Done."
