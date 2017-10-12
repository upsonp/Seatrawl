# -*- coding: utf-8 -*-

#WinBongo.py   D.Senciall  April 2015
# update June 1 2015 to fix incorrect presure conversion in realtime data reader
"""
Elements BASED ON CODE SAMPLE FROM: matplotlib-with-wxpython-guis by E.Bendersky
Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008

seee   http://eli.thegreenplace.net/2008/08/01/matplotlib-with-wxpython-guis/

Also
 Code Borrowed from seawater-3.3.2-py.27.egg for the density calcuations
"""
import os
import pprint
import random
import sys
import wx
from collections import OrderedDict
import time
import serial
import datetime

#import WINAQU_GUI_BONGO

# The recommended way to use wx graphics and matplotlib (mpl) is with the WXAgg
# backend. 
#
#import matplotlib
#matplotlib.use('WXAgg')
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_wxagg import \
#    FigureCanvasWxAgg as FigCanvas, \
#    NavigationToolbar2WxAgg as NavigationToolbar
#from mpl_toolkits.axes_grid.parasite_axes import HostAxes, ParasiteAxes
#from mpl_toolkits.axes_grid.parasite_axes import SubplotHost, ParasiteAxes
#import matplotlib.pyplot as plt
#import numpy as np
# import pylab

from Serial_Tools import *

import wxSerialConfigDialog_NAFC as wxSerialConfigDialog
#import wxTerminal_NAFC
from window_tools import *

ID_START_RT = wx.NewId()
ID_STOP_RT = wx.NewId()
ID_START_ARC = wx.NewId()
ID_STOP_ARC = wx.NewId()
ID_SER_CONF = wx.NewId()

VERSION = "V1.0 JUNE 2017"
TITLE = "ScanMar_Logger"
DEFAULT_COM = "COM1"
DEFAULT_BAUD = 4800
DEFAULT_RATE = 1   # scans per second

SIMULATOR = False

#

####################################################################
#   GraphFrame  -  Build the main frame of the application
#####################################################################
class GraphFrame(wx.Frame):

    title = TITLE +" "+VERSION
   
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        self.SetBackgroundColour('WHITE')
        self.ser = serial.Serial()  # Create a serial com port access instance
        SerialSource(self,self.ser).set_default()
        self.Serial_In = None
        
#        self.SRate = SmoothRate(5)  # Create a rate smoother instance

        self.port_open = False
        self.DataSource = None

# Some state variables
        self.LoggerRun = False
        self.MonitorRun = False

        self.RT_source = False
        self.ARC_source = False
        self.runlogfile=""
        self.LogFileName ="Not Logging"
        self.P_String= {}

        self.hd1=dict(SHIP="XX",TRIP="YYY",STN="000")
        self.hship = "YY"

        self.StartTime = 0
        self.ScanNum = 0

        self.Current={}
        self.CurrentBlock = {}
        self.CurrentBlock["HAVE-GLL"] = False
        self.CurrentBlock["NEWBLOCK"] = True
        self.CurrentBlock["NEXTGLL"] = False

# Build the display
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()



# TEMPORARY FOR TESTING
        self.LogFileName = "test_log.txt"
        self.flash_status_message("OPENING FILE FOR OUTPUT " + self.LogFileName)
        self.runlogfile = open(self.LogFileName, "w")

# the redraw timer is used to add new data to the plot and update any changes via
# the on_redraw_timer method
#10 ms; if you call at slower rate (say 100ms)the manual scale box entries don't respond well
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(1)

