# -*- coding: utf-8 -*-

"""
Created on Feb 15, 2021

@author: MrMeowlnir

Create full database of experimental data with GUI
"""

import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem,
    QFileDialog, QApplication)

""" функция склеивания даты и времени"""
def dateConcat(df):
    dataframe = df
    dataframe["Date/Time"] = pd.to_datetime(dataframe['Date'] + " " + dataframe['Time'],
                                 format = '%d.%m.%Y %H:%M:%S', 
                                 exact = False)
    dataframe.drop(['Time', 'Date'], axis=1, inplace=True)
    return dataframe


def replace_float(x):
    if isinstance(x, str):
        return float(x.replace(',','.'))
    else:
        return x

def fpress(x):
    if 'MPa' in x:
        return np.round(1000*float(x.rstrip(' MPa')), 3)
    elif 'kPa' in x:
        return np.round(float(x.rstrip(' kPa')), 3)
    return 0

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

""" Родительский класс ЛогФайл"""
class LogFile():
    def __init__(self, fnames = ''):
        if fnames == '':
            self.fnames = []
        else:
            self.fnames = fnames
            
    def set_fnames(self):
        fname = QFileDialog.getOpenFileName()[0]
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
        fname = QFileDialog.getOpenFileName()[0]
        if fname != '':
            self.fnames.append(fname)
    
    def AddFolder(self):
        Folder_Name = QFileDialog.getExistingDirectory()
        for dirs, folders, files in os.walk(Folder_Name):
            for file in files: 
                self.fnames.append(os.path.join(dirs,file))

""" Класс Лог Давления"""
class Pressure(LogFile):
    def __init__(self):
        super().__init__()
    
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
                    dataframe[name] = dataframe[name].map(lambda x: x.lstrip(parse))

                dataframe = dateConcat(dataframe)
                oldname = "Pressure"
                newname = 'Pressure' + "_" + dataframe["Addr"][0] + ", kPa"
                dataframe.rename(columns={oldname : newname}, inplace=True)
                dataframe[newname] = dataframe[newname].map(lambda x: x.replace(',','.'))
                dataframe[newname] = dataframe[newname].map(lambda x: fpress(x))
                dataframe.drop(['Addr', 'Command'], axis=1, inplace=True)
                result = result.append(dataframe, ignore_index = True)          
            except:
                pass
        
        return result

class AtmPressure(LogFile):
    def __init__(self):
        super().__init__()
    
    def GetDataFrame(self):
        while self.fnames == [] or self.fnames == '':
            self.set_fnames()
        
        names = ["Date/Time", "Atm.Pressure, kPa"]
        result = pd.DataFrame()
        for filename in self.fnames:
            try:
                xl = pd.ExcelFile(filename)
                dataframe = xl.parse(xl.sheet_names[0], header=None)
                dataframe.columns = names
                dataframe["Date/Time"] = pd.to_datetime(dataframe["Date/Time"],
                                 format = '%d.%m.%Y %H:%M:%S', 
                                 exact = False)
                result = result.append(dataframe, ignore_index = True)          
            except:
                pass
        
        return result

""" Класс температурного лога"""
class Temperature(LogFile):
    def __init__(self):
        super().__init__()
    
    def GetDataFrame(self):
        while self.fnames == [] or self.fnames == '':
            self.set_fnames()
        
        
        names1 = ["Date/Time", "T1, K", "T2, K", "T3, K", "T4, K", "T5, K", "T6, K", "T7, K","T8, K"]
        names2 = ["Date/Time", "T_rot1, K", "T_rot2, K"]
        result = pd.DataFrame()
        for filename in self.fnames:
            try:
                dataframe = pd.read_csv(filename, delimiter='\t')
                if len(dataframe.columns) == 9:
                    dataframe.columns = names1
                    
                elif len(dataframe.columns) == 3:
                    dataframe.columns = names2
                    
                    
                dataframe["Date/Time"] = pd.to_datetime(dataframe["Date/Time"],
                                 format = '%d.%m.%Y %H:%M:%S', 
                                 exact = False)
                for i in dataframe.columns [1:]:
                    dataframe[i] = dataframe[i].map(lambda x: replace_float(x))
                result = result.append(dataframe, ignore_index = True)          
            except:
                pass
        
        return result


