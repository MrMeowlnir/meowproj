# -*- coding: utf-8 -*-

"""
Created on Sun 15:59:08 2020

@author: Witcher

Real-time analysis with GUI
"""

import sys
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
        
    def initUI(self):
        pass
    
def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
        
if __name__ == "__main__":
    main()