#**************************** End of GraphFrame Init **********************
#*** GraphFrame Methods ***************************************************

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_ser_config = menu_file.Append(ID_SER_CONF, "Serial Config", "Serial Config")
        self.Bind(wx.EVT_MENU, self.on_ser_config, m_ser_config)
        menu_file.AppendSeparator()
        m_term = menu_file.Append(-1, "Launch Terminal", "Terminal")
        self.Bind(wx.EVT_MENU, self.on_term, m_term)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        menu_realtime = wx.Menu()
        m_rtstart = menu_realtime.Append(ID_START_RT, "Start", "Start realtime data")
        self.Bind(wx.EVT_MENU, self.on_start_rt, m_rtstart)
        menu_realtime.AppendSeparator()
        m_rtstop = menu_realtime.Append(ID_STOP_RT, "End", "End realtime data")
        self.Bind(wx.EVT_MENU, self.on_stop_rt, m_rtstop)

        menu_archived = wx.Menu()
        m_arcstart = menu_archived.Append(ID_START_ARC, "Start", "Start archived data")
        self.Bind(wx.EVT_MENU, self.on_start_arc, m_arcstart)
        menu_archived.AppendSeparator()
        m_arcstop = menu_archived.Append(ID_STOP_ARC, "End", "End archived data")
        self.Bind(wx.EVT_MENU, self.on_stop_arc, m_arcstop)

        menu_option = wx.Menu()
        m_basehead = menu_option.Append(-1, "Set ship trip stn", "shiptripstn")
        self.Bind(wx.EVT_MENU, self.on_set_base_header, m_basehead)
        menu_option.AppendSeparator()
        m_edithead = menu_option.Append(-1, "Edit File Header", "Edit File Header")
        self.Bind(wx.EVT_MENU, self.on_edit_head, m_edithead)
        menu_option.AppendSeparator()
        menu_option.AppendSeparator()
        self.cb_grid = menu_option.Append (-1,"Show Grid","Grid",kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_cb_grid, self.cb_grid)
#        m_grid.SetValue(True) need syntax ??

        menu_help = wx.Menu()
#        m_help = menu_help.Append(-1, "help", "help")
#        self.Bind(wx.EVT_MENU, self.on_help, m_help)
#        menu_help.AppendSeparator()
        m_about = menu_help.Append(-1, "About", "About ScanMar_Logger")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_realtime, "RealTime")
        self.menubar.Append(menu_archived, "Archived")
        self.menubar.Append(menu_option, "Options")
        self.menubar.Append(menu_help,"Help")
        self.SetMenuBar(self.menubar)

        self.cb_grid.Check(True)
        m_rtstop.Enable(False)
        m_arcstop.Enable(False)
        m_term.Enable (False)  # leave off for now
        m_basehead.Enable(False)

# ***********************************************************************************
    def create_main_panel(self):
        
        self.panel = wx.Panel(self)  # Create a Panel instance


# Create a Canvas
#        self.canvas = FigCanvas(self.panel, -1, self.fig)

#        self.r_text = RollingDialBox(self.panel, -1, "Spare)", '0',50)
     
        self.LoggerRun_button = wx.Button(self.panel, -1, "Start Logging")
        self.Bind(wx.EVT_BUTTON, self.on_LoggerRun_button, self.LoggerRun_button)

        self.monitor_button = wx.Button(self.panel, -1, "Start  Monitor")
        self.Bind(wx.EVT_BUTTON, self.on_monitor_button, self.monitor_button)

        self.monitor_button.Enable(False)
        self.LoggerRun_button.Enable(False)
        
# Row 0 - the data monitor display


        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

# build from a sequence of tuples so that the order of the Dictionary is preserved (normal a:b notation will not work
# to preserve order when passed into the OrderedDict )
#        self.label_text[x].SetValue(x)
        xx=OrderedDict([("R",u"Role"),("P",u"Pitch"),("A",u"Roll-Rattle"),("B",u"Pitch-Rattle"),("S",u"Door Dist(m)")])
        self.disp_label= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", xx, '0',80,wx.RED,wx.VERTICAL)

        self.disp_text=OrderedDict([("DVTLAM",''),("DVTLAS",''),("CVTLAM",''),("CVTLAS",'')])
        xx =OrderedDict([("R",'r'), ("P", 'p'),( "A", 'a'),( "B", 'b'),("S", 's')])

