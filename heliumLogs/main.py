# -*- coding: utf-8 -*-

"""
Created on Sun 15:59:08 2020

@author: Witcher

Real-time analysis with GUI
"""

import sys
from datetime import datetime
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem,
    QFileDialog, QApplication, QComboBox, QLabel)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        self.initUI()
        # создание полей класса
        self.list_press1 = []
        self.list_press2 = []
        self.list_press3 = []
        self.list_temp = []
        self.list_level = []
        
    def initUI(self):
        # 'Add' buttons
        self.button_press1_add.clicked.connect(self.press1_add)
        self.button_press2_add.clicked.connect(self.press2_add)
        self.button_press3_add.clicked.connect(self.press3_add)
        self.button_level_add.clicked.connect(self.level_add)
        self.button_temp_add.clicked.connect(self.temp_add)
        # 'Clear' buttons
        self.button_press1_clear.clicked.connect(self.press1_clear)
        self.button_press2_clear.clicked.connect(self.press2_clear)
        self.button_press3_clear.clicked.connect(self.press3_clear)
        self.button_level_clear.clicked.connect(self.level_clear)
        self.button_temp_clear.clicked.connect(self.temp_clear)
        
        # Run, stop, solve
        self.button_Run.clicked.connect(self.run_clicked)
        self.button_Stop.clicked.connect(self.stop_clicked)
        self.button_Solve.clicked.connect(self.solve_clicked)
        self.button_Save.clicked.connect(self.save_clicked)
        self.__Log('UI initialized successfully.')
        
    # метод записи отчетов о работе программы в лог
    def __Log(self, log):
        dt_string = datetime.now().strftime("%d.%m.%Y @ %H:%M:%S")
        self.editLog.appendPlainText(dt_string + ' - ' + log) 
    
    # метод записи в текстовое поле содержимого списка
    def fill_edit(self, edit, *strs):
        edit.clear()
        for i in strs:
            try:
                edit.appendPlainText(str(i))
            except:
                pass
    
    # слоты кнопок Run, Stop, Solve, Save
    def run_clicked(self):
        if self.button_Run.isChecked():
            self.execData()
        
    
    def stop_clicked(self):
        self.button_Run.setChecked(False)
        self.__Log('button_stop.clicked')
    
    def solve_clicked(self):
        self.button_Run.setChecked(False)
        self.__Log('button_solve.clicked')
    
    def save_clicked(self):
        self.button_Run.setChecked(False)
        self.__Log('button_save.clicked')
        
    
    
    # execData - main function
    def execData(self):
        self.progressBar.setValue(0)
        """
        logic
        """
        self.__Log('button_Run.isChecked')
        self.progressBar.setValue(100)
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        timeout = 2
        self.timer.setInterval(timeout*1000)
        self.timer.start()
        self.timer.timeout.connect(self.run_clicked)
    
    # слоты кнопок 'Add'
    def press1_add(self):
        self.list_press1.append('bonk')
        self.fill_edit(self.edit_press1, *self.list_press1)
        self.accessRun()
        self.__Log('press1_add.clicked')
        
    def press2_add(self):
        self.list_press2.append('bonk')
        self.fill_edit(self.edit_press2, *self.list_press2)
        self.accessRun()
        self.__Log('press2_add.clicked')
        
    def press3_add(self):
        self.list_press3.append('bonk')
        self.fill_edit(self.edit_press3, *self.list_press3)
        self.accessRun()
        self.__Log('press3_add.clicked')
        
    def temp_add(self):
        self.list_temp.append('bonk')
        self.fill_edit(self.edit_temp, *self.list_temp)
        self.accessRun()
        self.__Log('temp_add.clicked')
        
    def level_add(self):
        self.list_level.append('bonk')
        self.fill_edit(self.edit_level, *self.list_level)
        self.accessRun()
        self.__Log('level_add.clicked')
    
    # слоты кнопок 'Clear'
    def press1_clear(self):
        self.list_press1 = []
        self.fill_edit(self.edit_press1, *self.list_press1)
        self.accessRun()
        self.__Log('press1_clear.clicked')
        
    def press2_clear(self):
        self.list_press2 = []
        self.fill_edit(self.edit_press2, *self.list_press2)
        self.accessRun()
        self.__Log('press2_clear.clicked')
        
    def press3_clear(self):
        self.list_press3 = []
        self.fill_edit(self.edit_press3, *self.list_press3)
        self.accessRun()
        self.__Log('press3_clear.clicked')
        
    def temp_clear(self):
        self.list_temp = []
        self.fill_edit(self.edit_temp, *self.list_temp)
        self.accessRun()
        self.__Log('temp_clear.clicked')
        
    def level_clear(self):
        self.list_level = []
        self.fill_edit(self.edit_level, *self.list_level)
        self.accessRun()
        self.__Log('level_clear.clicked')



    # проверка готовности к запуску    
    def accessRun(self):
        a = self.list_press1 != []
        b = self.list_press2 != []
        c = self.list_press3 != []
        d = self.list_temp != []
        e = self.list_level != []
        if a and b and c and d and e:
            self.button_Run.setEnabled(True)
            self.button_Stop.setEnabled(True)
            self.button_Solve.setEnabled(True)
            return True
        else:
            self.button_Run.setEnabled(False)
            self.button_Stop.setEnabled(False)
            self.button_Solve.setEnabled(False)
            return False
    
         
    
def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
        
if __name__ == "__main__":
    main()