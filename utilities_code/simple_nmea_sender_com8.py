# from : http://eli.thegreenplace.net/2009/07/30/setting-up-python-to-work-with-the-serial-port/
# simple sender use with http://com0com.sourceforge.net/
# http://www.magsys.co.uk/comcap/onlinehelp/null_modem_emulator_com0com.htm

#############################################################################
# NOTE  IF YOU HAVE ISSUES NOT GETTING DATA LOWER THE SIZE OF THE FIFO BUFFERS 
# IN THE WINDOWS HARDWARE SETUP FOR THE SERIAL PORTS UNDER ADVANCED SETTINGS
#############################################################################

import serial
import time
import msvcrt # built-in module
import sys

class DataGen2(object):
    def __init__(self, FileName,init=50):
		self.data = self.init = init
		self.FileName = FileName
		self.f = open(self.FileName,"r")
		print "File opened"

    def next(self):
        line=self.f.readline()
        return line

    def close_infile(self):
        print "closing file"
        self.f.close()

	def rewind(self):
		self.f.seek(0)

def on_send_timer(datagen,ser) :
    line = datagen.next()
    if line !=[] :
        x = ser.write(line)
        return line
    else:
        return ([])


def kbfunc():

    return msvcrt.getch() if msvcrt.kbhit() else '0'

def main() :
	if len(sys.argv) != 2:
		print "supply data file name"
		quit()
	print sys.argv[0], sys.argv[1]


	FileName= sys.argv[1]


#	FileName = "scanmar_rs_trimmed.log"

	port = "com8"
	Nseconds = 0.02
	print "reading",FileName
	datagen = DataGen2(FileName)
	print "trying for serial port ",port
	try: 
		ser = serial.Serial(port, 9600)
	except serial.SerialException,e:
		print "error opening serial port: "+port+" " + str(e)
		return(False)
	print "port open"

	print " Press p to pause ; g to go ; l to loop ; f faster ; s slower ; z toggle silent mode ; q to quit gracefully"


	x = "x"
	paused = True
	kk = ''
	loop = False
	silent = False
	while x !="" :
	
		kk = kbfunc()

		if kk == 'g':
			paused=  False
		if kk == 'p':
			paused = True
		if kk == 'l':
			loop = True
		if kk == 'z':
			silent = not silent
		if kk  == 'q':
			break
		if kk == 'f':
			Nseconds = Nseconds - 0.005
			if Nseconds < 0.00001: 
				Nseconds = 0.00001
				sys.stdout.write("\a") # plays a beep to say your at limit

		if kk == 's':
			Nseconds = Nseconds + 0.005

			
		time.sleep(Nseconds)
		if not paused:
			x = on_send_timer(datagen,ser)
			if not silent:
				print x,
			if x =='' and loop:
				datagen.rewind()
		
        
	datagen.close_infile()

	ser.close()
	print 'bye - port closed'

if __name__ == '__main__':
        main()
