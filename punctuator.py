#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

from PyQt5.QtWidgets import QApplication

from gui import Punctuator

class App(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.ui = Punctuator()

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # form = Punctuator()
    # app.exec_()

    app = App(sys.argv)
    sys.exit(app.exec_())