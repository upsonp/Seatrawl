# -*- coding: utf-8 -*-

#
# ScanMar_logger.py   D.Senciall  August 2017
# update June 1 2015 to fix incorrect presure conversion in realtime data reader
"""
Some Elements BASED ON CODE SAMPLE FROM: matplotlib-with-wxpython-guis by E.Bendersky
Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008

"""
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


from Serial_Tools import *
from ScanMarNmea import SMN_TOOLS
import wxSerialConfigDialog

from window_tools import *

ID_START_RT = wx.NewId()
ID_STOP_RT = wx.NewId()
ID_START_ARC = wx.NewId()
ID_STOP_ARC = wx.NewId()
ID_SER_CONF = wx.NewId()

VERSION = "V1.01 Oct 2017"
TITLE = "ScanMar_Logger"


# ###################################################################
#   GraphFrame  -  Build the main frame of the application
# ####################################################################
class GraphFrame(wx.Frame):

    title = TITLE + " " + VERSION
   
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)

        self.SetBackgroundColour('WHITE')

# these tools proocess the messages
        self.smn_tools = SMN_TOOLS()

# we need a serial instance to allow the  serial config dialogue to function
        self.ser = serial.Serial()

# Some state variables
        self.Serial_In = None
        self.LoggerRun = False
        self.MonitorRun = False
        self.OnBottom = False
        self.DataSource = None
        self.RT_source = False
        self.ARC_source = False
        self.running_a_logfile = False

        self.ShipTripSet = {"SHIP": "00", "TRIP": "000", "SET": "000"}

# sued for elapsed time
        self.StartTime = -1

        self.RAWFileName = None
        self.JSONFileName = None
        self.CSVFileName = None
        self.MISIONFileName = None

#        self.BaseName = self.make_base_name()

        self.JDict = OrderedDict()
        self.JDict["Latitude"] = ''
        self.JDict["Longitude"] = ''

        self.RAW_fp = None
        self.JSON_fp = None
        self.CSV_fp = None
        self.TripLog_fp = None
#        self.flash_status_message("OPENING FILE FOR OUTPUT " + self.LogFileName)
#        print self.BaseName

        # Build the display
        self.menubar = wx.MenuBar()
        self.populate_menu()

        self.create_status_bar()

#        self.topPanel = wx.Panel(self)
 #       self.topPanel.SetBackgroundColour('#608060')
#        self.panel_1 = wx.Panel(self)  # Create a Panel instance
#        self.panel = wx.Panel(self.topPanel,-1,pos=(0,100),size=(100,100))  # Create a Panel instance
#       self.panel2 = wx.Panel(self.topPanel, -1,pos=(0,200))
#        self.panel = wx.Panel(self.topPanel,-1)  # Create a Panel instance
#        self.panel2 = wx.Panel(self.topPanel, -1)
#        self.panel2.SetBackgroundColour('#6f8089')
        self.panel= wx.Panel(self)  # Create a Panel instance
#        self.panel_4 = wx.Panel(self)  # Create a Panel instance

        self.panel.SetBackgroundColour(wx.NamedColour("WHEAT"))
        self.populate_main_panel()

        self.set_FileNames()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel,0,wx.EXPAND|wx.ALL,border=10)
#        sizer.Add(self.panel2,0,wx.EXPAND|wx.ALL,border=10)

#        self.topPanel.SetSizer(sizer)

        self.BQueue = Queue.Queue()

# the redraw timer is used to add new data to the plot and update any changes via
# the on_redraw_timer method
#  1000 ms; ie check  once a second;  since data rate is ~1 second per block (multiple nmea lines)
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(500)
#        self.redraw_timer.Stop()

# **************************** End of GraphFrame Init **********************
# *** GraphFrame Methods ***************************************************

    def populate_menu(self):

        menu_file = wx.Menu()
#        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
#        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_ser_config = menu_file.Append(ID_SER_CONF, "Serial Config", "Serial Config")
        self.Bind(wx.EVT_MENU, self.on_ser_config, m_ser_config)
        menu_file.AppendSeparator()
#        m_term = menu_file.Append(-1, "Launch Terminal", "Terminal")
#        self.Bind(wx.EVT_MENU, self.on_term, m_term)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        # responds to exit symbol x on frame title bar
        self.Bind(wx.EVT_CLOSE, self.on_exit)

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
#        self.SPW_tick = menu_option.Append (-1,"Show Port Wire","Show Port Wire",kind=wx.ITEM_CHECK)
#        self.Bind(wx.EVT_MENU, self.on_port_wire, self.SPW_tick)
#        self.SPW_tick.SetValue(True)

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
        self.menubar.Append(menu_help, "Help")
        self.SetMenuBar(self.menubar)

#        self.SPW_tick.Check(True)
        m_rtstop.Enable(False)
        m_arcstop.Enable(False)
#        m_term.Enable(False)  # leave off for now
        m_basehead.Enable(True)

# ***********************************************************************************
    def populate_main_panel(self):

#       Create a Canvas
#       self.canvas = FigCanvas(self.panel, -1, self.fig)
#       self.r_text = RollingDialBox(self.panel, -1, "Spare)", '0',50)

        self.populate_button_strip(self.panel)

        self.populate_logger_strip()

        self.populate_rolling_display_legacy()

        self.assemble_display()


# ###################################################################################

    def populate_button_strip(self,apanel):
        buttonfont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)

        self.LoggerStart_button = wx.Button(apanel, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button.SetFont(buttonfont)
        self.LoggerStart_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_LoggerStart_button, self.LoggerStart_button)


        self.LoggerEnd_button = wx.Button(apanel,-1,   " Out of Water  \nEnd Logging\n(F6)")
        self.LoggerEnd_button.SetFont(buttonfont)
        self.LoggerEnd_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_LoggerEnd_button, self.LoggerEnd_button)

        self.BottomStart_button = wx.Button(apanel,-1, "On Bottom\nStart Fishing Tow\n(F3)")
        self.BottomStart_button.SetFont(buttonfont)
#       self.monitor_button.SetBackgroundColour((255, 155, 0))  # set text back color
        self.BottomStart_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_BottomStart_button, self.BottomStart_button)

        self.BottomEnd_button = wx.Button(apanel, -1,   "Off Bottom \nEnd Fishing Tow\n(F5)")
        self.BottomEnd_button.SetFont(buttonfont)