# build the data boxes,,  access as disp_text["DVTLAM"].Data_text["R"].SetValue(xxxx)
        for x in self.disp_text:
            self.disp_text[x] = RollingDialBox_multi(self.panel, -1, x,xx, '0',50,wx.BLACK,wx.VERTICAL)
        self.hbox1.Add(self.disp_label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in self.disp_text:
            self.hbox1.Add(self.disp_text[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)




        xxy=OrderedDict([("R",u"Role"),("P",u"Pitch"),("A",u"Roll-Rattle"),("B",u"Pitch-Rattle")])
        self.disp_label2= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", xxy, '0',80,wx.RED,wx.VERTICAL)

        self.disp_text2 = OrderedDict([ ("TLT", '')])
        xxy =OrderedDict([("R",'r'), ("P", 'p'),( "A", 'a'),( "B", 'b')])
        self.disp_text2["TLT"] = RollingDialBox_multi(self.panel, -1, "TLT", xxy, '0', 50,wx.BLACK,wx.VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.disp_label2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.disp_text2["TLT"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        xxz=OrderedDict([("X","Across Speed"),("Y","Along Speed")])
        self.disp_label3= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", xxz, '0',90,wx.RED,wx.VERTICAL)

        self.disp_text3 = OrderedDict([ ("TSP", '')])
        xxz =OrderedDict([("X",u'x'), ("Y", u'y')])
        self.disp_text3["TSP"] = RollingDialBox_multi(self.panel, -1, "TSP", xxz, '0', 50,wx.BLACK,wx.VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.disp_text3["TSP"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        xxw=OrderedDict([("H","Height"),("O","Opening"),("C","Clearance"),("F","Fish Dens.")])
        self.disp_label4= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", xxw, '0',80,wx.RED,wx.VERTICAL)


        self.disp_text4 = OrderedDict([ ("TS", '')])
        xxw =OrderedDict([("H",'h'), ("O", 'o'),( "C", 'c'),( "F", 'f')])
        self.disp_text4["TS"] = RollingDialBox_multi(self.panel, -1, "TS", xxw, '0', 50,wx.BLACK,wx.VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
        self.hbox4.Add(self.disp_label4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.disp_text4["TS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.disp_text5 = OrderedDict([ ("ET", '')])
        xxw = OrderedDict([("ET", 'et')])
        self.disp_text5["ET"] = RollingDialBox_multi(self.panel, -1, "ET (secs)",xxw, '0',80,wx.BLACK,wx.VERTICAL)

        self.disp_text6 = OrderedDict([ ("CLOCK", '')])
        xxw = OrderedDict([("CLOCK", 'clk')])
        self.disp_text6["CLOCK"] = RollingDialBox_multi(self.panel, -1, "Clock",xxw, '0',80,wx.BLACK,wx.VERTICAL)

        gps=OrderedDict([("LA","LATITUDE"),("LO","LONGITUDE"),("H","HEADING(T)"),("SP","SPEED(Kn)")])
        self.disp_label8= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", gps, '0',80,wx.RED,wx.VERTICAL)


        self.disp_text8 = OrderedDict([ ("GPS", '')])
        gps =OrderedDict([("LA",'h'), ("LO", 'o'),( "H", 'c'),( "SP", 'f')])
        self.disp_text8["GPS"] = RollingDialBox_multi(self.panel, -1, "GPS", gps, '0', 70,wx.BLACK,wx.VERTICAL)
        self.hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
        self.hbox8.Add(self.disp_label8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox8.Add(self.disp_text8["GPS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        gps2=OrderedDict([("DT","DATE"),("TM","TIME")])
        self.disp_label10= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", gps2, '0',50,wx.RED,wx.VERTICAL)

        self.disp_text10 = OrderedDict([ ("GPSZDA", '')])
        gps2 =OrderedDict([("ZDA_DATE",'d'), ("ZDA_TS", 't')])
        self.disp_text10["GPSZDA"] = RollingDialBox_multi(self.panel, -1, "GPSZDA", gps2, '0', 90,wx.BLACK,wx.VERTICAL)
#        self.hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
# put in same box as the other gps stuff but next to it
        self.hbox8.Add(self.disp_label10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox8.Add(self.disp_text10["GPSZDA"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


# add the dictionaries onto the main dictionaries
        self.disp_text.update(self.disp_text2)
        self.disp_text.update(self.disp_text3)
        self.disp_text.update(self.disp_text4)
        self.disp_text.update(self.disp_text5)

        self.disp_text.update(self.disp_text8)
        self.disp_text.update(self.disp_text10)
        self.disp_text.update(self.disp_text6)
# Row 3   - buttoms and rate


        self.hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox9.Add(self.monitor_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox9.AddSpacer(2)
        self.hbox9.Add(self.LoggerRun_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox9.AddSpacer(20)
        self.hbox9.Add(self.disp_text5["ET"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox9.AddSpacer(10)
        self.hbox9.Add(self.disp_text6["CLOCK"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


# Put it all together

        self.VTBx = wx.StaticBox(self.panel,-1,"Door Sensors")
        self.VTbox = wx.StaticBoxSizer(self.VTBx, wx.HORIZONTAL)
        self.VTbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.TLTbx = wx.StaticBox(self.panel,-1,"Tilt")
        self.TLTbox = wx.StaticBoxSizer(self.TLTbx, wx.HORIZONTAL)
        self.TLTbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.TSPbx = wx.StaticBox(self.panel,-1,"Trawl Speed")
        self.TSPbox = wx.StaticBoxSizer(self.TSPbx, wx.HORIZONTAL)
        self.TSPbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.TSbx = wx.StaticBox(self.panel,-1,"Trawl Sounder")
        self.TSbox = wx.StaticBoxSizer(self.TSbx, wx.HORIZONTAL)
        self.TSbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.GPSbx = wx.StaticBox(self.panel,-1,"GPS")
        self.GPSbox = wx.StaticBoxSizer(self.GPSbx, wx.HORIZONTAL)
        self.GPSbox.Add(self.hbox8, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.GPSbox.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.LRbox = wx.BoxSizer(wx.HORIZONTAL)
        self.LRbox.Add(self.VTbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.TLTbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.TSPbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.TSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.LRbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.LRbox2.Add(self.GPSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.LRbox2.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.LRbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.LRbox3.Add(self.hbox9, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.LRbox3.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
#        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.LRbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.LRbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.LRbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        
#***********************************************************   
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

#############################################

#*** ACTION METHODS ***************        
    def on_LoggerRun_button(self, event):
        if  not self.DataSource == None :
            self.LoggerRun = not self.LoggerRun
            self.on_update_LoggerRun_button(event)
            if self.LoggerRun == True:
                self.MonitorRun = True
                self.on_update_monitor_button(event)

    def on_monitor_button(self, event):
        if  not self.DataSource == None :
          self.MonitorRun = not self.MonitorRun
          self.on_update_monitor_button(event)
          if self.MonitorRun == False:
            self.LoggerRun = False
            self.on_update_LoggerRun_button(event)
    
    def on_update_LoggerRun_button(self, event):
        label = "Stop Logging" if self.LoggerRun else "Start Logging"
        self.LoggerRun_button.SetLabel(label)

    def on_update_monitor_button(self, event):
        label = "Stop Monitor" if self.MonitorRun else "Start Monitor"
        self.StartTime = 0
        self.DataSource.flush()
        self.monitor_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

            
################### ON_REDRAW_TIMER ##########################################################
# This method is repeatably called by the re-draw timer to get any new data
# what it does depends on the STATE variables
##############################################################################################

    def on_redraw_timer(self, event):

# recorded_data = False means parse raw ctd format data, this flag is for testing
        self.Tstr = '0'
        ETstr ='0'
        pres = 0.0



# if no data source do nothing, but call for a re-draw in case any controls have been changed
        if self.DataSource == None :
#            self.draw_plot()
            return()

        if  not self.MonitorRun :
            self.DataSource.flush()
        else :
            scan =self.DataSource.next()
          
            if not scan["OK"]:
        

# we will only save the  data when the logger is running
#              if self.LoggerRun :


#                  print time.strftime('%Y:%m:%dT%X') # ISO 8601 date time stamp                  
# if scan not ok finished data stop the graph and monitor, turning off the monitor turns off the graph as well
                if scan["REASON"] == "FINISHED":
                    self.on_monitor_button(wx.EVT_BUTTON)
                    self.on_update_monitor_button(wx.EVT_UPDATE_UI)
                    self.on_stop_arc(1)
                else:
                    if self.RT_source :
#                      self.on_stop_rt(1)
                      self.message_box("DATA SOURCE HAS STOPPED or MISSING\nIF THIS IS UNEXPECTED CHECK CABLING etc\n ...CLOSING CONNECTION...")
#                    else :
#                       self.on_stop_arc(1)


# these are the data displayed on the monitor line
            elif  self.MonitorRun:


                if self.StartTime == 0:
                    self.StartTime = time.time()
                else:
                    Et = str(time.time() - self.StartTime)
                    self.disp_text["ET"].Data_text["ET"].SetValue('{:>5.4}'.format(str(Et)))



#           Rstr = '{:>5.4}'.format(str(self.SRate.get_rate(scan["pres"])))
#                for x in scan:
# waste gate the data until we get a GLL fix
                print "ugg"
                if  self.CurrentBlock["HAVE-GLL"] or  ("GLL" in scan) :

                    print "In logger", scan["SENSOR"],

                    if "SM2" in scan:
                        x = 'SM2'
                        print  scan[x].sensor,scan[x].status,scan[x].sensor_id,scan[x].measurement_id,scan[x].measurement_val, scan[x].timestamp
                        self.Current[scan["SENSOR"]] = scan[x]

# update the displayed value
                        if scan[x].measurement_id != '':  #issue with CVTLAM having no id value in test data
                            self.disp_text[scan[x].sensor].Data_text[scan[x].measurement_id].SetValue(scan[x].measurement_val)
                            self.disp_text["CLOCK"].Data_text["CLOCK"].SetValue(str(scan[x].timestamp))
                            self.P_String[scan["SENSOR"]] = scan[x].measurement_val,scan[x].status,scan[x].qf

                    elif "GLL" in scan:
                        x = 'GLL'
#                        for yy in scan[x] :
#                            print yy,scan[x][yy]


#                        GLL['LATITUDE'] = msg.latitude
#                        GLL['LONGITUDE'] = msg.longitude
#                        GLL['TIMESTAMP'] = msg.timestamp

                        if self.CurrentBlock["HAVE-GLL"]  :  # copy forward
                                self.Current[scan["SENSOR"]] = self.CurrentBlock["NEXTGLL"]
                                self.CurrentBlock["NEXTGLL"] = scan[x]
                                self.CurrentBlock["NEWBLOCK"] = True
                                print "COPY FORWARD.."

                        else: # starta new block
                                print "NEW START BLOCK.."
                                self.Current[scan["SENSOR"]] = scan[x]
                                self.CurrentBlock["NEWBLOCK"] = False

                        self.CurrentBlock["HAVE-GLL"] = True
                        self.disp_text["GPS"].Data_text["LA"].SetValue('{:>7.7}'.format(str(self.Current["GLL"].latitude)))

                        self.disp_text["GPS"].Data_text["LO"].SetValue('{:>8.8}'.format(str(scan[x].longitude)))
                        self.P_String["GLL_LAT"] = self.Current["GLL"].latitude
                        self.P_String["GLL_LON"] = self.Current["GLL"].longitude

                    elif "VTG" in scan:
                        x ='VTG'
#                        for yy in scan[x] :
#                            print yy,scan[x][yy]
                        self.Current["VTG"] = scan[x]
                        self.disp_text["GPS"].Data_text["H"].SetValue(str(scan[x].true_track))
                        self.disp_text["GPS"].Data_text["SP"].SetValue(str(scan[x].spd_over_grnd_kts))
                        self.P_String["VTG_TRACK"] = str(scan[x].true_track)
                        self.P_String["VTG_SPD"] = str(scan[x].spd_over_grnd_kts)

                    elif "ZDA" in scan:
                        x = 'ZDA'
#                        for yy in scan[x]:
#                            print yy, scan[x][yy]
                        self.Current[scan["SENSOR"]] = scan
                        self.disp_text["GPSZDA"].Data_text["ZDA_DATE"].SetValue(str(scan["ZDA"]["ZDA_DATE"]))
                        self.disp_text["GPSZDA"].Data_text["ZDA_TS"].SetValue(str(scan["ZDA"]["ZDA_TIMESTAMP"]))

                        self.P_String ["ZDA_DATETIME"]= str(scan["ZDA"]["ZDA_DATE"])+'T'+str(scan["ZDA"]["ZDA_TIMESTAMP"])

                    else:
                        print "Fell Through no hits.."


        
#                if self.LoggerRun and self.runlogfile :
                if self.LoggerRun and  self.CurrentBlock["HAVE-GLL"] and self.CurrentBlock["NEWBLOCK"]:
                    self.ScanNum+=1
                    xdatetime = '{:>8.8}'.format(str(datetime.datetime.now().time()))
                    print "OUTPUT.."
                    for xx in self.Current:
                        print xx,self.Current[xx],
#                       for yy in self.Current[xx]:
#                           print yy,self.Current[xx][yy],
#                            print yy,
                        print
                    for zz in self.P_String :
                        print self.P_String[zz],
                        self.runlogfile.write (zz+"="+str(self.P_String[zz])+" ")
                    print
                    self.runlogfile.write("\n" )
#                    self.runlogfile.write(str(self.ScanNum)+" "+xdatetime+" "+'{:>5.4}'.format(scan["Et"])+" "+scan["Pstr"]+" "+scan["Tstr"]+" "+scan["Cstr"]+
#                     " "+scan["Sstr"]+" "+scan["Dstr"]+ " "+scan["F1str"]+" "+scan["F2str"]+" "+scan["Lstr"]+" "+scan["Vstr"]+"\n")

                    self.CurrentBlock["NEWBLOCK"]= False
                    print
#  end of if else MonitorRun
# call draw-plot iregardless of monitor status so that rescale works, else it
# wont update to new button settings until monitor is started
#  redraw the plot, and then return to wait for next timer call
 #       self.draw_plot()

######################## Menu things ########################
    def save_file_dialog(self):

        """Save contents of output window."""
        outfilename = None
        dlg = wx.FileDialog(None, "Save File As...", "", "", "ScanMar Proc log|*.csv|All Files|*",  wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() ==  wx.ID_OK:
            outfilename = dlg.GetPath()
        dlg.Destroy()
        return (outfilename)
    
    def get_file_dialog(self):
        filename = None
        dialog = wx.FileDialog(None, "Choose File.",os.getcwd(), "", "ScanMar Raw Log|*.log|All Files|*",wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            filename =  dialog.GetPath()  
        dialog.Destroy()
        return(filename)
    
# Save plot image
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
            
# Configure serial port, requires our serial instance, make sure port is closed before calling
    def on_ser_config(self,event):
        self.ser.close()
        dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "",
                show=wxSerialConfigDialog.SHOW_BAUDRATE|wxSerialConfigDialog.SHOW_FORMAT|wxSerialConfigDialog.SHOW_FLOW,
                serial=self.ser
            )
        result = dialog_serial_cfg.ShowModal()
        dialog_serial_cfg.Destroy()

# pop up the wxterminal for interaction - THIS IS NOT WORKING YET NEEDS WORK
    def on_term(self,event):

        self.ser.close()
#        wxTerminal.MyApp()
        print "opening wx"
#        frame_terminal=wxTerminal.MyApp(0)
        frame_terminal=wxTerminal_NAFC.TerminalFrame(self, -1, "")
        print "Show modal"
#        self.SetTopWindow(frame_terminal)
        frame_terminal.Show()
        print "Destroying"
        frame_terminal.Destroy()

# Realtime -> start  opens serial port and log file for realtime data
        
    def on_start_rt (self, event):

        if self.Serial_In == None:
            self.Serial_In = SerialSource(self,self.ser) 

        self.port_open = self.Serial_In.open_Port()
        if not self.port_open :
            self.message_box("Can Not Open Port- check settings"+self.ser.getPort())          
            return()
        
# if we have an open port proceed     
        self.RT_source = True
        
        self.LogFileName = self.save_file_dialog() # get filename of desired logfile

        if not self.LogFileName == None :
            self.flash_status_message("OPENING FILE FOR OUTPUT "+self.LogFileName)
            self.runlogfile = open(self.LogFileName,"w")
            self.WriteHeader(self.runlogfile)
        else:
            self.flash_status_message("NOT LOGGING TO FILE")
            self.LogFileName = "NOT LOGGING TO FILE"
            
        self.host.set_title('Bongo trace data file= '+self.LogFileName, size=8) # label plot

# now configure the  and start the data coming
        self.Serial_In.send_Real()
        self.interval = DEFAULT_RATE  # until there is a menu item to change it :-)
        self.Serial_In.send_Set_Rate(str(self.interval))
        self.Serial_In.send_Start__Data()

# Lock out some controls like archived data play back while RealTime is running
# set End to active Start to inactive on Realtime Memu
# need to add lock out on serial config as well !!!
        menubar = self.menubar

        enabled = menubar.IsEnabled(ID_START_RT)
        menubar.Enable(ID_START_RT,not enabled)
        enabled = menubar.IsEnabled(ID_STOP_RT)
        menubar.Enable(ID_STOP_RT,not enabled)
        menubar.Enable(ID_SER_CONF, False)
        menubar.EnableTop(2, False)  # lock out arc playback while rt running
        self.monitor_button.Enable(True)
        self.LoggerRun_button.Enable(True)
        self.data["Pres"]=[0]
        self.data["Temp"]=[0]
        self.data["Et"]=[0]
        self.DataSource = self.Serial_In


# *****************************************************************

    def on_stop_rt (self, event):
        if self.MonitorRun:
             self.on_monitor_button(event)
        try:                  
              self.runlogfile.close()
        except: pass
        
        self.RT_source = False
        self.DataSource = None
        self.Serial_In.send_Stop__Data ()
        self.Serial_In.close_Port ()
        self.port_open = False
        menubar = self.GetMenuBar()
        enabled = menubar.IsEnabled(ID_START_RT)
        menubar.Enable(ID_START_RT,not enabled)
        enabled = menubar.IsEnabled(ID_STOP_RT)
        menubar.Enable(ID_STOP_RT,not enabled)
        menubar.Enable(ID_SER_CONF, True)

        menubar.EnableTop(2, True)  # re-enable archieved data option
        self.monitor_button.Enable(False)
        self.LoggerRun_button.Enable(False)
        
#************************ archieve data ***************************
    def on_start_arc(self, event):
        FileName = self.get_file_dialog()  #get filename of logged file
        if FileName !="" :
            self.RT_source = False
            self.ARC_source = True
#            self.host.set_title('Bongo trace data file= '+FileName, size=8) # label plot
            menubar = self.GetMenuBar()
            enabled = menubar.IsEnabled(ID_START_ARC)
            menubar.Enable(ID_START_ARC,not enabled)
            enabled = menubar.IsEnabled(ID_STOP_ARC)
            menubar.Enable(ID_STOP_ARC,not enabled)
            menubar.EnableTop(1, False)  # lock out RT playback while Archieved running
            self.monitor_button.Enable(True)
            self.LoggerRun_button.Enable(True)            
            self.datagen = DataGen_que(self,FileName) #Create a data source instance

            self.DataSource = self.datagen
            self.CurrentBlock["HAVE-GLL"] = False

    def on_stop_arc (self, event):
        if self.MonitorRun:
             self.on_monitor_button(event)
        if self.ARC_source:
            self.ARC_source = False
            self.datagen.close_DataSource()
        self.DataSource = None

        menubar = self.GetMenuBar()
        enabled = menubar.IsEnabled(ID_START_ARC)
        menubar.Enable(ID_START_ARC,not enabled)
        enabled = menubar.IsEnabled(ID_STOP_ARC)
        menubar.Enable(ID_STOP_ARC,not enabled)
        self.monitor_button.Enable(False)
        self.LoggerRun_button.Enable(False)
        menubar.EnableTop(1, True)  # re-enable realtime data option

    def on_edit_head(self,event):
        if self.RT_source == True:
            self.on_stop_rt (1)
#        WINAQU_GUI_BONGO.main()

    def on_set_base_header(self,event):
        xx = ShipTrip_Dialog(self,self.hd1["SHIP"],self.hd1["TRIP"],self.hd1["STN"])
        print "before "+self.hd1["SHIP"]+" "+ self.hship

        xx.SetBase(self.hship,self.hd1["TRIP"],self.hd1["STN"])
        res=xx.ShowModal()
        if res == wx.ID_OK:

 
            self.hd1["SHIP"] = xx.GetShip()
            self.hship = xx.GetShip()
            self.hd1["TRIP"] = xx.GetTrip()
            self.hd1["STN"] = xx.GetStn()
            print "AFTER="+self.hd1["SHIP"]+" "+ self.hship
            self.hship="LL"

            xx.Destroy()


#******************* assorted  methods ****************************************************

    def WriteHeader (self,fp) :
#        print "In WRite "+self.hd1["SHIP"]

        xtime = '{:>5.5}'.format(str(datetime.datetime.now().time()))
        xdate = '{:>12.12}'.format(str(datetime.datetime.now().date()))
        hdr1_out= self.hd1["SHIP"].strip().zfill(2)+ self.hd1["TRIP"].strip().zfill(3)+ self.hd1["STN"].strip().zfill(3)
        fp.write("NAFC_Y2K_HEADER\n")
        fp.write (hdr1_out+"                    "+xdate+" "+xtime+"      12     O                1\n")
        fp.write (hdr1_out+" 000000 01.00 A 12 #ZEPTCSMWwLV--------              000 0000 0000 000 4\n")
        fp.write (hdr1_out+"                                                                       8\n")
        fp.write ("SCAN CtdClk   ET   DEPTH    TEMP  COND   SAL   SIGMAT   FLOW1   FLOW2  LIGHT   VOLTS\n")
        fp.write ("-- DATA --\n")


    
    def on_exit(self, event):
        if self.runlogfile != "": 
          self.runlogfile.close()
        self.redraw_timer.Stop()
        self.on_stop_arc(event)
        if self.port_open:
          self.Serial_In.close_Port()
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def message_box (self,message):
        result= wx.MessageBox (message,style=wx.CENTER|wx.OK)

    def ShowMessage2(self, event):
        dial = wx.MessageDialog(None, 'Error loading file', 'Error', 
        wx.OK | wx.ICON_ERROR)
        dial.ShowModal()  

    def OnAbout(self,event):
        """ Show About Dialog """
        info = wx.AboutDialogInfo()

        desc = ["\nScanBas_Logger\n",
                "Platform Info: (%s,%s)",
                "License: None - see code"]
        desc = "\n".join(desc)

        # Platform info
        py_version = [sys.platform,", python ",sys.version.split()[0]]
        platform = list(wx.PlatformInfo[1:])
        platform[0] += (" " + wx.VERSION_STRING)
        wx_info = ", ".join(platform)

        info.SetName(TITLE)
        info.SetVersion(VERSION)
        info.SetDevelopers (["D. Senciall",
                             "\nScience Branch",
                             "\n NWAFC, NL region-DFO, Gov. of Canada"])
        info.SetCopyright ("Note: Some elements based or insprired by on open community code:\nSee Source for credits")
#        info.SetDescription (desc % (py_version, wx_info))
        wx.AboutBox(info)
        
#******** END of GraphFrame ************************************************************

##############################################################################################
#####################################  MAIN ENTRY POINT ################################        
if __name__ == '__main__':

    app = wx.App()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()
###################################### END OF CODE #####################################
