#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json

from PyQt5 import QtWidgets, QtCore, QtGui

import ui_main
import ui_info

import parse

class ResiltInfo(QtWidgets.QMainWindow, ui_info.Ui_info_form):
    def __init__(self, data):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.info_table.resizeColumnsToContents()
        self.info_table.resizeRowsToContents()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(['Правило', 'Шаблон', 'Результат'])
        self.info_table.setRowCount(len(data))
        for row, item in enumerate(data):
            for column, field in enumerate(item):
                self.info_table.setItem(row, column, QtWidgets.QTableWidgetItem(field))

class Punctuator(QtWidgets.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.rules = None
        self.rules_fn = None
        self.text_parser = parse.TextParser()
        self.result = None
        self.text_fn = None

        self.info = None

        self.connect_all()

    def connect_all(self):
        self.action_load_rule.triggered.connect(self.load_rules)
        self.action_save_rule.triggered.connect(self.save_rules)
        self.action_save_as_rule.triggered.connect(self.save_as_rules)
        self.action_load_text.triggered.connect(self.load_text)
        self.action_save_text.triggered.connect(self.save_text)
        self.action_save_as_text.triggered.connect(self.save_as_text)
        self.action_exit.triggered.connect(self.exit)

        self.text_input_edit.textChanged.connect(self.process)
        self.result_list.itemDoubleClicked.connect(self.result_info)

        self.rule_add_btn.clicked.connect(self.rule_add)
        self.rule_remove_btn.clicked.connect(self.rule_remove)
        self.rule_up_btn.clicked.connect(self.rule_up)
        self.rule_down_btn.clicked.connect(self.rule_down)
        self.rule_apply_btn.clicked.connect(self.rule_parse)

        self.rule_list.itemClicked.connect(self.rules_select)
        self.rule_list.itemChanged.connect(self.rules_edit)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Insert), self.rule_list).activated.connect(self.rule_add)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.rule_list).activated.connect(self.rule_remove)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Control + QtCore.Qt.Key_Up), self.rule_list).activated.connect(self.rule_up)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Control + QtCore.Qt.Key_Down), self.rule_list).activated.connect(self.rule_down)

        self.rule_template_edit.textChanged.connect(self.template_edit)


    def _fill_rule_list(self):
        self.rule_list.clear()
        for r in self.rules:
            i = QtWidgets.QListWidgetItem(r.name)
            i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)
            self.rule_list.addItem(i)
            # self.rule_list.addItem(QtWidgets.QListWidgetItem(r.name).setFlags(i.flags() | QtCore.Qt.ItemIsEditable))

    def load_rules(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберете файл")
        if file:
            if file[0] != '':
                self.rules_fn = file[0]
                with open(self.rules_fn, 'rt', encoding = 'utf-8') as rules_f:
                    self.rules = [self.text_parser.Rule(r['name'], text = [t for t in r['text']]) for r in json.load(rules_f)]
                    self.rule_parse()
                    self._fill_rule_list()

    def save_rules(self):
        if self.rules_fn and self.rules:
            with open(self.rules_fn, 'wt', encoding = 'utf-8') as rules_f:
                json.dump([r.to_json() for r in self.rules], rules_f, indent=4, ensure_ascii=False)

    def save_as_rules(self):
        if self.rules:
            file = QtWidgets.QFileDialog.getSaveFileName(self, "Выберете файл")
            if file:
                if file[0] != '':
                    self.rules_fn = file[0]
                    self.save_rules()

    def load_text(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Pick a file")
        if file:
            if file[0] != '':
                self.text_fn = file[0]
                text = []
                with open(self.text_fn, 'rt', encoding = 'utf-8') as text_f:
                    for t in text_f:
                        text.append(t.strip())

                self.text_input_edit.clear()
                self.text_input_edit.setText('\n'.join(text))
        self.process()

    def save_text(self):
        if self.text_fn:
            with open(self.text_fn, 'wt', encoding = 'utf-8') as text_f:
                text_f.write(self.text_input_edit.toPlainText())        

    def save_as_text(self):
        file = QtWidgets.QFileDialog.getSaveFileName(self, "Pick a file")
        if file:
            if file[0] != '':
                self.text_fn = file[0]
                self.save_text()

    def exit(self):
        QtCore.QCoreApplication.instance().quit()


    def process(self):
        self.result = []
        for t in self.text_input_edit.toPlainText().split('\n'):
            self.result.append(self.text_parser.parse(t, self.rules))
        self.result_list.clear()
        for r in self.result:
            self.result_list.addItem(r[0])

    def result_info(self):
        self.info = ResiltInfo(self.result[self.result_list.currentRow()][1])
        info_gm = self.info.frameGeometry()
        center = self.frameGeometry().center()
        info_gm.moveCenter(center)
        self.info.move(info_gm.topLeft())
        self.info.show()


    def rule_add(self):
        if not self.rules:
            return
        names = [r.name for r in self.rules]
        new_name_tmpl = 'Правило'
        idx = 0
        name = new_name_tmpl
        while name in names:
            idx += 1
            name = new_name_tmpl + ' %d'%(idx)
        self.rules.append(self.text_parser.Rule(name))
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(len(self.rules) - 1))

    def rule_remove(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 0:
            return
        del self.rules[idx]
        if len(self.rules) > 0:
            self._fill_rule_list()
            if idx >= len(self.rules):
                idx -= 1
            self.rule_list.setCurrentItem(self.rule_list.item(idx))

    def rule_up(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 1:
            return
        self.rules.insert(idx - 1, self.rules.pop(idx))
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(idx - 1))

    def rule_down(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 0 or idx >= len(self.rules) - 1:
            return
        self.rules.insert(idx + 1, self.rules.pop(idx))
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(idx + 1))

    def rule_parse(self):
        for r in self.rules:
            if r.text:
                r.tmpl = [self.text_parser.Template(t, self.text_parser.parse_rule(t.strip())) for t in r.text]
        self.rules_select()
        self.process()


    def rules_select(self):
        idx = self.rule_list.currentRow()
        if idx < 0:
            return
        res = ''
        for t in self.rules[idx].tmpl:
            if res != '':
                res += '<br>'
            color = ''
            if not t.handler:
                color = ' color="red"'
            res += '<font%s>%s</font>'%(color, t.text)
        self.rule_template_edit.setHtml(res)

    def rules_edit(self):
        self.rules[self.rule_list.currentRow()].name = self.rule_list.currentItem().text()

    def template_edit(self):
        self.rules[self.rule_list.currentRow()].text = [t.strip() for t in self.rule_template_edit.toPlainText().split('\n') if t.strip() != '']