#       self.monitor_button.SetBackgroundColour((255, 155, 0))  # set text back color
        self.BottomEnd_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_BottomEnd_button, self.BottomEnd_button)


        self.Abort_button = wx.Button(apanel, -1, "Abort\n(F10)")
        self.Abort_button.SetFont(buttonfont)
        self.Abort_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_Abort_button, self.Abort_button)

        self.Increment_button = wx.Button(apanel, -1, "Increment\nSet #\n(F12)")
        self.Increment_button.SetFont(buttonfont)
        self.Increment_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_Increment_tow_button,self.Increment_button)


        self.warpbox = wx.BoxSizer(wx.VERTICAL)


        warpfont = wx.Font(12, wx.DECORATIVE,wx.NORMAL, wx.BOLD)
        self.Warp_button  = wx.Button(apanel, -1, "Enter WarpOut(m)\n(F4)  ")
        self.Warp_button.SetFont(warpfont)
        self.Warp_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.warpbox.Add(self.Warp_button, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 0)
        self.Warp_text = wx.TextCtrl(self.panel,style = wx.TE_PROCESS_ENTER,validator=CharValidator('no-alpha'))


        warpTxtfont = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.Warp_text.SetFont(warpTxtfont)
        self.Warp_text.SetMaxLength(4)
        self.warpbox.Add(self.Warp_text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 0)
#        self.t1.Bind(wx.EVT_TEXT, self.OnKeyTyped)
        self.Warp_text.Bind( wx.EVT_TEXT_ENTER,self.OnWarpTyped)
#        self.t1.Bind( wx.EVT_KILL_FOCUS,self.OnKeyTyped)
        self.Bind(wx.EVT_BUTTON, self.on_Warp_button, self.Warp_button)


        self.Warp_text.Enable(False)
        self.WRPbox = wx.BoxSizer(wx.VERTICAL)
        self.WRPbox.AddSpacer(2)
        self.WRPbox.Add(self.warpbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)


        self.LoggerStart_button.Enable(True)
        self.LoggerEnd_button.Enable(False)
        self.Warp_button.Enable(False)

        self.BottomStart_button.Enable(False)
        self.BottomEnd_button.Enable(False)
        self.Abort_button.Enable(False)


        F1_id = wx.NewId()
        F3_id = wx.NewId()
        F4_id = wx.NewId()
        F5_id = wx.NewId()
        F6_id = wx.NewId()
        F10_id = wx.NewId()
        F12_id = wx.NewId()

        self.Bind(wx.EVT_MENU, self.on_LoggerStart_button, id=F1_id)
        self.Bind(wx.EVT_MENU, self.on_BottomStart_button, id=F3_id)
        self.Bind(wx.EVT_MENU, self.on_Warp_button, id=F4_id)
        self.Bind(wx.EVT_MENU, self.on_BottomEnd_button, id=F5_id)
        self.Bind(wx.EVT_MENU, self.on_LoggerEnd_button, id=F6_id)
        self.Bind(wx.EVT_MENU, self.on_Abort_button, id=F10_id)
        self.Bind(wx.EVT_MENU, self.on_Increment_tow_button, id=F12_id)

        self.accel_tbl = wx.AcceleratorTable(  [(wx.ACCEL_NORMAL, wx.WXK_F1, F1_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F3, F3_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F4, F4_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F5, F5_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F6, F6_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F10, F10_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F12, F12_id)
                                               ]
                                            )

        self.SetAcceleratorTable(self.accel_tbl)


# standard database colours  http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.ColourDatabase.html

