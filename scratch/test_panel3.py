import wx
import wx.lib.scrolledpanel as scrolled


class Input_Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Input variables
        self.parent = parent
#        self.tittle1 = wx.StaticText(self, label="Inputs:")
#        self.lblname1 = wx.StaticText(self, label="Input 1:")
#        self.format1 = ['Option 1','Option 2']
#        self.combo1 = wx.ComboBox(self, size=(200, -1),value='', choices=self.format1,style=wx.CB_DROPDOWN)
#        self.lblname2 = wx.StaticText(self, label="Input 2")
#        self.format2 = ['Option 1','Option 2', 'Option 3']
#        self.combo2 = wx.ComboBox(self, size=(200, -1),value='', choices=self.format2, style=wx.CB_DROPDOWN)
        buttonfont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.LoggerStart_button = wx.Button(self, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button.SetFont(buttonfont)
        self.LoggerStart_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_logger_start_button, self.LoggerStart_button)


        self.LoggerStart_button2 = wx.Button(self, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button2.SetFont(buttonfont)
        self.LoggerStart_button3 = wx.Button(self, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button3.SetFont(buttonfont)
        self.LoggerStart_button4 = wx.Button(self, -1, "   warp")
        self.LoggerStart_button4.SetFont(buttonfont)
        self.LoggerStart_button5 = wx.Button(self, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button5.SetFont(buttonfont)
        self.LoggerStart_button6 = wx.Button(self, -1, "   In Water  \nStart Logging\n(F1)")
        self.LoggerStart_button6.SetFont(buttonfont)
        self.LoggerStart_button7 = wx.Button(self, -1, "   abort")
        self.LoggerStart_button7.SetFont(buttonfont)




        # Set sizer for the panel content

#        self.sizer = wx.GridBagSizer(2, 2)

#       self.sizer.Add(self.tittle1, (1, 2))
#        self.sizer.Add(self.lblname1, (2, 1))
#        self.sizer.Add(self.combo1, (2, 2))
#        self.sizer.Add(self.lblname2, (3, 1))
#        self.sizer.Add(self.combo2, (3, 2))
#        self.sizer.Add(self.LoggerStart_button,(3,0))

        self.buttonsizer= wx.GridBagSizer(1, 7)

        self.buttonsizer.Add(self.LoggerStart_button, (0, 0))
        self.buttonsizer.Add(self.LoggerStart_button2, (0, 1))
        self.buttonsizer.Add(self.LoggerStart_button3, (0, 2))
        self.buttonsizer.Add(self.LoggerStart_button4, (0, 3))
        self.buttonsizer.Add(self.LoggerStart_button5, (0, 4))
        self.buttonsizer.Add(self.LoggerStart_button6, (0, 5))
        self.buttonsizer.Add(self.LoggerStart_button7, (0, 6))


        x = 1200
        y = 200
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.SUNKEN_BORDER | wx.VSCROLL

        self.label = wx.StaticText(self,
                                   label="    EVENT     STATION    DATE       TIME     BTM-D  TWL_DEP     LAT           LONG")
        self.log1 = wx.TextCtrl(self, wx.ID_ANY, size=(x, y), style=style)

        logfont = wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.log1.SetFont(logfont)
        self.label.SetFont(logfont)



#        self.sizer = wx.BoxSizer(wx.VERTICAL)
#        self.sizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
#        self.sizer.Add(self.log1, 1, wx.ALL | wx.EXPAND, 5)


        self.textsizer = wx.GridBagSizer(2, 2)
        self.textsizer.Add(self.label, (0, 1))
        self.textsizer.Add(self.log1, (1, 1))

        self.sizer = wx.GridBagSizer(2, 1)
        self.sizer.Add(self.buttonsizer, (0, 0))
        self.sizer.Add(self.textsizer, (1, 0))
#        self.sizer.Add(self.LoggerStart_button,1,wx.ALL|wx.EXPAND,5)
#        self.sizer.Add(self.textsizer,1,wx.ALL|wx.EXPAND,5)
#        self.sizer.Add(self.label,1,wx.ALL|wx.EXPAND,5)
#        self.sizer.Add(self.log1, 1,wx.ALL|wx.EXPAND,5)
        self.SetSizer(self.sizer)

        self.log1.AppendText("  START_FILE 39222001  2017-10-25 10:15:12   0340    0000    47 32.455 N   50 25.174 W\n")
        self.log1.AppendText("  START_TOW  39222001  2017-10-25 10:40:25   0345    0329    47 32.485 N   50 25.184 W\n")
        self.log1.AppendText("  END_TOW    39222001  2017-10-25 10:55:55   0342    0340    47 32.490 N   50 25.204 W\n")
        self.log1.AppendText("  END_FILE   39222001  2017-10-25 11:20:02   0313    0000    47 32.499 N   50 25.234 W\n")

        self.log1.AppendText("  START_FILE 39222002  2017-10-25 10:15:12   0340    0000    47 32.455 N   50 25.174 W\n")
        self.log1.AppendText("  START_TOW  39222002  2017-10-25 10:40:25   0345    0329    47 32.485 N   50 25.184 W\n")
        self.log1.AppendText("  END_TOW    39222002  2017-10-25 10:55:55   0342    0340    47 32.490 N   50 25.204 W\n")
        self.log1.AppendText("  END_FILE   39222002  2017-10-25 11:20:02   0313    0000    47 32.499 N   50 25.234 W\n")

    def on_logger_start_button(self,event):
        print "hello"
        self.log1.AppendText("  END_FILE   39222003  2017-10-25 11:20:02   0313    0000    47 32.499 N   50 25.234 W\n")

class TestPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        desc = wx.StaticText(self, -1,
                             "ScrolledPanel extends wx.ScrolledWindow, adding all "
                             "the necessary bits to set up scroll handling for you.\n\n"
                             "Here are three fixed size examples of its use. The "
                             "demo panel for this sample is also using it -- the \nwxStaticLine "
                             "below is intentionally made too long so a scrollbar will be "
                             "activated."
                             )
        desc.SetForegroundColour("Blue")
        vbox.Add(desc, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.SetSizer(vbox)
        self.SetAutoLayout(1)
        self.SetupScrolling()
#        desc.SetLabel("test")
#        desc.SetLabelText("testlabeltext")


class Output_Scrolled_Panel1(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

    # --------------------
    # Scrolled panel stuff

        self.scrolled_panel = scrolled.ScrolledPanel(self, -1,
                                                     style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, name="panel1")
        self.scrolled_panel.SetAutoLayout(1)
        self.scrolled_panel.SetupScrolling()

        words = "A Quick Brown Insane Fox Jumped Over the Fence and Ziplined to Cover".split()
        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        for word in words:
            text = wx.TextCtrl(self.scrolled_panel, value=word)
            self.spSizer.Add(text)

        self.scrolled_panel.SetSizer(self.spSizer)
        # --------------------
        btn = wx.Button(self, label="Add Widget")
        btn.Bind(wx.EVT_BUTTON, self.onAdd)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.AddSpacer(50)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        panelSizer.Add(btn)
        self.SetSizer(panelSizer)

    def onAdd(self, event):
        """"""
        print "in onAdd"
        new_text = wx.TextCtrl(self.scrolled_panel, value="New Text")
        self.spSizer.Add(new_text)
        self.scrolled_panel.Layout()
        self.scrolled_panel.SetupScrolling()

class Output_Panel1(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Output variables
#        self.tittle2 = wx.StaticText(self, label="Outputs:")
#        self.lblname3 = wx.StaticText(self, label="Output1")
#        self.result3 = wx.StaticText(self, label="", size=(100, -1))



        #        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL |wx.VSCROLL |wx.SUNKEN_BORDER| wx.TE_NO_VSCROLL
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.SUNKEN_BORDER | wx.VSCROLL

        x = 800
        y = 125

#        log1_title = wx.StaticText(self, label="End_File")


        self.label = wx.StaticText(self,label= "    EVENT     STATION    DATE       TIME     BTM-D  TWL_DEP     LAT           LONG")
        self.log1 = wx.TextCtrl(self, wx.ID_ANY, size=(x, y), style=style)

        logfont = wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.log1.SetFont(logfont)
        self.label.SetFont(logfont)

#        blox1 = wx.BoxSizer(wx.HORIZONTAL)
#        blox1.Add(log1_title, 1, wx.ALL | wx.EXPAND, 5)
#        blox1.Add(self.log1, 1, wx.ALL | wx.EXPAND, 5)

        #        self.log2 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
        #        self.log3 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
        #        self.log4 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
        #        self.log5 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
        #        x,y = self.log.GetTextExtent("T")
        #        print x,y
        #        N = 160
        #        self.log = wx.TextCtrl(self, wx.ID_ANY, style=style)
        #        self.log.SetMinSize(wx.Size(x * N + 10, -1))
        #        self.log.SetMaxSize(wx.Size(x * N + 10, -1))

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.log1, 1, wx.ALL | wx.EXPAND, 5)
        #        sizer.Add(self.log2, 1, wx.ALL | wx.EXPAND, 5)
        #        sizer.Add(self.log3, 1, wx.ALL | wx.EXPAND, 5)
        #        sizer.Add(self.log4, 1, wx.ALL | wx.EXPAND, 5)
        #        sizer.Add(self.log5, 1, wx.ALL | wx.EXPAND, 5)
#        self.SetSizerAndFit(sizer)

        #        self.logger_txt.Enable(False)


#        self.hbox0a = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox0a.Add(self.logger_txt, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)



        # Set sizer for the panel content
#        self.sizer = wx.GridBagSizer(2, 2)
#        self.sizer.Add(self.tittle2, (1, 2))
#        self.sizer.Add(self.lblname3, (2, 1))
#        self.sizer.Add(self.result3, (2, 2))
#        self.sizer.Add(self.logger_txt,(3,3))
        self.SetSizer(sizer)




#        self.logger_txt.log3.SetValue("Test3\n")
#        self.logger_txt.log4.SetValue("Test4\n")
#        self.logger_txt.log5.SetValue("Test5\n")
        self.log1.AppendText("  START_FILE 39222001  2017-10-25 10:15:12   0340    0000    47 32.455 N   50 25.174 W\n")
        self.log1.AppendText("  START_TOW  39222001  2017-10-25 10:40:25   0345    0329    47 32.485 N   50 25.184 W\n")
        self.log1.AppendText("  END_TOW    39222001  2017-10-25 10:55:55   0342    0340    47 32.490 N   50 25.204 W\n")
        self.log1.AppendText("  END_FILE   39222001  2017-10-25 11:20:02   0313    0000    47 32.499 N   50 25.234 W\n")

        self.log1.AppendText("  START_FILE 39222002  2017-10-25 10:15:12   0340    0000    47 32.455 N   50 25.174 W\n")
        self.log1.AppendText("  START_TOW  39222002  2017-10-25 10:40:25   0345    0329    47 32.485 N   50 25.184 W\n")
        self.log1.AppendText("  END_TOW    39222002  2017-10-25 10:55:55   0342    0340    47 32.490 N   50 25.204 W\n")
        self.log1.AppendText("  END_FILE   39222002  2017-10-25 11:20:02   0313    0000    47 32.499 N   50 25.234 W\n")

#        self.log1.AppendText("C12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("D12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("E12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("F12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("G12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("H12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("I12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")
#        self.log1.AppendText("J12345 6789012345678901 2345678901234567890123456789012345678901234567890123456789\n")








class Output_Panel2(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Output variables
        self.tittle2 = wx.StaticText(self, label="Outputs:")
        self.lblname3 = wx.StaticText(self, label="Output1")
        self.result3 = wx.StaticText(self, label="", size=(100, -1))

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(2, 2)
        self.sizer.Add(self.tittle2, (1, 2))
        self.sizer.Add(self.lblname3, (2, 1))
        self.sizer.Add(self.result3, (2, 2))
        self.SetSizer(self.sizer)

# ##################### Multi line static text box for log output
class multiline_text_static(wx.Panel):
    """ Displays the realtime data values, even when graph is paused. size = 50 for most
            self.dvtlam_text = RollingDialBox(self.panel, -1, "DVTLAM", '0',50)
    """

    def __init__(self, parent, ID):
        wx.Panel.__init__(self, parent, ID)

#        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL |wx.VSCROLL |wx.SUNKEN_BORDER| wx.TE_NO_VSCROLL
        style = wx.TE_MULTILINE | wx.TE_READONLY  |wx.SUNKEN_BORDER |wx.VSCROLL

        x= 1000
        y=125


        log1_title= wx.StaticText(self, label="End_File")
        self.log1 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
        y=25

        blox1 = wx.BoxSizer(wx.HORIZONTAL)
        blox1.Add(log1_title, 1, wx.ALL | wx.EXPAND, 5)
        blox1.Add(self.log1, 1, wx.ALL | wx.EXPAND, 5)

#        self.log2 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
#        self.log3 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
#        self.log4 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
#        self.log5 = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
#        x,y = self.log.GetTextExtent("T")
#        print x,y
#        N = 160
#        self.log = wx.TextCtrl(self, wx.ID_ANY, style=style)
#        self.log.SetMinSize(wx.Size(x * N + 10, -1))
#        self.log.SetMaxSize(wx.Size(x * N + 10, -1))

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(blox1, 1, wx.ALL | wx.EXPAND, 5)
#        sizer.Add(self.log2, 1, wx.ALL | wx.EXPAND, 5)
#        sizer.Add(self.log3, 1, wx.ALL | wx.EXPAND, 5)
#        sizer.Add(self.log4, 1, wx.ALL | wx.EXPAND, 5)
#        sizer.Add(self.log5, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizerAndFit(sizer)

         # redirect text here
#        sys.stdout = log



class Main_Window(wx.Frame):
    def __init__(self, parent, title):
#        wx.Frame.__init__(self, parent, title = title, pos = (0, 0)  , size = wx.DisplaySize())
        wx.Frame.__init__(self, parent, title = title, size = (1280,800))



        # Set variable panels
        self.main_splitter = wx.SplitterWindow(self)
        self.out_splitter = wx.SplitterWindow(self.main_splitter)

        self.inputpanel = Input_Panel(self.main_splitter)
        self.inputpanel.SetBackgroundColour('#c4c4ff')

        self.outputScrolledpanel1 = Output_Scrolled_Panel1(self.out_splitter)
        self.outputScrolledpanel1.SetBackgroundColour('#c2b1f5')

        outputpanel1 = Output_Panel1(self.out_splitter)
        outputpanel1.SetBackgroundColour('#c2f1f5')

#        self.outputpanel1 = TestPanel(self.out_splitter)
#        self.outputpanel1.SetBackgroundColour('#c2d103')

        self.outputpanel2 = Output_Panel2(self.out_splitter)
        self.outputpanel2.SetBackgroundColour('#c2f103')

        self.main_splitter.SplitHorizontally(self.inputpanel, self.out_splitter)
        self.out_splitter.SplitHorizontally(outputpanel1, self.outputpanel2)

        self.main_splitter.SetSashPosition(400)  # set depth of top panel
        self.out_splitter.SetSashPosition(130)  # set depth of middle panel



def main():
    app = wx.App(False)
    frame = Main_Window(None, "App GUI")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__" :
    main()