""" Класс лога уровня"""
class Level(LogFile):
    def __init__(self):
        super().__init__()
    
    def GetDataFrame(self):
        while self.fnames == [] or self.fnames == '':
            self.set_fnames()
        
        names = ["Date/Time", "Level, cm"]
        result = pd.DataFrame()
        for filename in self.fnames:
            try:
                dataframe = pd.read_csv(filename, delimiter='\t', names=names)
                dataframe["Level, cm"] = dataframe["Level, cm"].map(lambda x: float(x.rstrip(" cm").replace(',','.')))
                dataframe["Date/Time"] = pd.to_datetime(dataframe["Date/Time"],
                                 format = '%d.%m.%Y  %H:%M:%S', 
                                 exact = False)
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
        self.log_atmpress = AtmPressure()
        self.log_temp = Temperature()
        self.log_temp2 = Temperature()
        self.log_level = Level()
        
    def initUI(self):
        # 'Add' buttons
        self.button_press1_add.clicked.connect(self.press1_add)
        self.button_press2_add.clicked.connect(self.press2_add)
        self.button_press3_add.clicked.connect(self.press3_add)
        self.button_level_add.clicked.connect(self.level_add)
        self.button_temp_add.clicked.connect(self.temp_add)
        self.button_temp2_add.clicked.connect(self.temp2_add)
        self.button_pressatm_open.clicked.connect(self.atmpress_open)
        # 'Clear' buttons
        self.button_press1_clear.clicked.connect(self.press1_clear)
        self.button_press2_clear.clicked.connect(self.press2_clear)
        self.button_press3_clear.clicked.connect(self.press3_clear)
        self.button_level_clear.clicked.connect(self.level_clear)
        self.button_temp_clear.clicked.connect(self.temp_clear)
        self.button_temp2_clear.clicked.connect(self.temp2_clear)
        
        # 'AddFolder' buttons
        self.button_press1_addfolder.clicked.connect(self.press1_addfolder)
        self.button_press2_addfolder.clicked.connect(self.press2_addfolder)
        self.button_press3_addfolder.clicked.connect(self.press3_addfolder)
        self.button_level_addfolder.clicked.connect(self.level_addfolder)
        self.button_temp_addfolder.clicked.connect(self.temp_addfolder)
        self.button_temp2_addfolder.clicked.connect(self.temp2_addfolder)
        
        # Run, stop, solve
        self.button_Run.clicked.connect(self.run_clicked)
        self.button_Stop.clicked.connect(self.stop_clicked)
        self.button_Solve.clicked.connect(self.solve_clicked)
        
        # Save buttons
        self.button_Save.clicked.connect(self.save_clicked)
        self.button_save_dropna.clicked.connect(self.save_dropna)
        self.button_save_split.clicked.connect(self.save_split)
        self.button_save_slice.clicked.connect(self.save_slice)
        self.__Log('UI initialized successfully.')
        
        # Menu 
        
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
        self.execData()
        self.__Log('button_solve.clicked')
    
    def save_clicked(self):
        self.button_Run.setChecked(False)
        fname = QFileDialog.getSaveFileName(self, 'Save File', filter='Excel files (*.xlsx)')[0]
        if '.xlsx' not in fname:
            fname = fname + '.xlsx'
        self.edit_save.setText('Saved: ' + fname)
        if (fname[0] != '.'):
            self.union.to_excel(fname)
        self.__Log('button_save.clicked')
        
    def save_dropna(self):
        self.button_Run.setChecked(False)
        fname = QFileDialog.getSaveFileName(self, 'Save File', filter='Excel files (*.xlsx)')[0]
        if '.xlsx' not in fname:
            fname = fname + '.xlsx'
        self.edit_save.setText('Saved: ' + fname)
        if (fname[0] != '.'):
            self.union.dropna(subset = self.union.columns[:-1]).to_excel(fname)
        self.__Log('button_save_dropna.clicked')
    
    def save_split(self):
        self.button_Run.setChecked(False)
        fname = QFileDialog.getSaveFileName(self, 'Save File', filter='Excel files (*.xlsx)')[0]
        if '.xlsx' not in fname:
            fname = fname + '.xlsx'
        self.edit_save.setText('Saved: ' + fname)
        if (fname[0] != '.'):
            xl = pd.ExcelWriter(fname, engine = 'xlsxwriter')
            self.p.to_excel(xl, sheet_name = 'P')
            self.t.to_excel(xl, sheet_name = 'T')
            self.t2.to_excel(xl, sheet_name = 'T2')
            self.l.to_excel(xl, sheet_name = 'L')
            xl.save()
        self.__Log('button_save_split.clicked')
        
        
    def save_slice(self):
        self.button_Run.setChecked(False)
        self.__Log('button_save_slice.clicked')
        self.progressBar.setValue(0)
        try:
            tmp_time_from = datetime.strptime(self.edit_from.text(), '%d.%m.%Y %H:%M')
            self.__Log(datetime.strftime(tmp_time_from, '%d.%m.%Y %H:%M'))
            tmp_time_to = datetime.strptime(self.edit_to.text(), '%d.%m.%Y %H:%M')
            self.__Log(datetime.strftime(tmp_time_to, '%d.%m.%Y %H:%M'))
        except:
            tmp_time_from = 0
            tmp_time_to = 0
            self.__Log('Exception')
            
        self.progressBar.setValue(10)
        if (isinstance(tmp_time_from, datetime) and
                isinstance(tmp_time_to, datetime)):
            self.__Log('isinctance')
            time_from = min([tmp_time_from, tmp_time_to])
            time_to = max([tmp_time_from, tmp_time_to])
            self.__Log('Min datetime' + datetime.strftime(time_from, '%d.%m.%Y %H:%M'))
            self.__Log('Max datetime' + datetime.strftime(time_to, '%d.%m.%Y %H:%M'))
            
            p_slice = self.p[self.p['Date/Time'] >= time_from].dropna().reset_index(drop = True)
            p_slice = p_slice[p_slice['Date/Time'] <= time_to].dropna().reset_index(drop = True)
            self.__Log('len(p_slice) = ' + str(len(p_slice)))
            t_slice = self.t[self.t['Date/Time'] >= time_from].dropna().reset_index(drop = True)
            t_slice = t_slice[t_slice['Date/Time'] <= time_to].dropna().reset_index(drop = True)
            self.__Log('len(t_slice) = ' + str(len(t_slice)))
            t2_slice = self.t2[self.t2['Date/Time'] >= time_from].dropna().reset_index(drop = True)
            t2_slice = t2_slice[t2_slice['Date/Time'] <= time_to].dropna().reset_index(drop = True)
            self.__Log('len(t2_slice) = ' + str(len(t2_slice)))
            l_slice = self.l[self.l['Date/Time'] >= time_from].dropna().reset_index(drop = True)
            l_slice = l_slice[l_slice['Date/Time'] <= time_to].dropna().reset_index(drop = True)
            self.__Log('len(l_slice) = ' + str(len(l_slice)))
            union_slice = self.union[self.union['Date/Time'] >= time_from].dropna(subset = self.union.columns[:-3]).reset_index(drop = True)
            union_slice = union_slice[union_slice['Date/Time'] <= time_to].dropna(subset = self.union.columns[:-3]).reset_index(drop = True)
            self.__Log('len(union_slice) = ' + str(len(union_slice)))
            self.progressBar.setValue(20)
            
            model = PandasModel(union_slice)
            self.table_slice.setModel(model)
            self.progressBar.setValue(50)
            
            fname = QFileDialog.getSaveFileName(self, 'Save File', filter='Excel files (*.xlsx)')[0]
            self.progressBar.setValue(55)
            if '.xlsx' not in fname:
                fname = fname + '.xlsx'
            
            if (fname[0] != '.'):
                xl = pd.ExcelWriter(fname, engine = 'xlsxwriter')
                p_slice.to_excel(xl, sheet_name = 'P')
                self.progressBar.setValue(60)
                t_slice.to_excel(xl, sheet_name = 'T')
                self.progressBar.setValue(70)
                t2_slice.to_excel(xl, sheet_name = 'T2')
                self.progressBar.setValue(80)
                l_slice.to_excel(xl, sheet_name = 'L')
                self.progressBar.setValue(90)
                union_slice.to_excel(xl, sheet_name = 'Full')
                self.progressBar.setValue(95)
                xl.save()
                self.edit_save_slice.setText('Saved: ' + fname)
            else:
                self.edit_save_slice.setText('Wrong Filename: ' + fname)
        else:
            self.__Log('NOT isinctance')    
                
        self.progressBar.setValue(100)        
        self.__Log('button_save_slice.done')
        
        
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
        self.__Log('len(p1) = ' + str(len(p1)))
        self.progressBar.setValue(10)
        p2 = self.log_press2.GetDataFrame()
        self.__Log('len(p2) = ' + str(len(p2)))
        self.progressBar.setValue(20)
        p3 = self.log_press3.GetDataFrame()
        self.__Log('len(p3) = ' + str(len(p3)))
        self.progressBar.setValue(30)
        patm = self.log_atmpress.GetDataFrame()
        self.__Log('len(patm) = ' + str(len(patm)))
        self.progressBar.setValue(33)
        t = self.log_temp.GetDataFrame()
        self.__Log('len(t) = ' + str(len(t)))
        if len(t) > 0:
            self.t = t
        self.progressBar.setValue(35)
        t2 = self.log_temp2.GetDataFrame()
        self.__Log('len(t2) = ' + str(len(t2)))
        if len(t2) > 0:
            self.t2 = t2
        self.progressBar.setValue(38)
        l = self.log_level.GetDataFrame()
        self.__Log('len(l) = ' + str(len(l)))
        if len(l) > 0:
            self.l = l
        self.progressBar.setValue(40)
        p1p2 = pd.merge(p1, p2, on="Date/Time", how="outer")
        self.progressBar.setValue(45)
        p1p2p3 = pd.merge(p1p2, p3, on="Date/Time", how="outer")
        self.progressBar.setValue(50)
        p = pd.merge(p1p2p3, patm, on="Date/Time", how="outer")
        self.progressBar.setValue(51)
        p.sort_values('Date/Time', inplace = True)
        p.reset_index(drop = True, inplace = True)
        self.progressBar.setValue(53)
        
        cols = p.columns.tolist()
        cols = cols[1:2]+cols[:1]+cols[2:]
        p = p[cols]
        p.interpolate(inplace = True)
        self.progressBar.setValue(54)
        self.__Log(p.columns[4])
        p.dropna(inplace = True)
        self.progressBar.setValue(55)
        for i in p.columns[1:-1]:
            self.__Log(str(i) + ' (abs)')
            p[str(i) + ' (abs)'] = p[i] + p[p.columns[4]]
        p = p.round(3)
        if len(p) > 0:
            self.p = p
        self.progressBar.setValue(56)
        pt = pd.merge(p, t, on="Date/Time", how="outer")
        self.progressBar.setValue(57)
        pt2 = pd.merge(pt, t2, on="Date/Time", how="outer")
        self.progressBar.setValue(58)
        self.union = pd.merge(pt2, l, on="Date/Time", how="outer")
        self.progressBar.setValue(60)
        self.union.sort_values('Date/Time', inplace = True)
        self.progressBar.setValue(70)
        """
        TODO:
            Fill graphics
            1. Pressure
            2. Temperature
            3. Level
        """
        if len(self.union) > 0:
            self.button_Save.setEnabled(True)
            self.button_save_dropna.setEnabled(True)
            self.button_save_split.setEnabled(True)
            self.button_save_slice.setEnabled(True)
            model = PandasModel(self.union)
            self.table_result.setModel(model)
        else:
            self.button_Save.setEnabled(False)
            self.button_save_dropna.setEnabled(False)
            self.button_save_split.setEnabled(False)
            self.button_save_slice.setEnabled(False)
        
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
    
    def atmpress_open(self):
        self.log_atmpress.ClearFNames()
        self.log_atmpress.AddFName()
        self.edit_pressatm.setText(self.log_atmpress.GetFNames()[0])
        self.accessRun()
        self.__Log('pressatm_open.clicked')
        
    def temp_add(self):
        self.log_temp.AddFName()
        self.fill_edit(self.edit_temp, *self.log_temp.GetFNames())
        self.accessRun()
        self.__Log('temp_add.clicked')
    
    def temp2_add(self):
        self.log_temp2.AddFName()
        self.fill_edit(self.edit_temp2, *self.log_temp2.GetFNames())
        self.accessRun()
        self.__Log('temp2_add.clicked')
        
    def level_add(self):
        self.log_level.AddFName()
        self.fill_edit(self.edit_level, *self.log_level.GetFNames())
        self.accessRun()
        self.__Log('level_add.clicked')
    
    # слоты кнопок 'Add Folder'
    def press1_addfolder(self):
        self.log_press1.AddFolder()
        self.fill_edit(self.edit_press1, *self.log_press1.GetFNames())
        self.accessRun()
        self.__Log('press1_addfolder.clicked')
        
    def press2_addfolder(self):
        self.log_press2.AddFolder()
        self.fill_edit(self.edit_press2, *self.log_press2.GetFNames())
        self.accessRun()
        self.__Log('press2_addfolder.clicked')
        
    def press3_addfolder(self):
        self.log_press3.AddFolder()
        self.fill_edit(self.edit_press3, *self.log_press3.GetFNames())
        self.accessRun()
        self.__Log('press3_addfolder.clicked')
        
    def temp_addfolder(self):
        self.log_temp.AddFolder()
        self.fill_edit(self.edit_temp, *self.log_temp.GetFNames())
        self.accessRun()
        self.__Log('temp_addfolder.clicked')
    
    def temp2_addfolder(self):
        self.log_temp2.AddFolder()
        self.fill_edit(self.edit_temp2, *self.log_temp2.GetFNames())
        self.accessRun()
        self.__Log('temp2_addfolder.clicked')
        
    def level_addfolder(self):
        self.log_level.AddFolder()
        self.fill_edit(self.edit_level, *self.log_level.GetFNames())
        self.accessRun()
        self.__Log('level_addfolder.clicked')
    
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
        self.log_temp.ClearFNames()
        self.fill_edit(self.edit_temp, *self.log_temp.GetFNames())
        self.accessRun()
        self.__Log('temp_clear.clicked')
    
    def temp2_clear(self):
        self.log_temp2.ClearFNames()
        self.fill_edit(self.edit_temp2, *self.log_temp2.GetFNames())
        self.accessRun()
        self.__Log('temp2_clear.clicked')
        
    def level_clear(self):
        self.log_level.ClearFNames()
        self.fill_edit(self.edit_level, *self.log_level.GetFNames())
        self.accessRun()
        self.__Log('level_clear.clicked')



    # проверка готовности к запуску    
    def accessRun(self):
        a = self.log_press1.GetFNames() != []
        b = self.log_press2.GetFNames() != []
        c = self.log_press3.GetFNames() != []
        d = self.log_temp.GetFNames() != []
        e = self.log_level.GetFNames() != []
        f = self.log_temp2.GetFNames() != []
        g = self.log_atmpress.GetFNames() != []
        if a and b and c and d and e and f and g:
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