# -*- coding: utf-8 -*-

# ondoing main libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# hiding possible warnings in the system
import warnings
warnings.filterwarnings('ignore')


#provides a creation of the pressure level dataframe with default delimeter from txt - ";"
#removes the top two extra lines from raw .txt files
#names columns from pattern "names"
def сreatePressureDt(filename):
    names = ["Addr", "Command", "Pressure", "Time", "Date"]
    return pd.read_csv(filename, skiprows = 2, header=None, delimiter=';', names=names)


#provides a creation of the temperature level dataframe with default delimeter from .xlsx - "\t" - "tabulation"
#names columns from pattern "names"
def сreateTempDt(filename):
    names = ["T1, K", "T2, K", "T3, K", "T4, K", "T5, K", "T6, K", "T7, K","T8, K","Date", "Time"]
    dataframe = pd.read_csv(filename, delimiter='\t', names=names)
    dataframe = dateConcat(dataframe)
    return dataframe


#provides a creation of the liquid helium level dataframe with default delimeter from .xlsx - "\t" - "tabulation"
#names columns from pattern "names"
#removes trash "cm" from data cells
def сreateLevelDt(filename):
    names = ["Level, cm", "Date", "Time"]
    dataframe = pd.read_csv(filename, delimiter='\t', names=names)
    dataframe["Level, cm"] = dataframe["Level, cm"].map(lambda x: float(x.rstrip(" cm")))
    dataframe = dateConcat(dataframe)
    return dataframe


#optional
#concatenate the "Data" and "Time" columns and reformat their into "datetime"
#drops extra "Time" and "Data"
def dateConcat(df):
    dataframe = df
    dataframe["Date/Time"] = pd.to_datetime(dataframe['Date'] + " " + dataframe['Time'],
                                 format = '%d.%m.%Y %H:%M:%S', 
                                 exact = False)
    dataframe.drop(['Time', 'Date'], axis=1, inplace=True)
    return dataframe
    
    
#removes trash words from cells according to pattern "parser_cond"
#removes extra milliseconds from "Time"
def pressureParser(df):
    dataframe = df
    parser_cond = {"Addr" : "Addr:", "Command" : "Command: ", "Pressure" : "Pressure: ", 
                   "Time" : "Time: ", "Date" : "Date: "}
    for name, parse in parser_cond.items():
        dataframe[name] = dataframe[name].map(lambda x: x.lstrip(parse).rstrip(" kPa"))

    dataframe = dateConcat(dataframe)


    return dataframe
    
#provides a complete name of column "Pressure" with considering gauge number (1,2 or 4) and unit of measure
def pressureDeterminator(df):
    dataframe = df
    oldname = "Pressure"
    newname = 'Pressure' + "_" + dataframe["Addr"][0] + ", kPa"
    dataframe.rename(columns={oldname : newname}, inplace=True)
    dataframe[newname] = dataframe[newname].map(lambda x: float(x.replace(',','.')))
    dataframe.drop(['Addr', 'Command'], axis=1, inplace=True)
    return dataframe
    
filename_pressure_1 = "data/Davlenie_start_otkachka_22.30_1.txt"
filename_pressure_2 = "data/Davlenie_start_otkachka_22.30_2.txt"
filename_pressure_4 = "data/Davlenie_start_otkachka_22.30_4.txt"


sensor_surf_1 = сreatePressureDt(filename_pressure_1)
sensor_surf_2 = сreatePressureDt(filename_pressure_2)
sensor_surf_4 = сreatePressureDt(filename_pressure_4)

sensor_surf_1 = pressureParser(sensor_surf_1)
sensor_surf_2 = pressureParser(sensor_surf_2)
sensor_surf_4 = pressureParser(sensor_surf_4)

sensor_surf_1 = pressureDeterminator(sensor_surf_1)
sensor_surf_2 = pressureDeterminator(sensor_surf_2)
sensor_surf_4 = pressureDeterminator(sensor_surf_4)

filename_temp = "data/TEMP_OTKACHKA_27.11.2020_22.39.xls"
filename_level = "data/LEVEL_OTKACHKA_27.11.2020_22.39.xls"

temp_surf = сreateTempDt(filename_temp)
level_surf = сreateLevelDt(filename_level)

union_pres_df = pd.merge(sensor_surf_1, sensor_surf_2, on="Date/Time", how="outer")
union_pres_df = pd.merge(union_pres_df, sensor_surf_4, on="Date/Time", how="outer")
union_pres_temp_df = pd.merge(union_pres_df, temp_surf, on="Date/Time", how="outer")
union = pd.merge(union_pres_temp_df, level_surf, on="Date/Time", how="outer")
union.sort_values('Date/Time', inplace = True)
cols = union.columns.tolist()
cols = cols[1:2]+cols[:1]+cols[2:]
union = union[cols]