#        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hb0 = wx.StaticBox(apanel,-1,"Buttons")
#        self.hb0.SetBackgroundColour((200, 200, 200))  # set text back color
        self.hb0.SetBackgroundColour("WHEAT")  # set text back color
        self.hb0.SetForegroundColour((0, 0, 0))  # set text back color
        self.hbox0 = wx.StaticBoxSizer(self.hb0, wx.HORIZONTAL)

        self.hbox0.AddSpacer(5)
        self.hbox0.Add(self.LoggerStart_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.Add(self.BottomStart_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.AddSpacer(5)
        self.hbox0.Add(self.warpbox, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.AddSpacer(5)
        self.hbox0.Add(self.BottomEnd_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.Add(self.LoggerEnd_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.AddSpacer(8)
        self.hbox0.Add(self.Abort_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

    def populate_logger_strip(self):

        # Row 0 - the data monitor display
        x = 1200
        y = 150
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.SUNKEN_BORDER | wx.VSCROLL

        self.label = wx.StaticText(self.panel,
                label="   EVENT     STATION    DATE       TIME   BTM-D(m)  TRL_DEP(m)    LATITUDE     LONGITUDE")
        self.log1 = wx.TextCtrl(self.panel, wx.ID_ANY, size=(x, y), style=style)

        logfont = wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.log1.SetFont(logfont)
        self.label.SetFont(logfont)

#        self.textsizer = wx.BoxSizer(wx.VERTICAL)
#        self.textsizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
#        self.textsizer.Add(self.log1, 1, wx.ALL | wx.EXPAND, 5)

#        self.hbox0a = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox0a.Add(self.textsizer, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        self.hbox_EL= wx.GridBagSizer(2, 2)
        self.hbox_EL.Add(self.label, (0, 1))
        self.hbox_EL.Add(self.log1, (1, 1))

        self.EVbx = wx.StaticBox(self.panel,-1,"Event Log")
        self.ELbox = wx.StaticBoxSizer(self.EVbx, wx.VERTICAL)
        self.ELbox.Add(self.hbox_EL, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    def populate_rolling_display_legacy(self):


        afontsize = 10
        afontbigger = 26
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

# build from a sequence of tuples so that the order of the Dictionary is preserved (normal a:b notation will not work
# to preserve order when passed into the OrderedDict )
#        self.label_text[x].SetValue(x)
        timelabel=OrderedDict([("0",u"Current"),("1",u"1 scan Ago"),("2",u"2 scan Ago"),("3",u"3 scan Ago"),
                                        ("4",u"4 scan Ago")])

        self.disp_label= RollingDialBox_multi_static(self.panel, -1,"---- Log ----", timelabel, '0',80,
                                        wx.BLUE,wx.VERTICAL,afontsize)

        self.disp_text=OrderedDict([("DVTLAM_1_P",''),("DVTLAM_1_R",''),("DVTLAS_1_P",''),("DVTLAS_1_R",''),
                                        ("CVTLAM_1_S",'')])
        xx =OrderedDict([("0",'0'), ("1", '0'),( "2", '0'),( "3", '0'),("4", '0')])
        x2 = OrderedDict([("DVTLAM_1_P", 'Port-Pitch'), ("DVTLAM_1_R", 'Port-Roll'), ("DVTLAS_1_P",'Stbd-Pitch'),
                                        ("DVTLAS_1_R",'Stbd-Roll'),("CVTLAM_1_S", 'Wing-Spread')])


# build the data boxes,,  access as disp_text["DVTLAM"].Data_text["R"].SetValue(xxxx)
        for x in self.disp_text :
            self.disp_text[x] = RollingDialBox_multi(self.panel, -1, x2[x],xx, '0',50,wx.BLACK,wx.VERTICAL,afontsize)
        self.hbox1.Add(self.disp_label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in self.disp_text:
            self.hbox1.Add(self.disp_text[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.disp_text["DVTLAS"].Data_text["S"].SetValue('-------')
#        self.disp_text["DVTLAS"].Data_text["S"].Enable(False)


#        xxy=OrderedDict([("R",u"Role (Deg)"),("P",u"Pitch (Deg)"),("A",u"Roll-Rattle"),("B",u"Pitch-Rattle")])
#        self.disp_label2= RollingDialBox_multi_static(self.panel, -1,"---- Log ----", xxy, '0',80,wx.RED,wx.VERTICAL)


#        self.disp_text2 = OrderedDict([ ("TLT", '')])
#        xxy =OrderedDict([("R",'r'), ("P", 'p'),( "A", 'a'),( "B", 'b')])
#        self.disp_text2["TLT"] = RollingDialBox_multi(self.panel, -1, "Tilt", xxy, '0', 50,wx.BLACK,wx.VERTICAL)

#        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox2.Add(self.disp_label2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox2.Add(self.disp_text2["TLT"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.disp_text3 = OrderedDict([ ("TSP_1_X", ''),("TSP_1_Y",'')])

        x2 = OrderedDict([("TSP_1_X", 'Cross'), ("TSP_1_Y", 'Along')])

        for x in self.disp_text3 :
            self.disp_text3[x] = RollingDialBox_multi(self.panel, -1, x2[x],xx, '0',50,wx.BLACK,wx.VERTICAL,afontsize)
#        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in self.disp_text3:
            self.hbox3.Add(self.disp_text3[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.disp_text4 = OrderedDict([ ("TS_5_H", ''),("TS_5_O",''),("TS_5_C",''),("DP_1_H",'')])
        x2 = OrderedDict([("TS_5_H", 'Height'), ("TS_5_O", 'Opening'), ("TS_5_C", 'Clear'),("DP_1_H",'TrawlDepth')])
        for x in self.disp_text4:
            self.disp_text4[x] = RollingDialBox_multi(self.panel, -1, x2[x], xx, '0', 60, wx.BLACK, wx.VERTICAL,afontsize)
            #        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in self.disp_text4:
            self.hbox4.Add(self.disp_text4[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.disp_text4["TS"] = RollingDialBox_multi(self.panel, -1, "TS (m)", xxw, '0', 50,wx.BLACK,wx.VERTICAL)
#        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
#        self.hbox4.Add(self.disp_label4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox4.Add(self.disp_text4["TS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.disp_text5 = OrderedDict([ ("ET", '')])
        xxw = OrderedDict([("ET", '00:00:00')])
        self.disp_text5["ET"] = RollingDialBox_multi(self.panel, -1, "ET Bottom (H:M:S)",xxw, '0',160,
                                                     wx.RED,wx.VERTICAL,afontbigger)
        self.hbox5.Add(self.disp_text5["ET"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.disp_text6 = OrderedDict([ ("CLOCK", '')])
        xxw = OrderedDict([("CLOCK", '12:12:12')])
        dt =  time.strftime('%Y-%m-%d\n%H:%M:%S')
        zone = time.tzname[time.daylight]
        self.disp_text6["CLOCK"] = RollingDialBox_2d(self.panel, -1, "PC Clock", dt ,80,
                                                        wx.BLACK,wx.VERTICAL,afontsize)
        self.hbox5.Add(self.disp_text6["CLOCK"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

# ##########################

        self.disp_label2= RollingDialBox_multi_static(self.panel, -1,"---- Log ----", timelabel, '0',80,wx.BLUE,
                                                      wx.VERTICAL,afontsize)

        self.hbox8 = wx.BoxSizer(wx.HORIZONTAL)

        self.disp_text8 = OrderedDict([("ZDA_TS",''),("LAT",''),("LON",''),("VTG_COG",''),("VTG_SPD",'')])
        self.disp_text8_size = OrderedDict([("ZDA_TS",70),("LAT",90),("LON",100),("VTG_COG",60),("VTG_SPD",60)])

        x2 = OrderedDict([("ZDA_TS",'Time (GPS)'),("LAT", 'Latitude'), ("LON", 'Longitude'),("VTG_COG","COG"), ("VTG_SPD", 'Speed (kn)')])

        # build the data boxes,,  access as disp_text["DVTLAM"].Data_text["R"].SetValue(xxxx)
        for x in self.disp_text8:
            self.disp_text8[x] = RollingDialBox_multi(self.panel, -1, x2[x], xx, '0', self.disp_text8_size[x], wx.BLACK, wx.VERTICAL,afontsize)
        self.hbox8.Add(self.disp_label2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in self.disp_text8:
            self.hbox8.Add(self.disp_text8[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)



        # ###########################
#        gps=OrderedDict([("LA","LATITUDE"),("LO","LONGITUDE"),("H","COG (True)"),("SP","SPEED (Kn)")])
#        self.disp_label8= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", gps, '0',80,wx.RED,wx.VERTICAL)

#        self.hbox8 = wx.BoxSizer(wx.HORIZONTAL)

#        self.disp_text8 = OrderedDict([ ("GPS", '')])
#        gps =OrderedDict([("LA",'00\xb0 00.00\' N'), ("LO", '00\xb0 00.00\' W'),( "H", '000\xb0'),( "SP", '0')])
#        self.disp_text8["GPS"] = RollingDialBox_multi(self.panel, -1, "GPS", gps, '0', 95,wx.BLACK,wx.VERTICAL)
#        self.hbox8.Add(self.disp_label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox8.Add(self.disp_label8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox8.Add(self.disp_text8["GPS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)




#        gps2=OrderedDict([("DT","DATE"),("TM","TIME")])
#        self.disp_label10= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", gps2, '0',50,wx.RED,wx.VERTICAL)
#        self.disp_text10 = OrderedDict([ ("GPSZDA", '')])
#        gps2 =OrderedDict([("ZDA_DATE",'d'), ("ZDA_TS", 't')])
#        self.disp_text10["GPSZDA"] = RollingDialBox_multi(self.panel, -1, "GPSZDA", gps2, '0', 90,wx.BLACK,wx.VERTICAL)
#        self.hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
# put in same box as the other gps stuff but next to it
#        self.hbox8.Add(self.disp_label10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox8.Add(self.disp_text10["GPSZDA"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.disp_text11 = OrderedDict([ ("DBS", '')])
#        xxw = OrderedDict([("DBS", 'dbs')])
#        self.disp_text11["DBS"] = RollingDialBox_multi(self.panel, -1, "DBS (m)",xxw, '0',80,wx.BLACK,wx.VERTICAL,afontsize)

        self.hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        self.disp_text11 = OrderedDict([("DBS", '')])

        x2 = OrderedDict([("DBS", '(DBS) Depth (m)')])
        self.disp_text11["DBS"] = RollingDialBox_multi(self.panel, -1, x2["DBS"], xx, '0', 80, wx.BLACK, wx.VERTICAL,
                                                      afontsize)
        self.hbox11.Add(self.disp_text11["DBS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)








        #        xxz = OrderedDict([("-", "Depth (m)"),])
#        self.disp_label12 = RollingDialBox_multi_static(self.panel, -1, "----  Channel  ----", xxz, '0', 90, wx.RED,
#                                                       wx.VERTICAL,afontsize)

#        self.disp_text12 = OrderedDict([("DP", '')])
#        xxw = OrderedDict([("R", 'h')])
#        self.disp_text12["DP"] = RollingDialBox_multi(self.panel, -1, "DP (m)", xxw, '0', 50, wx.BLACK, wx.VERTICAL,afontsize)

#        self.hbox12 = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox12.Add(self.disp_label12, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox12.Add(self.disp_text12["DP"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        xxz=OrderedDict([("X","Bottom Contact")])
#       self.disp_label3= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", xxz, '0',90,wx.RED,wx.VERTICAL)

#        self.disp_text13 = OrderedDict([ ("CON", '')])
#        xxz =OrderedDict([("R",u'OFF BTM')])
#        con_font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
#        self.disp_text13["CON"] = RollingDialBox_multi(self.panel, -1, "BTM Contact", xxz, '1', 70,wx.BLACK,wx.VERTICAL,afontsize)
#        self.disp_text13["CON"].SetFont(con_font)
#        self.disp_text13["CON"].Data_text['R'].SetBackgroundColour('PINK')

# wire  port values
#        wire=OrderedDict([("LEN","Length (m)"),("SPD","Speed (m/s)"),("TEN","Tension (T)")])
#        self.disp_label14= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", wire, '0',80,wx.RED,wx.VERTICAL,afontsize)


#        if self.SPW_tick.IsChecked():
#            self.disp_text14 = OrderedDict([("WP", '')])
#            wire = OrderedDict([("LEN", 'l'), ("SPD", 's'), ("TEN", 't')])
#            self.disp_text14["WP"] = RollingDialBox_multi(self.panel, -1, "value", wire, '0', 70, wx.BLACK, wx.VERTICAL)
#            self.hbox14 = wx.BoxSizer(wx.HORIZONTAL)
#            #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
#            self.hbox14.Add(self.disp_label14, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#            self.hbox14.Add(self.disp_text14["WP"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

    # wire starboard values
#        wire=OrderedDict([("LEN","Length (m)"),("SPD","Speed (m/s)"),("TEN","Tension-Tons")])
#        self.disp_label15= RollingDialBox_multi_static(self.panel, -1,"----  Channel  ----", wire, '0',80,wx.RED,wx.VERTICAL)

#        self.disp_text15 = OrderedDict([("WS", '')])
#        wire = OrderedDict([("LEN", 'l'), ("SPD", 's'), ("TEN", 't')])
#        self.disp_text15["WS"] = RollingDialBox_multi(self.panel, -1, "value", wire, '0', 70, wx.BLACK, wx.VERTICAL)
#        self.hbox15 = wx.BoxSizer(wx.HORIZONTAL)
        #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
#        self.hbox15.Add(self.disp_label15, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox15.Add(self.disp_text15["WS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)



        self.disp_BaseName = RollingDialBox(self.panel, -1, "Ship - Trip - Set","00-999-000", 200,wx.GREEN,wx.HORIZONTAL,afontbigger)

#        print self.BaseName

# add the dictionaries onto the main dictionaries
#        self.disp_text.update(self.disp_text2)
        self.disp_text.update(self.disp_text3)
        self.disp_text.update(self.disp_text4)
        self.disp_text.update(self.disp_text5)

        self.disp_text.update(self.disp_text8)
#        self.disp_text.update(self.disp_text10)
        self.disp_text.update(self.disp_text6)
        self.disp_text.update(self.disp_text11)
#        self.disp_text.update(self.disp_text12)
#        self.disp_text.update(self.disp_text13)
#        self.disp_text.update(self.disp_text14)
#        self.disp_text.update(self.disp_text15)
# Row 3   - buttoms and rate


#        self.hbox9 = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox9.Add(self.monitor_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(2)
#        self.hbox9.Add(self.LoggerRun_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(20)

#        self.hbox9.AddSpacer(10)
#        self.hbox9.Add(self.disp_text6["CLOCK"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(10)
#        self.hbox9.Add(self.disp_text11["DBS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(10)
#        self.hbox9.Add(self.disp_text13["CON"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(10)
#        self.hbox9.Add(self.disp_BaseName,border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox9.AddSpacer(10)



    # Put it all together

        self.VTBx = wx.StaticBox(self.panel,-1,"Door & Wing Sensors")
        self.VTbox = wx.StaticBoxSizer(self.VTBx, wx.HORIZONTAL)
        self.VTbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.InfoBx = wx.StaticBox(self.panel,-1,"INFO")
        self.Infobox = wx.StaticBoxSizer(self.InfoBx, wx.VERTICAL)
        self.Infobox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.Infobox.Add(self.disp_BaseName, 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        self.ETBx = wx.StaticBox(self.panel, -1, "ELAPSED TIME ON BOTTOM")
#        self.ETbox = wx.StaticBoxSizer(self.ETBx, wx.HORIZONTAL)
#        self.ETbox.Add(self.disp_text5["ET"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.TLTbx = wx.StaticBox(self.panel,-1,"Tilt")
#        self.TLTbox = wx.StaticBoxSizer(self.TLTbx, wx.HORIZONTAL)
#        self.TLTbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.TSPbx = wx.StaticBox(self.panel,-1,"Trawl Speed")
        self.TSPbox = wx.StaticBoxSizer(self.TSPbx, wx.VERTICAL)
        self.TSPbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.TSPbox.AddSpacer(8)
#        self.TSPbox.Add(self.hbox12, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.TSbx = wx.StaticBox(self.panel,-1,"Trawl Sounder")
        self.TSbox = wx.StaticBoxSizer(self.TSbx, wx.VERTICAL)
        self.TSbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.DBSbx = wx.StaticBox(self.panel,-1,"Ship Sounder")
        self.DBSbox = wx.StaticBoxSizer(self.DBSbx, wx.VERTICAL)
        self.DBSbox.Add(self.hbox11, 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        self.WPbx = wx.StaticBox(self.panel, -1, "Wire - Port")
#        self.WPbox = wx.StaticBoxSizer(self.WPbx, wx.HORIZONTAL)
#        self.WPbox.Add(self.hbox14, 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        self.WSbx = wx.StaticBox(self.panel, -1, "Wire - Starboard")
#        self.WSbox = wx.StaticBoxSizer(self.WSbx, wx.HORIZONTAL)
#        self.WSbox.Add(self.hbox15, 0, flag=wx.ALIGN_LEFT | wx.TOP)


        self.GPSbx = wx.StaticBox(self.panel,-1,"GPS")
        self.GPSbox = wx.StaticBoxSizer(self.GPSbx, wx.HORIZONTAL)
        self.GPSbox.Add(self.hbox8, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.GPSbox.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    def assemble_display(self):

#        self.FULL_PAGE = wx.FlexGridSizer(2, 1, 0, 0)
#        self.FULL_PAGE.SetFlexibleDirection(wx.BOTH)
#        self.FULL_PAGE.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.LRbox = wx.BoxSizer(wx.HORIZONTAL)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.VTbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.TSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(4)
        self.LRbox.Add(self.DBSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox.AddSpacer(10)
        self.LRbox.Add(self.Increment_button, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.LRbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.LRbox2.AddSpacer(4)
        self.LRbox2.Add(self.GPSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox2.AddSpacer(4)
        self.LRbox2.Add(self.TSPbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.LRbox2.AddSpacer(10)
        self.LRbox2.Add(self.Infobox, 0, flag=wx.ALIGN_LEFT | wx.TOP)


#        if self.SPW_tick.IsChecked():
#            self.LRbox2.Add(self.WPbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#            self.LRbox2.AddSpacer(4)
#        self.LRbox2.Add(self.WSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.LRbox2.AddSpacer(4)


#        self.LRbox3 = wx.BoxSizer(wx.HORIZONTAL)

#        self.LRbox3.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
#        self.vbox = wx.FlexGridSizer(wx.VERTICAL)
#        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW) Bongo graph
        self.vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.vbox.Add(self.textsizer, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.vbox.Add(self.ELbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.LRbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.LRbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.vbox.AddSpacer(4)
#        self.vbox.Add(self.LRbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        self.FULL_PAGE.Add(self.panel_1, 1, wx.EXPAND | wx.ALL, 5)
#        self.FULL_PAGE.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

#        self.SetSizer(self.FULL_PAGE)
#        self.Layout()
#        self.FULL_PAGE.Fit(self)

#        self.Centre(wx.BOTH)



# ***********************************************************
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

# ############################################

# *** ACTION METHODS ***************


    def OnWarpTyped(self, event):
        self.WarpOut = event.GetString()
        self.Warp_text.Enable(False)
#        self.Warp_button.Enable(False)
        self.mark_event("WARPENTER")
#        print event.GetValue()


    # if we hve no source, prompt to see of serial soruce desired (the normal)
    # else do nothing; if user wants play back they can choose it from main menu
    def on_LoggerStart_button(self, event):

        if not self.RT_source and not self.ARC_source:
            if self.Confirm_start_RT_dialogue(-1):
                self.on_start_rt(-1)
#                self.Startup_Data_Source()
            else:
                return()

        self.setup_new_tow()
        self.LoggeerRun = True
        self.LoggerStart_button.Enable(False)
        self.BottomStart_button.Enable(True)
        self.Abort_button.Enable(True)
        self.mark_event("INWATER")

    def on_BottomStart_button(self, event):
        self.flash_status_message("BOTTOM TOW STARTED at",time.time())
        self.OnBottom = True
        self.StartTime = 0
        self.BottomStart_button.Enable(False)
        self.Warp_button.Enable(True)
        self.BottomEnd_button.Enable(True)
        self.Warp_text.Enable(True)
        self.mark_event("ONBOTTOM")

    def on_Warp_button(self, event):
        self.Warp_text.Enable(True)
        self.Warp_text.SetFocus()
        self.warp_out = self.Warp_text.GetValue()
        self.warp_out = self.get_warp()


    def get_warp(self):
        return(self.Warp_text.GetValue())

    def on_BottomEnd_button(self, event):
        self.OnBottom = False
        self.BottomEnd_button.Enable(False)
        self.LoggerEnd_button.Enable(True)

        self.mark_event("OFFBOTTOM")


    def on_LoggerEnd_button(self, event):
        self.LoggerRun = False
        self.mark_event("OUTWATER")
        self.Warp_text.Enable(False)
        self.Warp_button.Enable(False)
        self.Shutdown_Data_Source()
#        self.close_files("SET")
        self.clear_all_buttons()

    def on_Abort_button(self, event):
            if self.Confirm_abort_dialogue(event):
                self.OnBottom = False
                self.LoggerRun = False
                self.mark_event("ABORT")
                self.Shutdown_Data_Source()
                self.abort_logging_file()
                self.clear_all_buttons()
                self.setup_new_tow()

    def on_Increment_tow_button(self, event):
        new= self.ShipTripSet["SET"]
        new2 = int(new)
        new2 = new2 + 1
        new3 = str(new2)
        new4 = new3.strip().zfill(3)


        print "SET",self.ShipTripSet["SET"],"|new=",new,"|new2=",new2,"|NEW3=",new3,"|new4=",new4,"|"
        if self.Confirm_Increment_dialogue(event,new4):
            self.ShipTripSet["SET"]  = new4
            self.basename = self.make_base_name()
            self.disp_BaseName.Data_text.SetValue(self.basename)


    def on_start_arc(self,event):
        self.RT_source = False
        self.ARC_source = True
        self.Startup_Data_Source()

    def on_stop_arc(self,event):
        self.RT_source = False
        self.ARC_source = False
        self.Shutdown_Data_Source()
        self.clear_all_buttons()

    def on_start_rt(self, event):
        self.RT_source = True
        self.ARC_source = False
        self.Startup_Data_Source()

    def on_stop_rt(self, event):
        self.RT_source = False
        self.ARC_source = False
        self.Shutdown_Data_Source()
        self.clear_all_buttons()


#   def on_LoggerRun_button(self, event):
#       if  not self.DataSource == None :
#           self.LoggerRun = not self.LoggerRun
#           self.on_update_LoggerRun_button(event)
#           if self.LoggerRun == True:
#               self.MonitorRun = True
#               self.on_update_monitor_button(event)
#
#   def on_monitor_button(self, event):
#       if  self.DataSource != None :
#         self.DataSource.flush()
#         self.DataSource.start_data_feed()
#         self.StartTime = 0
#         self.MonitorRun = not self.MonitorRun
#         self.on_update_monitor_button(event)
#         if self.MonitorRun == False:  # if monitor is stopped then also stop logging
#           self.LoggerRun = False
#           self.DataSource.pause_data_feed()   # pause data feed; for serial waste-gate; for file just pause reead
#           self.on_update_LoggerRun_button(event)
#


# ################ TEST STUFF _ INGORE ~~~~~~~~~~~~
#    def   on_port_wire(self,event):
#        if self.SPW_tick.IsChecked():
#            self.WPbx.Show(True)
#            self.hbox14.Show(True)
#            self.disp_label14.Show(True)
#            print "showing"
#        else:
#            self.WPbx.Show(False)
#            self.hbox14.Show(False)
#            self.disp_label14.Hide()

#            print "hiding"
#        self.Layout()
#        self.Fit()

#        self.SendSizeEvent()

    def onF4(self, event):
        print "F4 hit",event

    def onF2(self, event):
       print "F2 hit",event
# ########### -----------------------------------
            
################### ON_REDRAW_TIMER ##########################################################
# This method is repeatably called by the re-draw timer to get any new data
# what it does depends on the STATE variables
##############################################################################################

    def on_redraw_timer(self, event):

        self.Tstr = '0'
        ETstr ='0'


        # working variables with no persistence outside this routine or across calls to it

        Raw_String = OrderedDict()
        dttm = str(datetime.now())
        dt =  time.strftime('%Y-%m-%d\n%H:%M:%S')
        self.disp_text["CLOCK"].Data_text.SetValue(str(dt))


        # If a data source has not been defined do nothing on this pass
        if self.DataSource == None :
            return()

        if  not self.MonitorRun :
            # if we have a data source but are not monitoring
            # is source is live serial the data is just waste gated
            # if the source is a file the reader pauses
            self.DataSource.pause_data_feed()
            return()
        else :
            # process the available data to screen etc, so retrieve a block of input else return to try later
            if not self.BQueue.empty():
                tries = 0
                block = self.BQueue.get()
            else:
#                print "Empty Queue"
                return()

#            block =self.DataSource.next()

        # This is the elapsed time since the start of monitoring the bottom section
        if self.OnBottom:
            if self.StartTime == 0:
                self.StartTime = datetime.now()
                ET = 0
            else:
                Et = datetime.now() - self.StartTime
                self.disp_text["ET"].Data_text["ET"].SetValue(str(timedelta(seconds=Et.seconds)))


# process the block of data
        if block["OK"]:
            for sentence_type in block:
                if sentence_type != "OK" and sentence_type != "REASON":     #skip these house keepers flag dict elements
                    self.smn_tools.dispatch_message(sentence_type,block[sentence_type],self.disp_text,Raw_String,self.JDict)
                else:
                    pass

        else:
            if block["REASON"] == "FINISHED" :
                self.flash_status_message("DATA SOURCE SIGNALLED FINISHED")
                if self.ARC_source:
                    self.on_stop_arc(-1)
                else :
                    self.on_stop_rt(-1)
            return()

        if self.LoggerRun:
#            print "OUTPUT.."

            self.write_RawData(Raw_String)
            self.write_Jdata(self.JDict)
            self.write_CSVdata(self.JDict)
        # end of if LoggerRun
        # end of for sentence in block...



######################## Menu things ########################

# #############################################################################
#  Note:  These Consol messages seem to occur when FileDialog is used on a PC running ViewFinity
#    D_Lib: debug    printing    for files[. *] and level[100] is turned on
#    D_Lib: debug    printing    for files[. *] and level[200] is turned on
#    D_Lib: debug    printing    for files[. *] and level[300] is turned on
# ########################################################################

    def save_file_dialog(self):
        """Save contents of output window."""
        CSV_outfilename = self.ShipTripSet["SHIP"]+self.ShipTripSet["TRIP"]+self.ShipTripSet["SET"]
        dlg = wx.FileDialog(None, "Save File As...", "", "", "ScanMar Proc log|*.csv|All Files|*",  wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() ==  wx.ID_OK:
            CSV_outfilename = dlg.GetPath()
        dlg.Destroy()
        return (CSV_outfilename)
    
    def get_file_dialog(self):
        filename = None
        dialog = wx.FileDialog(None, "Choose File.",os.getcwd(), "", "ScanMar Raw Log|*.log|All Files|*",wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            filename =  dialog.GetPath()  
        dialog.Destroy()
        return(filename)

    def make_base_name(self):
         return(self.ShipTripSet["SHIP"]+self.ShipTripSet["TRIP"]+self.ShipTripSet["SET"])

         ########################################################
         # dialog to verify abort

    def Confirm_abort_dialogue(self, event):
        dlg = wx.MessageDialog(self, "Want to Abort?", "Abort", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            return (True)
        else:
            return (False)

    def Confirm_Increment_dialogue(self,event,new_set):
        print  new_set
        dlg = wx.MessageDialog(self, "Increment set # to "+new_set, "Newset", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            return (True)
        else:
            return (False)


    def Confirm_start_RT_dialogue(self, event):
        dlg = wx.MessageDialog(self, "Raeltime data not selected.\nOpen feed from Scanmar and continue?", "RT Feed y/n", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            return (True)
        else:
            return (False)

    def mark_event(self,flag):

        self.log1.AppendText("  "+"{:<10}".format(flag)+" "+self.BaseName+" "+ self.JDict["DATETIME"]+"  "+self.JDict["DBS"]+"  "+self.JDict["DP_1_H"]["measurement_val"]+"   "+ self.JDict["LAT"]+"  "+self.JDict["LON"])


    def abort_logging_file(self):
        pass

    def clear_all_buttons(self):
        self.LoggerStart_button.Enable(True)
        self.BottomStart_button.Enable(False)
        self.BottomEnd_button.Enable(False)
        self.LoggerEnd_button.Enable(False)
        self.Abort_button.Enable(False)
        pass

    def setup_new_tow(self):
        pass

    def set_FileNames(self):
        self.BaseName = self.make_base_name()
#        self.disp_BaseName.Data_text.SetValue(str(self.BaseName))

        self.disp_BaseName.Data_text.SetValue(str(self.BaseName[0:2]+"-"+self.BaseName[2:5]+"-"+self.BaseName[5:8]))
        self.CSVFileName = self.BaseName +".csv"
        self.RAWFileName = self.BaseName +".raw"
        self.JSONFileName = self.BaseName +".json"

    def write_Jdata(self,JDict):
        if self.JSON_fp == None:
            self.JSON_fp = open(self.JSONFileName, "w")
        X = json.dumps(JDict)
        self.JSON_fp.write(X+'\n')

    def write_CSVdata(self,JDict):
            if self.CSV_fp ==None:
                self.CSV_fp= open(self.CSVFileName,"w")

                for ele, val in JDict.iteritems():
                    if isinstance(val, dict):
                        for k, v in val.items():
                            self.CSV_fp.write(k + ',', )
                    else:
                        self.CSV_fp.write(ele + ',', )
#                self.CSVwriter = csv.writer(self.CSV_fp)
#                self.CSVwriter.writerow(JDict.keys())
            else:
                for ele, val in JDict.iteritems():
                    if isinstance(val, dict):
                        for k, v in val.items():
                            self.CSV_fp.write(str(v) + ',', )
                    else:
                        self.CSV_fp.write(str(val) + ',', )
            self.CSV_fp.write('\n')

#                self.CSVwriter.writerow(JDict.values())


    def write_RawData(self,Raw_String):
        if  self.RAW_fp == None:
            self.RAW_fp = open(self.RAWFileName,"w")

        for zz in Raw_String :
            self.RAW_fp.write(str(Raw_String[zz]) + '\n')


            
# Configure serial port, requires our serial instance, make sure port is closed before calling
    def on_ser_config(self,event):
#        self.ser.close()
        self.read_cfg()
        dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "",
                show=wxSerialConfigDialog.SHOW_BAUDRATE|wxSerialConfigDialog.SHOW_FORMAT|wxSerialConfigDialog.SHOW_FLOW,
                serial=self.ser
            )
        result = dialog_serial_cfg.ShowModal()
        dialog_serial_cfg.Destroy()
        self.save_cfg()



# RT start button pressed on main menu RT pull down - note this is the default mode
    def Startup_Data_Source (self):

        menubar = self.menubar

        if self.RT_source :
            ID_START = ID_START_RT
            ID_STOP = ID_STOP_RT
            self.DataSource = DataGen_que(self, "SERIAL", self.ser, self.BQueue)
#            self.DataSource = DataGen_que(self, "SERIAL", self.ser)  # Create a data source instance
            menubar.EnableTop(2, False)  # lock out ARC playback while RealTime running
        else: # ARC_SOURCE
            FileName = self.get_file_dialog()  # get filename of logged file
            if FileName != None:

                Source = "ARCHIVE"
                self.DataSource = DataGen_que(self, "ARCHIVE", FileName, self.BQueue)
#                self.DataSource = DataGen_que(self,"ARCHIVE", FileName)  # Create a data source instance
                menubar.EnableTop(1, False)  # lock out RT playback while Archived running
                ID_START = ID_START_ARC
                ID_STOP = ID_STOP_ARC
            else:
                self.ARC_source = False
                return()


        enabled = menubar.IsEnabled(ID_START)  # reverse the menu items
        menubar.Enable(ID_START,not enabled)
        enabled = menubar.IsEnabled(ID_STOP)
        menubar.Enable(ID_STOP,not enabled)

        menubar.Enable(ID_SER_CONF, False)  # lock out serial config while running

        self.settings = {}

        self.MonitorRun = True
        self.DataSource.start()
        self.DataSource.start_data_feed()


#        if self.DataSource != None:
#            #          self.DataSource.flush()
#            self.DataSource.start_data_feed()
#            self.StartTime = 0

#        if not self.BaseName != None:
#            self.flash_status_message("OPENING FILES FOR OUTPUT Prefix = " + self.BaseName)
#        else:
#            self.flash_status_message("NO LOGFILE SPECIFIED NOT LOGGING TO FILE")
#            self.LogFileName = "NOT LOGGING TO FILE"


# *****************************************************************

    def Shutdown_Data_Source (self):

        if self.RT_source == True:
            try:
              self.close_files("ALL")
            except: pass
        
            self.RT_source = False
            self.ARC_source = False

        if self.RT_source :
            ID_START = ID_START_RT
            ID_STOP = ID_STOP_RT

        else:
            ID_START = ID_START_ARC
            ID_STOP = ID_STOP_ARC

        # reset the menu items to startup defaults
        menubar = self.GetMenuBar()
        menubar.EnableTop(1, True)  # turn back on menus
        menubar.EnableTop(2, True)

        menubar.Enable(ID_START_RT,True)
        menubar.Enable(ID_START_ARC,True)
        menubar.Enable(ID_STOP_RT,False)
        menubar.Enable(ID_STOP_ARC,False)

        menubar.Enable(ID_SER_CONF, True)

        if self.DataSource != None:
            self.DataSource.flush()
            self.DataSource.close_DataSource()
            self.DataSource = None
            self.StartTime = 0

        self.MonitorRun = False

        
#************************ archieve data ***************************
    def on_start_arc_old(self):
        FileName = self.get_file_dialog()  #get filename of logged file
        if FileName !=None :
            self.RT_source = False
            self.ARC_source = True
#            self.host.set_title('Bongo trace data file= '+FileName, size=8) # label plot
            menubar = self.GetMenuBar()
            enabled = menubar.IsEnabled(ID_START_ARC)
            menubar.Enable(ID_START_ARC,not enabled)
            enabled = menubar.IsEnabled(ID_STOP_ARC)
            menubar.Enable(ID_STOP_ARC,not enabled)
            menubar.EnableTop(1, False)  # lock out RT playback while Archieved running

            self.DataSource = DataGen_que(self,"ARCHIVE",FileName) #Create a data source instance
            self.MonitorRun = True
            self.start_data_feed()



    def on_stop_arc_old (self, event):
        if self.ARC_source:
            self.ARC_source = False
            self.DataSource.close_DataSource()
            self.MonitorRun = False
        self.DataSource = None

        menubar = self.GetMenuBar()
        enabled = menubar.IsEnabled(ID_START_ARC)
        menubar.Enable(ID_START_ARC,not enabled)
        enabled = menubar.IsEnabled(ID_STOP_ARC)
        menubar.Enable(ID_STOP_ARC,not enabled)

#        self.monitor_button.Enable(False)
#        self.LoggerRun_button.Enable(False)

        menubar.EnableTop(1, True)  # re-enable realtime data option

    def on_edit_head(self,event):
        if self.RT_source == True:
            self.on_stop_rt (1)
#        WINAQU_GUI_BONGO.main()

    def on_set_base_header(self,event):
        xx = ShipTrip_Dialog(self)
#        print "before ",self.ShipTripSet

        xx.SetBase(self.ShipTripSet["SHIP"],self.ShipTripSet["TRIP"],self.ShipTripSet["SET"])
        res=xx.ShowModal()
        if res == wx.ID_OK:
#            print "After " , self.ShipTripSet
            self.ShipTripSet["SHIP"] = xx.GetShip()
#            self.hship = xx.GetShip()
            self.ShipTripSet["TRIP"] = xx.GetTrip()
            self.ShipTripSet["SET"] = xx.GetStn()
#            print "AFTER=",self.ShipTripSet
#            self.hship="LL"
            self.basename = self.make_base_name()
            self.disp_BaseName.Data_text.SetValue(self.basename)

            self.set_FileNames()

            xx.Destroy()

    def read_cfg(self):
        try:
            with open('ScanMar.CFG', 'r') as fp:
                commsettings = json.load(fp)
                self.ser.applySettingsDict(commsettings)
            fp.close()
        except:
            pass


    def save_cfg(self):
        comsettings = self.ser.getSettingsDict()
        print comsettings
        with open('ScanMar.CFG', 'w') as fp:
            fp.write(json.dumps(comsettings))
        fp.close()


    #******************* assorted  methods ****************************************************

#    def WriteHeader (self,fp) :
#        print "In WRite "+self.hd1["SHIP"]

#        xtime = '{:>5.5}'.format(str(datetime.datetime.now().time()))
#        xdate = '{:>12.12}'.format(str(datetime.datetime.now().date()))
#        hdr1_out= self.hd1["SHIP"].strip().zfill(2)+ self.hd1["TRIP"].strip().zfill(3)+ self.hd1["STN"].strip().zfill(3)
#        fp.write("NAFC_Y2K_HEADER\n")
#        fp.write (hdr1_out+"                    "+xdate+" "+xtime+"      12     O                1\n")
#        fp.write (hdr1_out+" 000000 01.00 A 12 #ZEPTCSMWwLV--------              000 0000 0000 000 4\n")
#        fp.write (hdr1_out+"                                                                       8\n")
#        fp.write ("SCAN CtdClk   ET   DEPTH    TEMP  COND   SAL   SIGMAT   FLOW1   FLOW2  LIGHT   VOLTS\n")
#        fp.write ("-- DATA --\n")

    def close_files(self,Which):
        if Which == "ALL" :
            try:
                self.TripLog_fp.close()
            except:
                pass

        try:
            self.JSON_fp.close()
        except:
            pass
        self.flash_status_message("CLOSING FILES...")

        try:
            self.RAW_fp.close()
        except:
            pass
        try:
            self.CSV_fp.close()
        except:
            pass


    
    def on_exit(self, event):
        self.redraw_timer.Stop()
        self.Shutdown_Data_Source()
        self.close_files("ALL")
#        self.Close(True)
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=2000):
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
        info.SetCopyright ("Note: See Source for any 3rd party credits")
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
