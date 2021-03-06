

import os
import pprint
import random
import sys
import wx
from collections import OrderedDict
import time
import serial
from  datetime import datetime, timedelta
import json
from math import radians, cos, sin, asin, sqrt


from ScanMar_Serial_Tools import *

from ScanMar_Nmea import SMN_TOOLS
import wxSerialConfigDialog

from ScanMar_Window_Tools import *


class StatusVars(object):

    def __init__(self):

        self.initialize_vars()

    def initialize_vars(self):
        # Some state variables
        self.Serial_In = None
        self.LoggerRun = False
        self.MonitorRun = False
        self.OnBottom = False
        self.DataSource = None
        self.RT_source = False
        self.ARC_source = False

        # sued for elapsed time
        self.StartTime = -1



        self.comPort = ''




class DataVars(object):

    def __init__(self,parent,status_vars):
        self.initialize_vars()
        self.parent = parent
        self.status = status_vars
    def initialize_vars(self):

        self.JDict = OrderedDict()
        self.initialize_Jdict()

        self.dataDir = "C:\ScanMar_data"
        self.TripDataDir = ""

        self.ShipTripSet = {"YEAR": '1900', "SHIP": "TEL", "TRIP": "000", "SET": "000"}

        self.basename = self.make_base_name()

        self.WarpOut = '0'
        self.dist = 0.0
        self.elapsed = ""

        self.RAWFileName = None
        self.JSONFileName = None
        self.CSVFileName = None
        self.MISIONFileName = None

        self.RAW_fp = None
        self.JSON_fp = None
        self.CSV_fp = None
        self.TripLog_fp = None

    # JDICT valeues go into the csv file irregardlesss of if present; fields not in JDICT taht are found get appended
    #  to the end of the CSV records
    def initialize_Jdict(self):

        self.JDict["DATETIME"] = ""
        self.JDict["Lat"] = ""
        self.JDict["Long"] = ""
        self.JDict["LAT"] = ""
        self.JDict["LON"] = ""

        self.JDict["VTG_SPD"] = ""
        self.JDict["VTG_COG"] = ""
        self.JDict["DBS"] = ""

        self.JDict['DVTLAM_P'] = ""
        self.JDict['DVTLAM_R'] = ""
        self.JDict['DVTLAM_A'] = ""
        self.JDict['DVTLAM_B'] = ""
        self.JDict['DVTLAM_S'] = ""
        self.JDict['DVTLAS_P'] = ""
        self.JDict['DVTLAS_R'] = ""
        self.JDict['DVTLAS_A'] = ""
        self.JDict['DVTLAS_B'] = ""
        self.JDict['CVTLAM_S'] = ""
        self.JDict['TSP_X'] = ""
        self.JDict['TSP_Y'] = ""
        self.JDict['TLT_P'] = ""
        self.JDict['TLT_R'] = ""
        self.JDict['TLT_A'] = ""
        self.JDict['TLT_B'] = ""
        self.JDict['TS_H'] = ""
        self.JDict['TS_C'] = ""
        self.JDict['TS_O'] = ""
        self.JDict['TS_F'] = ""
        self.JDict['DPTM_D'] = ""   # Mapped DT to this one in the nmea parser for simplicity
        self.JDict['DPTM_T'] = ""   # BIO has this one
        self.JDict['WLPS'] = ""
        self.JDict['WLPO'] = ""
        self.JDict['WLSS'] = ""
        self.JDict['WLSO'] = ""
        self.JDict['WTP'] = ""
        self.JDict['WTS'] = ""
        self.JDict['WST'] = ""

