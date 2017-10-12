import serial
import time
import threading
import Queue
import ScanMarNmea as SMN
import pynmea2

DEFAULT_COM = "COM1"
DEFAULT_BAUD = 1200
DEFAULT_RATE = 1   # scans per second
SIMULATOR = False

########################################################################################
#  SERIAL PORT STD READER CLASS
# non threaded version  reads data from port when asked via next method
# initialization
#
# for linux
# ser.port = "/dev/ttyS2"
# for windows
# ser.port ="COM1"
#
# Possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call
#
# ser.timeout = None          #blocking read when using radline
# ser.timeout = 0             #non-block read
########################################################################################
class SerialSource():

    def __init__(self ,parent ,serial):
        self.parent = parent                # needed to call the flash status bar method of Graphframe
        self.ser = serial
        self.StartTime = 0
        self.set_default()
# Convert Class takes the data as read and translates it as and if  required
        self.Convert =ConvertClass()
        self.scan = dict()

    def set_default (self):
        self.ser.port = DEFAULT_COM
        self.ser.baudrate = DEFAULT_BAUD
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self.ser.timeout = 5  # timeout block read
        self.ser.xonxoff = True  # disable software flow control
        self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2  # timeout for write

    def open_Port(self):
        try:
            self.ser.open()
        except Exception, e:
#            print "error open serial port: "+self.ser.port+" " + str(e)
             return(False)

        self.parent.flash_status_message("PORT OPEN "+self.ser. getPort())

        return (True)

    def flush (self):
        self.ser.flushInput()
        line = self.ser.readline()  # ensure a full line is in buffer by discarding any stub

    def next(self):

        if self.StartTime == 0:
            self.StartTime = time.time()

        text = self.ser.readline()
        if text == "":  # this is due to Cr-Lf show as 2 lines which requires the (LF)to be flushed
            text = self.ser.readline()

        if text =="" :
            self.scan["OK"] = False
            return(self.scan)
        else :
            line = text.split()
            if SIMULATOR :
                scan = self.Convert.convert_simulation_b95(line)
#             scan = self.Convert.convert_archived(line)
                scan["Et"]= str(time. time() - self.StartTime)
            else:
                scan = self.Convert.convert_raw(line)
        return (scan)

    def send_wake(self):
        self.parent.flash_status_message("WAKING STD")
        self.ser.write("\r\r\r")
        self.ser.readline()

    def send_Real(self):
        self.parent.flash_status_message("SENDING REAL")
        self.ser.write("REAL\r")
        self.ser.readline()  # echo plus Cr-Lf which requires the 2nd read
        self.ser.readline()
        time.sleep(1.0)

    def send_Start_STD_Data(self):
        self.ser.write("M\r")
        time.sleep(2.0)
        self.flush()
        self.parent.flash_status_message("STD DATA STARTED")

    def send_Stop_STD_Data(self):
        self.ser.write ("\r")
        self.flush()
        self.parent.flash_status_message("STD DATA STOPPED")

    def send_Set_Rate(self,rate):
        self. parent.flash_status_message("SETTING STD DATA RATE = "+ rate+ " SCANS PER SECOND" )
        self.ser.write("SET S "+rate+"\r"); self.ser. readline()

    def close_Port(self):
        self.parent.flash_status_message("PORT CLOSSING")
        self.ser.close()

    def is_port_open(self):
        return (self.ser.isOpen())

# *** END OF SerialSource Class ******************


#################### SAMPLE DUMMY
class ConvertClass ():

    def __init__(self):
        self.a = (999.842594, 6.793952e-2, -9.095290e-3, 1.001685e-4, -1.120083e-6,6.536332e-9)
        self.b = (8.24493e-1, -4.0899e-3, 7.6438e-5, -8.2467e-7, 5.3875e-9)
        self.c = (-5.72466e-3, 1.0227e-4, -1.6546e-6)
        self.d = 4.8314e-4

        self.bastime = 0

    def convert_raw(self,line):
        pass

    def convert_simulation_b95(self, line):
        pass

    def convert_archived(self, line):
        scan = dict()

        #        xdatetime = datetime.datetime.strptime(ctdclock,'%H:%M:%S')
        #        if basetime = 0 :
        #                 basetime = xdatetime
        #        scan["ctdclock"] = line[0]
        scan["scannum"] = line[0]
        scan["ctdclock"] = line[1]
        scan["Et"] = line[2]
        scan["pres"] = -1. * float(line[3])
        scan["Pstr"] = str('{:.5}'.format(line[3]))
        scan["Tstr"] = str('{:.5}'.format(line[4]))
        scan["Cstr"] = str('{:.5}'.format(line[5]))
        scan["Sstr"] = str('{:.6}'.format(line[6]))
        scan["Dstr"] = str('{:.6}'.format(line[7]))
        scan["F1str"] = str('{:.5}'.format(line[8]))
        scan["F2str"] = str('{:.5}'.format(line[9]))
        scan["Lstr"] = str('{:.5}'.format(line[10]))
        scan["Vstr"] = str('{:.5}'.format(line[11]))
        #        scan["Et"] = xdatetime - basetime

        #        scan["Dstr"] = str('{:.5}'.format(self.dens0(np.float(line[6]),np.float(line[4]))-1000.0))
        scan["OK"] = True
        return (scan)


