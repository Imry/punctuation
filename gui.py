#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json

from PyQt5 import QtWidgets, QtCore, QtGui

import ui_main
import ui_info

import parse


TABLE_DATA_EMPTY_FIELDS = 10


class ResiltInfo(QtWidgets.QWidget, ui_info.Ui_InfoForm):
    def __init__(self, data):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.info_table.resizeRowsToContents()
        self.info_table.setColumnCount(3)
        self.info_table.setHorizontalHeaderLabels(['Правило', 'Шаблон', 'Результат'])
        self.info_table.setRowCount(len(data))
        for row, item in enumerate(data):
            for column, field in enumerate(item):
                self.info_table.setItem(row, column, QtWidgets.QTableWidgetItem(field))
        self.info_table.adjustSize()
        self.info_table.horizontalHeader().setStretchLastSection(True)
        self.info_table.resizeColumnsToContents()

class Punctuator(QtWidgets.QMainWindow, ui_main.Ui_MainWindow):
    class DataModel(QtCore.QAbstractTableModel):
        def __init__(self, text, header, parent=None, *args):
            QtCore.QAbstractTableModel.__init__(self, parent, *args)
            self.text = text
            self.header = header
            self.parent = parent

        def rowCount(self, parent):
            return len(self.text) 

        def columnCount(self, parent):
            return len(self.header)

        def headerData(self, col, orientation, role):
            if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.header[col])
            return QtCore.QVariant()

        def setData(self, index, value, role):
            if index.isValid() and role == QtCore.Qt.EditRole:
                row = index.row()
                col = index.column()
                if col == 0 and row < len(self.text):
                    if isinstance(value, QtCore.QVariant):
                        value = value.toString().simplified()
                    self.text[row][0] = value
                    self.text[row][1] = self.parent.text_parser.parse(value, self.parent.rules)
                    self.dataChanged.emit(QtCore.QModelIndex().child(row, 1), QtCore.QModelIndex().child(row, 1), [QtCore.Qt.EditRole])
                    self.expand_data()
                    self.parent.table_data.resizeColumnToContents(0)
                    self.parent.btn_text_save.setEnabled(True)
                    self.parent.text_change = True

                    return True
            return False

        def data(self, index, role):
            if index.isValid():
                row = index.row()
                col = index.column()
                if col < len(self.header) and row < len(self.text):
                    if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
                        return self.text[row][col]
            return


        def flags(self, index):
            if index.column() == 0:
                return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        def removeRow(self, index):
            if 0 <= index < len(self.text):
                self.beginRemoveRows(QtCore.QModelIndex(), index, index)
                del self.text[index]
                self.endRemoveRows()

        def addRow(self, index, text):
            if 0 <= index < len(self.text):
                self.beginInsertRows(QtCore.QModelIndex(), index, index)
                self.text.insert(index, [text, '', []])
                self.endInsertRows()

        def expand_data(self):
            idx = len(self.text) - 1
            count = 0
            while idx >= 0:
                if self.text[idx][0] != '':
                    break
                count += 1
                idx -= 1
            if count < TABLE_DATA_EMPTY_FIELDS:
                self.beginInsertRows(QtCore.QModelIndex(), len(self.text), len(self.text) + TABLE_DATA_EMPTY_FIELDS - count - 1)
                for _ in range(TABLE_DATA_EMPTY_FIELDS - count):
                    self.text.append(['', '', []])
                self.endInsertRows()
            if count > TABLE_DATA_EMPTY_FIELDS:
                self.beginRemoveRows(QtCore.QModelIndex(), len(self.text) - count + TABLE_DATA_EMPTY_FIELDS, len(self.text) - 1)
                self.text = self.text[:len(self.text) - count + TABLE_DATA_EMPTY_FIELDS]
                self.endRemoveRows()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.text_parser = parse.TextParser()

        self.text = self.DataModel([], ['Текст', 'Результат'], self)
        self.text_fn = None
        self.text_change = False

        self.rules = []
        self.rules_fn = None
        self.rules_change = False

        self.info = None

        self.text.expand_data()
        self.table_data.setModel(self.text)
        hh = self.table_data.horizontalHeader()
        hh.setStretchLastSection(True)
        self.table_data.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self._connect_all()

        self._center()
        self.show()

        self.btn_text_save.setEnabled(False)
        self.btn_rule_save.setEnabled(False)


    def _center(self):
        fm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        center = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        fm.moveCenter(center)
        self.move(fm.topLeft())        

    def _connect_all(self):
        # menu 'file'
        self.action_rule_load.triggered.connect(self.rule_load)
        self.action_rule_save.triggered.connect(self.rule_save)
        self.action_rule_save_as.triggered.connect(self.rule_save_as)

        self.action_text_load.triggered.connect(self.text_load)
        self.action_text_save.triggered.connect(self.text_save)
        self.action_text_save_as.triggered.connect(self.text_save_as)

        self.action_exit.triggered.connect(self.exit)

        # menu 'rule'
        self.action_rule_add.triggered.connect(self.rule_add)
        self.action_rule_remove.triggered.connect(self.rule_remove)
        self.action_rule_up.triggered.connect(self.rule_up)
        self.action_rule_down.triggered.connect(self.rule_down)

        self.action_rule_apply.triggered.connect(self.rule_parse)
        self.action_rule_check.triggered.connect(self.rule_check)

        # menu 'settings'
        self.action_settings_font.triggered.connect(self.settings_font)
        self.action_settings_hotkey.triggered.connect(self.settings_hotkey)

        # 'text' toolbar
        self.btn_text_load.clicked.connect(self.text_load)
        self.btn_text_save.clicked.connect(self.text_save)
        self.btn_text_save_as.clicked.connect(self.text_save_as)

        # 'text' list
        self.table_data.doubleClicked.connect(self.result_info)
        # self.text.dataChanged.connect(self._process)
        QtWidgets.QShortcut(QtGui.QKeySequence('Del'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_remove)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+C'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_copy)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Ins'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_copy)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+X'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_cut)
        QtWidgets.QShortcut(QtGui.QKeySequence('Shift+Del'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_cut)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+V'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_paste)
        QtWidgets.QShortcut(QtGui.QKeySequence('Shift+Ins'), self.table_data, context=QtCore.Qt.WidgetShortcut).activated.connect(self.text_paste)

        # 'rule' toolbar
        self.btn_rule_apply.clicked.connect(self.rule_parse)

        self.btn_rule_add.clicked.connect(self.rule_add)
        self.btn_rule_remove.clicked.connect(self.rule_remove)
        self.btn_rule_up.clicked.connect(self.rule_up)
        self.btn_rule_down.clicked.connect(self.rule_down)

        self.btn_rule_load.clicked.connect(self.rule_load)
        self.btn_rule_save.clicked.connect(self.rule_save)
        self.btn_rule_save_as.clicked.connect(self.rule_save_as)

        QtWidgets.QShortcut(QtGui.QKeySequence('Insert'), self.rule_list, context=QtCore.Qt.WidgetShortcut).activated.connect(self.rule_add)
        QtWidgets.QShortcut(QtGui.QKeySequence('Del'), self.rule_list, context=QtCore.Qt.WidgetShortcut).activated.connect(self.rule_remove)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Up'), self.rule_list, context=QtCore.Qt.WidgetShortcut).activated.connect(self.rule_up)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Down'), self.rule_list, context=QtCore.Qt.WidgetShortcut).activated.connect(self.rule_down)

        # 'rule' list
        self.rule_list.itemClicked.connect(self.rules_select)
        self.rule_list.itemChanged.connect(self.rules_edit)

        # 'template' toolbar
        self.btn_rule_check.clicked.connect(self.rule_check)

        # 'template' edit
        self.rule_template_edit.textChanged.connect(self.template_edit)

    def text_load(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, caption='Выберете текстовый файл', filter='text (*.txt)')
        if file:
            if file[0] != '':
                self.text_fn = file[0]
                text = []
                with open(self.text_fn, 'rt', encoding = 'utf-8') as text_f:
                    text = []
                    for t in text_f:
                        text.append(t)
                    self.text.beginResetModel()
                    self.text.text.clear()
                    self.text.endResetModel()
                    self.text.beginInsertRows(QtCore.QModelIndex(), 0, len(text) - 1)
                    for t in text:
                        self.text.text.append([t.strip(), '', []])
                    self.text.endInsertRows()
                    self.text.expand_data()
                    s = len(self.text.text)
                    self.text.dataChanged.emit(QtCore.QModelIndex().child(s, 0), QtCore.QModelIndex().child(s, 1), [QtCore.Qt.EditRole])
                    # self.text.submit()
                    self.table_data.resizeColumnToContents(0)
                    self._process()
                    self.btn_text_save.setEnabled(False)
                    self.text_change = False


    def _get_file_fn(self, caption, flt):
        file = QtWidgets.QFileDialog.getSaveFileName(self, caption=caption, filter=flt)
        if file:
            if file[0] != '':
                return file[0]

    def _get_text_fn(self):
        self.text_fn = self._get_file_fn('Выберете файл для текста', 'text (*.txt)')

    def _get_rules_fn(self):
        self.rules_fn = self._get_file_fn('Выберете файл правил', 'JSON (*.json)')

    def text_save(self):
        if not self.text_fn:
            self._get_text_fn()
        if self.text_fn and self.text:
            with open(self.text_fn, 'wt', encoding = 'utf-8') as text_f:
                text = '\n'.join([t[0] for t in self.text.text]).strip()
                text_f.write(text)
                self.btn_text_save.setEnabled(False)
                self.text_change = False

    def text_save_as(self):
        self._get_text_fn()
        self.text_save()

    def rule_load(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, caption='Выберете файл правил', filter='JSON (*.json)')
        if file:
            if file[0] != '':
                self.rules_fn = file[0]
                with open(self.rules_fn, 'rt', encoding = 'utf-8') as rules_f:
                    self.rules = [self.text_parser.Rule(r['name'], text = [t for t in r['text']], changed = True) for r in json.load(rules_f)]
                    self.rules_change = False
                    self.btn_rule_save.setEnabled(False)
                    self.rule_parse()
                    self._fill_rule_list()
                    self.rule_list.setCurrentItem(self.rule_list.item(0))
                    self.rules_select()
                    self._process()

    def rule_save(self):
        if not self.rules_fn:
            self._get_rules_fn()
        if self.rules_fn and self.rules:
            with open(self.rules_fn, 'wt', encoding = 'utf-8') as rules_f:
                json.dump([r.to_json() for r in self.rules], rules_f, indent=4, ensure_ascii=False, sort_keys=False)
                self.btn_rule_save.setEnabled(False)
                self.rules_change = False

    def rule_save_as(self):
        self._get_rules_fn()
        self.rules_save()

    def _fill_rule_list(self):
        if self.rules != None:
            self.rule_list.clear()
            for r in self.rules:
                i = QtWidgets.QListWidgetItem(r.name)
                i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)
                self.rule_list.addItem(i)
                # self.rule_list.addItem(QtWidgets.QListWidgetItem(r.name).setFlags(i.flags() | QtCore.Qt.ItemIsEditable))

    def closeEvent(self, event):
        self.exit()

    def _save_data(self, flag, question, handler):
        if flag:
            reply = QtWidgets.QMessageBox.question(self, 'Внимание', 
                question, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                handler()            
                return True
            elif reply == QtWidgets.QMessageBox.Cancel:
                return False
            else:
                return True

    def exit(self):
        if not self._save_data(self.text_change, 'Изменения в тексте не сохранены. Сохранить?', self.text_save):
            return
        if not self._save_data(self.rules_change, 'Изменения в правилах не сохранены. Сохранить?', self.rule_save):
            return        
        QtCore.QCoreApplication.instance().quit()

    def settings_font(self):
        None

    def settings_hotkey(self):
        None

    def _process(self):
        for t in self.text.text:
            pr = self.text_parser.parse(t[0], self.rules)
            t[1:] = pr[0:]
        self.text.dataChanged.emit(QtCore.QModelIndex().child(0, 1), QtCore.QModelIndex().child(len(self.text.text), 1), [QtCore.Qt.DisplayRole])

    def _text_get_selected(self):
        return set([i.row() for i in self.table_data.selectedIndexes()])

    def text_cut(self):
        self.text_copy()
        self.text_remove()
        self.btn_text_save.setEnabled(True)
        self.text_change = True

    def text_copy(self):
        selected = self._text_get_selected()
        text = '\n'.join([self.text.text[i][0] for i in selected]).strip()
        # text = ''
        # for i in selected:
        #     text += '%s\n'%(self.text.text[i][0])
        # text = text.strip()
        QtWidgets.QApplication.clipboard().setText(text)

    def text_paste(self):
        text = QtWidgets.QApplication.clipboard().text().split('\n')
        index = sorted(self._text_get_selected())[0]
        for i, t in enumerate(text):
            self.text.addRow(i + index, t)
        self.table_data.resizeColumnToContents(0)
        self._process()
        self.text.dataChanged.emit(QtCore.QModelIndex().child(index, 0), QtCore.QModelIndex().child(index + len(text), 1), [QtCore.Qt.EditRole])
        self.btn_text_save.setEnabled(True)
        self.text_change = True

    def text_remove(self):
        selected = self._text_get_selected()
        first_selected = sorted(selected)[0]
        while(len(selected)):
            self.text.removeRow(selected.pop())
            selected = self._text_get_selected()
        self.text.expand_data()
        self.table_data.selectionModel().select(QtCore.QModelIndex().child(first_selected, 0), QtCore.QItemSelectionModel.Select)
        self.btn_text_save.setEnabled(True)
        self.text_change = True

    def result_info(self, index):
        col = index.column()
        if col != 1:
            return
        data = self.text.text[index.row()][2]
        if data:
            self.info = ResiltInfo(data)
            info_gm = self.info.frameGeometry()
            center = self.frameGeometry().center()
            info_gm.moveCenter(center)
            self.info.move(info_gm.topLeft())
            self.info.show()

    def rule_add(self):
        if not self.rules:
            self.rules = []
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
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True

    def rule_remove(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 0 or idx >= len(self.rules):
            return
        del self.rules[idx]
        if idx >= len(self.rules):
            idx -= 1
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(idx))
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True

    def rule_up(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 1:
            return
        self.rules.insert(idx - 1, self.rules.pop(idx))
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(idx - 1))
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True

    def rule_down(self):
        if not self.rules:
            return
        idx = self.rule_list.currentRow()
        if idx < 0 or idx >= len(self.rules) - 1:
            return
        self.rules.insert(idx + 1, self.rules.pop(idx))
        self._fill_rule_list()
        self.rule_list.setCurrentItem(self.rule_list.item(idx + 1))
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True

    def _rule_parse(self, rule):
        if rule.text and rule.changed:
            rule.tmpl = [self.text_parser.Template(t, self.text_parser.parse_rule(t.strip())) for t in rule.text]
            rule.changed = False
        return rule

    def rule_parse(self):
        if not self.rules:
            return
        for r in self.rules:
            self._rule_parse(r)
        self.rules_select()
        self._process()

    def _templates_show(self, rule):
        res = ''
        for t in rule.tmpl:
            if res != '':
                res += '<br>'
            color = ''
            if not t.handler:
                color = ' color="red"'
            res += '<font%s>%s</font>'%(color, t.text)
        self.rule_template_edit.setHtml(res)

    def rules_select(self):
        idx = self.rule_list.currentRow()
        if idx < 0 or idx >= len(self.rules):
            return

        self._is_select_show = True
        self._templates_show(self._rule_parse(self.rules[idx]))
        self._is_select_show = False
        # rule = self.rules[idx]
        # self._rule_parse(rule)
        # self._templates_show(rule)

    def rules_edit(self):
        self.rules[self.rule_list.currentRow()].name = self.rule_list.currentItem().text()
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True

    def rule_check(self):
        idx = self.rule_list.currentRow()
        if 0 <= idx < len(self.rules):
            self._rule_parse(self.rules[idx])
            self.rules_select()

    def template_edit(self):
        if self._is_select_show:
            return
        self.rules[self.rule_list.currentRow()].text = [t.strip() for t in self.rule_template_edit.toPlainText().split('\n') if t.strip() != '']
        self.rules[self.rule_list.currentRow()].changed = True
        self.btn_rule_save.setEnabled(True)
        self.rules_change = True
