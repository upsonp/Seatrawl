import wx

class Input_Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Input variables
        self.tittle1 = wx.StaticText(self, label="Inputs:")
        self.lblname1 = wx.StaticText(self, label="Input 1:")
        self.format1 = ['Option 1','Option 2']
        self.combo1 = wx.ComboBox(self, size=(200, -1),value='', choices=self.format1,style=wx.CB_DROPDOWN)
        self.lblname2 = wx.StaticText(self, label="Input 2")
        self.format2 = ['Option 1','Option 2', 'Option 3']
        self.combo2 = wx.ComboBox(self, size=(200, -1),value='', choices=self.format2, style=wx.CB_DROPDOWN)

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(2, 2)
        self.sizer.Add(self.tittle1, (1, 2))
        self.sizer.Add(self.lblname1, (2, 1))
        self.sizer.Add(self.combo1, (2, 2))
        self.sizer.Add(self.lblname2, (3, 1))
        self.sizer.Add(self.combo2, (3, 2))
        self.SetSizer(self.sizer)

class Output_Panel1(wx.Panel):
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



class Main_Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title = title, pos = (0, 0), size = wx.DisplaySize())

        # Set variable panels
        self.main_splitter = wx.SplitterWindow(self)
        self.out_splitter = wx.SplitterWindow(self.main_splitter)
        self.inputpanel = Input_Panel(self.main_splitter)
        self.inputpanel.SetBackgroundColour('#c4c4ff')
        self.outputpanel1 = Output_Panel1(self.out_splitter)
        self.outputpanel1.SetBackgroundColour('#c2f1f5')
        self.outputpanel2 = Output_Panel2(self.out_splitter)
        self.outputpanel2.SetBackgroundColour('#c2f103')
        self.main_splitter.SplitVertically(self.inputpanel, self.out_splitter)
        self.out_splitter.SplitHorizontally(self.outputpanel1, self.outputpanel2)
        self.main_splitter.SetSashPosition(600)  # set width of left panel
        self.out_splitter.SetSashPosition(600)  # set width of left panel


def main():
    app = wx.App(False)
    frame = Main_Window(None, "App GUI")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__" :
    main()