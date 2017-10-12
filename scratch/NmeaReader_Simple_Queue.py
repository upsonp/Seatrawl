# from : https://lonelycode.com/2011/02/04/python-threading-and-queues-and-why-its-awesome/
import threading
import Queue
import time
import pynmea2
import sys

import ScanMarNmea as SMN


myQueue = Queue.Queue()

class read_stuff(threading.Thread):
    """ 
        A thread class that will read a line , output that number to queue and sleep
    """
    
    def __init__ (self, filename, q):
        self.filename = filename
        self.q = q
        threading.Thread.__init__ (self)
    
    def run(self):
         with open(self.filename) as fp:
            for line in fp:
                try:
                    msg = pynmea2.parse(line)
                except pynmea2.nmea.ChecksumError :
                    print "Checksum issue"
                    self.q.put("CHECKSUM_ERROR")
                    continue
#                print "in thread"
                self.q.put(msg)
                time.sleep(0.1)
            self.q.put("FINISHED")
            print "thread says by by"


def test_proprietary_types2(msg):

#    data = '$PTNL,AVR,212405.20,+52.1531,Yaw,-0.0806,Tilt,,,12.575,3,1.4,16*39'
#    data2 = '$GPGLL,3953.88008971,N,10506.75318910,W,034138.00,A,D*7A'
#    data3 = '$PTNL,GGK,102939.00,051910,5000.97323841,N,00827.62010742,E,5,09,1.9,EHT150.790,M*73'
#    data4 = '$PSCMSM2,131320.00,V,TS,5,C,,0*36'
#    data5 = '$PSCMGLL,4751.0422,N,05335.5213,W,111646.00,A,A*62'
#                print 'MAN=',msg.manufacturer
#                if isinstance(msg, pynmea2.types.talker.GGA):
#                if isinstance(msg, pynmea2.types.talker.GLL):
#                if isinstance(msg, pynmea2.types.proprietary.tnl.TNLGGK):

    if isinstance(msg, SMN.SCM):
            print "manufactures = ",msg.manufacturer
            print "Sentence type = ",msg.sentence_type
            print "name = ",msg.name
            print 'ELEMENTS=', len(msg.data)

            if msg.sentence_type in SMN.GroupDict:
                print SMN.GroupDict[msg.sentence_type]
                SMN.GroupDict[msg.sentence_type](msg)
            else:
                print "missing key",msg.sentence_type

            for i in range(0, len(msg.data)):
                print msg.data[i], '|',
            print  '\n', msg.data

#            print  'ELEMENTS by Name= ', msg.tel, msg.ts, msg.status
            print repr(msg)

def echo_elements (msg):
    for i in range(0, len(msg.data)):
        print msg.data[i], '|',
    print  '\n', msg.data

def main():
        if len(sys.argv) > 1:
            datafile = sys.argv[1]
        else:
            datafile = "scan_simple_rs.log"

        scanner = SMN.SCAN_MSG()
        myThread = read_stuff(datafile, myQueue)
        myThread.start()
        msg=""
        while msg != "FINISHED":
            if not myQueue.empty():
                msg = myQueue.get()
                if msg != "FINISHED" and msg != "CHECKSUM_ERROR":
                    scanner.process_message(msg)
#diagnostic monitoring code
#                    echo_elements(msg)
                    for x in scanner.current :
                        if x == 'SM2':
                            print x,scanner.current[x].sensor,scanner.current[x].measurement_val, scanner.current[x].timestamp
                        else:
                            print x, scanner.current[x],'|',
                    print
                    print "*************************************************"

                time.sleep(0.1)

if __name__ == "__main__":
    main()
