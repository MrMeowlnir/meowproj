# -*- coding: utf-8 -*-

"""
Created on Feb 15, 2021

@author: MrMeowlnir

Create full database of experimental data with GUI
"""

import sys
from datetime import datetime
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem,
    QFileDialog, QApplication, QComboBox, QLabel)

""" функция склеивания даты и времени"""
def dateConcat(df):
    dataframe = df
    dataframe["Date/Time"] = pd.to_datetime(dataframe['Date'] + " " + dataframe['Time'],
                                 format = '%d.%m.%Y %H:%M:%S', 
                                 exact = False)
    dataframe.drop(['Time', 'Date'], axis=1, inplace=True)
    return dataframe

""" Класс Лог Давления"""
class Pressure():
    def __init__(self, fnames = ''):
        if fnames == '':
            self.fnames = []
        else:
            self.fnames = fnames
            
    def set_fnames(self):
        fname = QFileDialog.getOpenFileName(filter = 'Text Files (*.txt)')[0]
        if fname != '':
            self.fnames = [fname]
        else:
            self.fnames = []
            
    def GetFNames(self):
        return self.fnames
    
    def ClearFNames(self):
        self.fnames = []
        return 0
    
    def AddFName(self):
        fname = QFileDialog.getOpenFileName(filter = 'Text Files (*.txt)')[0]
        if fname != '':
            self.fnames.append(fname)
    
    def GetDataFrame(self):
        while self.fnames == [] or self.fnames == '':
            self.set_fnames()
        
        
        names = ["Addr", "Command", "Pressure", "Time", "Date"]
        result = pd.DataFrame()
        parser_cond = {"Addr" : "Addr:", "Command" : "Command: ", "Pressure" : "Pressure: ", 
                   "Time" : "Time: ", "Date" : "Date: "}
        for filename in self.fnames:
            try:
                dataframe = pd.read_csv(filename, skiprows = 2, header=None, delimiter=';', names=names)
                for name, parse in parser_cond.items():
                    dataframe[name] = dataframe[name].map(lambda x: x.lstrip(parse).rstrip(" kPa"))

                dataframe = dateConcat(dataframe)
                oldname = "Pressure"
                newname = 'Pressure' + "_" + dataframe["Addr"][0] + ", kPa"
                dataframe.rename(columns={oldname : newname}, inplace=True)
                dataframe[newname] = dataframe[newname].map(lambda x: float(x.replace(',','.')))
                dataframe.drop(['Addr', 'Command'], axis=1, inplace=True)
                result = result.append(dataframe, ignore_index = True)          
            except:
                pass
        
        return result
    
""" Класс Главное Окно"""
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        self.initUI()
        # создание полей класса
        self.Result_Table = pd.DataFrame()
        self.log_press1 = Pressure()
        self.log_press2 = Pressure()
        self.log_press3 = Pressure()
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
        fname = QFileDialog.getSaveFileName(self, 'Save File', filter='Excel files (*.xlsx)')[0]
        if '.xlsx' not in fname:
            fname = fname + '.xlsx'
        self.edit_result.setText('Saved: ' + fname)
        
        if (fname[0] != '.'):
            self.union.to_excel(fname)
        self.__Log('button_save.clicked')
        
    def FillTable(self, Result_Table, tableWidget):
        col_count = len(Result_Table.columns)
        row_count = len(Result_Table.index)
        tableWidget.setColumnCount(col_count)
        tableWidget.setRowCount(row_count)
        tableWidget.setHorizontalHeaderLabels(Result_Table.columns)
        for i in range(row_count):
            for j in range(col_count):
                tableWidget.setItem(i,j, QTableWidgetItem(str(Result_Table.iat[i, j])))
    
    # execData - main function
    def execData(self):
        self.progressBar.setValue(0)
        """
        logic
        """
        p1 = self.log_press1.GetDataFrame()
        self.progressBar.setValue(10)
        p2 = self.log_press2.GetDataFrame()
        self.progressBar.setValue(20)
        p3 = self.log_press3.GetDataFrame()
        self.progressBar.setValue(30)
        p1p2 = pd.merge(p1, p2, on="Date/Time", how="outer")
        self.progressBar.setValue(40)
        p = pd.merge(p1p2, p3, on="Date/Time", how="outer")
        self.progressBar.setValue(50)
   
        self.union = p
        cols = self.union.columns.tolist()
        cols = cols[1:2]+cols[:1]+cols[2:]
        self.union = self.union[cols]
        self.union.sort_values('Date/Time', inplace = True)
        self.__Log(str(len(self.union)))
        self.progressBar.setValue(70)
        
        if len(self.union) > 0:
            self.button_Save.setEnabled(True)
            self.FillTable(self.union, self.table_result)
        else:
            self.button_Save.setEnabled(False)
        
        self.progressBar.setValue(100)
        
        # Setup a timer to trigger runbutton.
        self.timer = QtCore.QTimer()
        timeout = 2
        self.timer.setInterval(timeout*1000)
        self.timer.start()
        self.timer.timeout.connect(self.run_clicked)
    
    # слоты кнопок 'Add'
    def press1_add(self):
        self.log_press1.AddFName()
        self.fill_edit(self.edit_press1, *self.log_press1.GetFNames())
        self.accessRun()
        self.__Log('press1_add.clicked')
        
    def press2_add(self):
        self.log_press2.AddFName()
        self.fill_edit(self.edit_press2, *self.log_press2.GetFNames())
        self.accessRun()
        self.__Log('press2_add.clicked')
        
    def press3_add(self):
        self.log_press3.AddFName()
        self.fill_edit(self.edit_press3, *self.log_press3.GetFNames())
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
        self.log_press1.ClearFNames()
        self.fill_edit(self.edit_press1, *self.log_press1.GetFNames())
        self.accessRun()
        self.__Log('press1_clear.clicked')
        
    def press2_clear(self):
        self.log_press2.ClearFNames()
        self.fill_edit(self.edit_press2, *self.log_press2.GetFNames())
        self.accessRun()
        self.__Log('press2_clear.clicked')
        
    def press3_clear(self):
        self.log_press3.ClearFNames()
        self.fill_edit(self.edit_press3, *self.log_press3.GetFNames())
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
        a = self.log_press1.GetFNames() != []
        b = self.log_press2.GetFNames() != []
        c = self.log_press3.GetFNames() != []
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