########## Smooths a variable ################
class SmoothRate(object):
    def __init__(self,interval):
        self.Avg_interval = interval
        self.rolling_list =  l = [0.0] * self.Avg_interval
        self.n = 0
        self.OldPres = 0.0
        self.PSum =0.0

    def get_rate(self,pres):
           self.n = (self.n  + 1)% self.Avg_interval
           deltaP = pres - self.OldPres
           self.PSum = self.PSum + deltaP - self.rolling_list[self.n]
           the_rate = (60. *self.PSum/self.Avg_interval)
#           print self.n,pres,self.OldPres,deltaP, self.PSum,self.Avg_interval, Rstr
           self.rolling_list[self.n] = deltaP
           self.OldPres = pres
           return (the_rate)
#*** END of SmoothRate Class ******************************

##########################################################################
# READS DATA FROM A FILE :PASS 1 LINE at a atime back via the next method

class read_file_stuff(threading.Thread):
    """
        A thread class that will read a line , output that number to queue and sleep
    """

    def __init__(self, filename, q):
        self.filename = filename
        self.q = q
        self.shutdown = False
        threading.Thread.__init__(self)

    def run(self):
        with open(self.filename) as self.fp:
            for line in self.fp:
                if not self.shutdown:
                    try:
                        msg = pynmea2.parse(line)
                    except pynmea2.nmea.ChecksumError:
                        print "Checksum issue"
                        self.q.put("CHECKSUM_ERROR")
                        continue
                # print "in thread"
                    self.q.put(msg)
                    time.sleep(0.05) # this is just to make the feed more readable and not blow through it
                else:
                    self.q.put("FINISHED")
                    self._close_source()
                    return()
            self.q.put("FINISHED")
#            print "thread says by by"

    def _close_source(self):
        self.fp.close()

    def shut_down(self):
        self.shutdown = True

class DataGen_que(object):
    def __init__(self, parent, FileName, init=50):
        self.parent = parent
        self.data = self.init = init
        self.datafile = FileName
        self.myQueue = Queue.Queue()
        scanner = SMN.SCAN_MSG()
        self.myThread = read_file_stuff(self.datafile, self.myQueue)
        self.status={}
        msg = ""
        self.scanner = SMN.SCAN_MSG()
        self.myThread.start()

    def next(self):
        if not self.myQueue.empty():
            msg = self.myQueue.get()
            if msg != "FINISHED" and msg != "CHECKSUM_ERROR":
                self.scanner.process_message(msg)
                # diagnostic monitoring code
                #                    echo_elements(msg)
#                for x in self.scanner.current:
#                    if x == 'SM2':
#                         print self.scanner.current[x].sensor, self.scanner.current[x].measurement_val, self.scanner.current[x].timestamp
#                     else:
#                        print x, self.scanner.current[x], '|',
                return (self.scanner.current)
            else:
                self.status["OK"] = False
                self.status["REASON"]=msg
                return (self.status)

        else:
            self.status["OK"]=False
            self.status["REASON"] = "WAITING"
            return (self.status)

    def close_DataSource(self):
        self.myThread.shut_down()
        self.flush()
        self.parent.flash_status_message("DATA SOURCE STOPPED")


    def flush(self):  # the mutex is to make sure it is thread safe since clear is 'under the hood'
        with self.myQueue.mutex:
            self.myQueue.queue.clear()

############################################################
class DataGen2(object):
    def __init__(self, FileName, init=50):
        self.data = self.init = init
        self.Convert = ConvertClass()
        #        self.temp = 0.0
        self.FileName = FileName
        self.f = open(self.FileName, "r")
        self.scannum = 0
        self.scan = dict()

        self.readheader()

    def next(self):
        text = self.f.readline()

        if text == "":
            self.scan["OK"] = False
            return (self.scan)
        else:
            self.scannum += 1
            line = text.split()
            #            scan = self.Convert.convert_simulation_b95(line)
            scan = self.Convert.convert_archived(line)
            scan["Et"] = str(self.scannum * DEFAULT_RATE)

            return (scan)

    def readheader(self):

        text = self.f.readline()
        text = self.f.readline()
        text = self.f.readline()
        text = self.f.readline()
        text = self.f.readline()
        text = self.f.readline()

    def flush(self):  # dummy
        return ()

    def close_infile(self):
        self.f.close()