# BIO Channels,  if preset they will auto add to the end of the Jdict
#       self.JDict['DPTM_D'] = ""
#       self.JDict['DPTM_T'] = ""
#       self.JDict'DVTLAS_T'] = ""
#       self.JDict['DVTLAM_D' = ""


    def make_base_name(self):
        return (self.ShipTripSet["SHIP"] + '-' + self.ShipTripSet["YEAR"] + '-' + self.ShipTripSet["TRIP"] + '-' +
                self.ShipTripSet["SET"])

    def make_SYTS(self, abasename):
        self.ShipTripSet["SHIP"], self.ShipTripSet["YEAR"], self.ShipTripSet["TRIP"], self.ShipTripSet[
            "SET"] = abasename.split('-')

    def set_FileNames(self):
            #        self.basename = self.make_base_name()
            #        self.disp_BaseName.Data_text.SetValue(str(self.BaseName))

            # directory to store recorded data and logs
        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        self.TripDataDir = self.dataDir + "\\" + self.basename[0:12]

            # directory to store recorded data and logs
        if not os.path.exists(self.TripDataDir):
            os.makedirs(self.TripDataDir)

        self.CSVFileName = self.TripDataDir + "\\" + self.basename + ".csv"
        self.RAWFileName = self.TripDataDir + "\\" + self.basename + ".pnmea"
        self.JSONFileName = self.TripDataDir + "\\" + self.basename + ".json"
        self.MISIONFileName = self.TripDataDir + "\\" + self.basename[0:12] + ".log"

    def increment_tow(self):
        new = self.ShipTripSet["SET"]
        new2 = int(new)
        new2a = new2 + 1
        new3 = str(new2a)
        new4 = new3.strip().zfill(3)
        #        print "SET",self.ShipTripSet["SET"],"|new=",new,"|new2=",new2,"|NEW3=",new3,"|new4=",new4,"|"
        #        if self.Confirm_Increment_dialogue(event,new4):
        self.ShipTripSet["SET"] = new4




    #        self.disp_BaseName.Data_text.SetForegroundColour()

    def mark_event(self, flag):

            #        dttm = str(datetime.now())
            dt = time.strftime('%Y-%m-%dT%H:%M:%S')

            #        if self.LoggerRun:
            if self.JDict["DPTM_D"] != '':
                msg = self.basename + ", " + self.JDict["DATETIME"] + ", " + "{:<10}".format(flag) + ", " + self.JDict[
                    "DBS"] + ", " + \
                      self.JDict["DPTM_D"]["measurement_val"] + ",  " + self.JDict["LAT"] + ", " + self.JDict["LON"]
            else:

                msg = self.basename + ", " + self.JDict["DATETIME"] + ", " + "{:<10}".format(flag) + ", " + self.JDict[
                    "DBS"] + ", " + \
                      "NULL" + ",  " + self.JDict["LAT"] + ", " + self.JDict["LON"]

            if flag == "WARPENTER":
                msg = msg + ', WARP= ' + self.WarpOut + ' m'

            screen_msg = msg
