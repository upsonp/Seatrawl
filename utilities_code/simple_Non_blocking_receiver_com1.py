# from : http://eli.thegreenplace.net/2009/07/30/setting-up-python-to-work-with-the-serial-port/
# a non blocking reciever
# use with com0com  http://com0com.sourceforge.net/
# http://www.magsys.co.uk/comcap/onlinehelp/null_modem_emulator_com0com.htm
import serial
import msvcrt # built-in module
import sys
from time import sleep

def kbfunc():

    return msvcrt.getch() if msvcrt.kbhit() else '0'

port = "com3"
ser = serial.Serial(port, 9600, timeout=0)
Nseconds = 0.05

print " Press p to pause ; g to go ; f faster ; s slower ; q to quit gracefully"
paused = True
while True:
	
		kk = kbfunc()

		if kk == 'g':
			paused=  False
		if kk == 'p':
			paused = True

		if kk  == 'q':
			break
		if kk == 'f':
			Nseconds = Nseconds - 0.005
			if Nseconds < 0.00001: 
				Nseconds = 0.00001
				sys.stdout.write("\a") # plays a beep to say your at limit

		if kk == 's':
			Nseconds = Nseconds + 0.005

		if not paused :
			data = ser.readline()
			if len(data) > 0:
				print  data,

		sleep(Nseconds)


ser.close()
