# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_info.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InfoForm(object):
    def setupUi(self, info_form):
        info_form.setObjectName("info_form")
        info_form.resize(741, 546)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(info_form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.info_table = QtWidgets.QTableWidget(info_form)
        self.info_table.setObjectName("info_table")
        self.info_table.setColumnCount(0)
        self.info_table.setRowCount(0)
        self.verticalLayout.addWidget(self.info_table)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(info_form)
        QtCore.QMetaObject.connectSlotsByName(info_form)

    def retranslateUi(self, info_form):
        _translate = QtCore.QCoreApplication.translate
        info_form.setWindowTitle(_translate("info_form", "Form"))