#            self.screen_log.AppendText('\n' + msg)

            #        else:
            #            msg ="  "+"{:<10}".format(flag)+", "+self.basename

            log_msg = dt + ", " + msg
            self.write_MissionLog(log_msg)

            if flag == "OUTWATER":
                msg = msg + ',' + self.elapsed + ',' + '{:>7.3}'.format(self.dist)

                msg = self.basename + ", " + self.JDict["DATETIME"] + ", " + "{:<10}".format(
                    "TOWINFO") + ", DURATION= " + \
                      self.elapsed + ', DISTANCE= ' + '{:>7.3}'.format(self.dist) + ' Nm, WARP= ' + self.WarpOut + ' m'
                self.parent.screen_log.AppendText('\n' + msg)
                log_msg = dt + ", " + msg
                if self.status.RT_source:  # dont write to files if in archive playback mode
                    self.write_MissionLog(log_msg)

            return (screen_msg)

    def haversine(self,lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2.) ** 2. + cos(lat1) * cos(lat2) * sin(dlon / 2.) ** 2.
        c = 2. * asin(sqrt(a))
        r = 6371.8  # Radius of earth in kilometers. Use 3959.87433 for miles
        km =  c * r
        nm= km/1.853
        return nm

    def save_file_dialog(self):
        """Save contents of output window."""
        #        CSV_outfilename = self.ShipTripSet["SHIP"]+self.ShipTripSet["YEAR"]+self.ShipTripSet["TRIP"]+'-'+self.ShipTripSet["SET"]
        CSV_outfilename = self.basename
        dlg = wx.FileDialog(None, "Save File As...", "", "", "ScanMar Proc log|*.csv|All Files|*",
                     wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
                CSV_outfilename = dlg.GetPath()
        dlg.Destroy()
        return (CSV_outfilename)

    def get_file_dialog(self):
        filename = None
        dialog = wx.FileDialog(None, "Choose File.", os.getcwd(), "", "ScanMar Raw Log|*.pnmea|All Files|*",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
        dialog.Destroy()
        return (filename)




#   ########  the various log files for data and events #################
    # I'm opening for append and unbuffered,, the append is to get around a repeat of a set#
    # and avoiding the 'do you want to over write or ... ' issue.. this is temp fix..
    # the unbuffered is CYA in case of crashes HOWEVER in python 3 the unbuffering required the file to be
    #  opened in binary mode causes a issue with the unicode meaning we have to encode the string to bytes
    # (it wont take a string argument)  hence the str(xx + yy +\n).encode()  type stuff
#   #####################################################################
    def write_Jdata(self,JDict):
        if self.JSON_fp == None:
            self.JSON_fp = open(self.JSONFileName, "a",0)

        X = json.dumps(JDict)
        self.JSON_fp.write(X+'\n')

    def write_CSVdata(self,JDict):
            flag = ""
            if self.CSV_fp ==None:
                self.CSV_fp= open(self.CSVFileName,"ab",0)

                for ele, val in JDict.items():
                    if ele == "DATETIME":
                        self.CSV_fp.write(str('{:>10}'.format('DATE') +','+ '{:>10}'.format('TIME')+',',).encode() )
                    elif ele == "LAT" or ele == "LON" :
                        self.CSV_fp.write(str('{:>10}'.format(ele+'_D')+','+'{:>10}'.format(ele+'_M')+',',).encode() )
                    else:
                        self.CSV_fp.write(str('{:>10}'.format(ele) + ',',).encode())
                    if isinstance(val, dict):
                            self.CSV_fp.write(str('{:>10}'.format('QF') +','+ '{:>10}'.format('VA')+',',).encode() )

#                self.CSVwriter = csv.writer(self.CSV_fp)
#                self.CSVwriter.writerow(JDict.keys())
                    flag = '{:>10}'.format("OnBottom")
            else:
                for ele, val in JDict.items():
                    if isinstance(val, dict):
                        for k, v in val.items():
                            self.CSV_fp.write(str('{:>10}'.format(v) + ',',).encode() )
                    else:
                        if ele == "DATETIME":
                            DT = val.split()
                            self.CSV_fp.write(str('{:>10}'.format(DT[0])+','+ '{:>10}'.format(DT[1])+',',).encode() )
                        elif  ele == "LAT"  or  ele == "LON":
                                L = val.split()
                                self.CSV_fp.write(str('{:>10}'.format(L[0]) + ',' + '{:>10}'.format(L[1]) + ',',).encode() )
                        else:
                            self.CSV_fp.write(str('{:>10}'.format(val) + ',',).encode() )
                flag = '{:>10}'.format('B') if self.status.OnBottom else '{:>10}'.format('W')

            self.CSV_fp.write(str(flag+'\n').encode())

#                self.CSVwriter.writerow(JDict.values())

    def write_RawData(self,Raw_String):
        if  self.RAW_fp == None:
            self.RAW_fp = open(self.RAWFileName,"ab",0)

        for zz in Raw_String :
            aline = str(Raw_String[zz]) + '\n'
            self.RAW_fp.write(aline.encode())



    def write_MissionLog(self, Event_String):
        if self.TripLog_fp == None:
            if os.path.isfile(self.MISIONFileName):
                self.TripLog_fp = open(self.MISIONFileName, "a")
            else:
                msg = "PC CLOCK           , SHIPTRIPSET    ,   FEED ClOCK,       EVENT     , ShipSND, NetSND,   LAT    ,    LONG,     INFO"

                self.TripLog_fp = open(self.MISIONFileName, "w")
                self.TripLog_fp.write(msg + '\n')

        self.TripLog_fp.write(Event_String + '\n')

    def close_files(self,Which):
        if Which == "ALL" :
            try:
                self.TripLog_fp.close()
                self.TripLog_fp = None
            except:
                self.TripLog_fp = None

        try:
            self.JSON_fp.close()
        except:
            pass
#        self.flash_status_message("CLOSING FILES...")

        try:
            self.RAW_fp.close()
        except:
            pass
        try:
            self.CSV_fp.close()
        except:
            pass


        self.JSON_fp = None
        self.RAW_fp = None
        self.CSV_fp = None


    def read_cfg(self,ser):
        try:
            with open('ScanMar.CFG', 'r') as fp:
                self.basename = fp.readline().rstrip()
                self.make_SYTS(self.basename)
                self.comPort = fp.readline().rstrip()
                ser.port = self.comPort
                commsettings = json.load(fp)
            try:
                ser.apply_settings(commsettings)
            except:
                ser.applySettingsDict(commsettings)    # pyserial pre v 3.0

#            fp.close()
        except:
            return (False)

        return (True)
#            self.set_default_com_cfg()


    def save_cfg(self,ser):
        try:
            comsettings = ser.get_settings()
        except:
            comsettings = ser.getSettingsDict()   # pyserial pre v 30.0

        with open('ScanMar.CFG', 'w') as fp:
            fp.write(self.basename)
            fp.write('\n')
            fp.write (ser.port)
            fp.write('\n')
            fp.write(json.dumps(comsettings))
        fp.close()


    def set_default_com_cfg(self,ser):  # Defaults as specified
        DEFAULT_COM = "COM3"
        DEFAULT_BAUD = 4800

        ser.port = DEFAULT_COM
        ser.baudrate = DEFAULT_BAUD
        ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        ser.parity = serial.PARITY_NONE  # set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        ser.timeout = 5  # timeout block read
        ser.xonxoff = True  # disable software flow control
        ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        ser.writeTimeout = 2  # timeout for write