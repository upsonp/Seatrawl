import time
import serial
import pynmea2
import sys
import datetime

import ScanMarNmea as SMN



def read(filename):
    f = open(filename)
    reader = pynmea2.NMEAStreamReader(f)

    while 1:
        for msg in reader.next():
            print(msg)
            test_proprietary_type_SCM(msg)


def read_serial(filename):
    com = None
    reader = pynmea2.NMEAStreamReader()

    while 1:

        if com is None:
          try:
            com = serial.Serial(filename, timeout=5.0)
          except serial.SerialException:
            print('could not connect to %s' % filename)
            time.sleep(5.0)
            continue

        data = com.read(16)
        for msg in reader.next(data):
            print(msg)
            test_proprietary_type_SCM(msg)


        
def Myread(filename):

    with open(filename) as fp:
        for line in fp: 
##            reader = pynmea2.NMEAStreamReader(fp)
            try:
                msg= pynmea2.parse(line)
#                print 'MAN=',msg.manufacturer 
#                if isinstance(msg, pynmea2.types.talker.GGA):
#                print 'LINE=',line
#                print 'ELEMENTS=',msg.data[0],msg.data[1],msg.data[2],msg.data[3],msg.data[4],msg.data[5],msg.data[6],msg.data[7]
            except pynmea2.nmea.ChecksumError:
                print "Checksum issue"
#                exit()
                continue
            test_proprietary_types2(msg)

#            print msg.manufacturer

#            assert isinstance(msg, ABC)
#            if msg.data[0]=='SM2':
#                msg.sentence_type = 'SM2'
#            print msg.sentence_type
#            print' MANU = ',msg.manufacturer

def test_proprietary_type_WTS(msg):


#    data = "$PSCMWTS,131321.00,0.00,T*16"
#    try :
#        msg = pynmea2.parse(data)
#    except pynmea2.nmea.ChecksumError:
#        print "Checksum issue"
    print isinstance(msg, SMN.SCM)
    print 'MAN=',msg.manufacturer
    print 'TEL=',msg.tel
    print msg.ts, msg.units

def process_gll():
    print "hello"


funcdict = {
    'GLL' : process_gll
}


def test_proprietary_types2(msg):

    data = '$PTNL,AVR,212405.20,+52.1531,Yaw,-0.0806,Tilt,,,12.575,3,1.4,16*39'
    data2 = '$GPGLL,3953.88008971,N,10506.75318910,W,034138.00,A,D*7A'
    data3 = '$PTNL,GGK,102939.00,051910,5000.97323841,N,00827.62010742,E,5,09,1.9,EHT150.790,M*73'
    data4 = '$PSCMSM2,131320.00,V,TS,5,C,,0*36'
    data5 = '$PSCMGLL,4751.0422,N,05335.5213,W,111646.00,A,A*62'
    try:
#        msg = pynmea2.parse(data4)
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
    except pynmea2.nmea.ChecksumError:
        print "Checksum issue"

def test_proprietary_types():
        data='$PTNL,AVR,212405.20,+52.1531,Yaw,-0.0806,Tilt,,,12.575,3,1.4,16*39'
        data2='$GPGLL,3953.88008971,N,10506.75318910,W,034138.00,A,D*7A'
        data3='$PTNL,GGK,102939.00,051910,5000.97323841,N,00827.62010742,E,5,09,1.9,EHT150.790,M*73'
        data4='$PSCMSM2,131320.00,V,TS,5,C,,0*36'
        data5='$PSCMGLL,4751.0422,N,05335.5213,W,111646.00,A,A*62'
        try:
                msg= pynmea2.parse(data4)
#                print 'MAN=',msg.manufacturer 
#                if isinstance(msg, pynmea2.types.talker.GGA):
#                if isinstance(msg, pynmea2.types.talker.GLL):
#                if isinstance(msg, pynmea2.types.proprietary.tnl.TNLGGK):
                if isinstance(msg,SMN.SCMSM2):
                        print 'ELEMENTS=', len(msg.data) 
                        for i in range(0,len(msg.data)) :
                                print msg.data[i],'|',
                        print  '\n',msg.data
                        print  'ELEMENTS by Name= ',msg.tel, msg.ts,msg.status
                        print repr(msg)
        except pynmea2.nmea.ChecksumError:
                print "Checksum issue"


def test_proprietary_types_PSCMGLL():
        data5='$PSCMGLL,4751.0422,N,05335.5213,W,111646.00,A,A*62'
        try:
                msg= pynmea2.parse(data5)
#                print 'MAN=',msg.manufacturer 
#                if isinstance(msg, pynmea2.types.talker.GGA):
#                if isinstance(msg, pynmea2.types.talker.GLL):
#                if isinstance(msg, pynmea2.types.proprietary.tnl.TNLGGK):
                if isinstance(msg,SMNGLL):
                        print 'ELEMENTS=', len(msg.data) 
                        for i in range(0,len(msg.data)) :
                                print msg.data[i],'|',
                        print  '\n',msg.data
#                        print  'ELEMENTS by Name=',msg.tel, msg.lat,msg.lon,msg.latitude,msg.longitude,msg.timestamp
                        print repr(msg)
                else:
                        print 'Nope not seen as GLL'
        except pynmea2.nmea.ChecksumError:
                print "Checksum issue"
def test_proprietary_type_SCM(msg):


#    data = '$PABC,1,2*13'
#    msg = pynmea2.parse(data)
    print msg.data

    print 'IS IT SCM=',isinstance(msg, SCM)
    print 'TEL=',msg.tel


#    assert msg.a == '1'
#    assert msg.b == '2'
    print 'DATA =',msg.data
#    assert repr(msg) == "<ABC(_='', a='1', b='2')>"
    print 'MESG=',str(msg)
    print 'ELEMENTS=', len(msg.data) 
    for i in range(0,len(msg.data)) :
        print msg.data[i],'|',   
#    print msg.ts,msg,status,msg.sensor_id,msg.mes_id,msg.mes_val,msg.val

def test_proprietary_type_sample():
    class ADC(pynmea2.ProprietarySentence):
        fields = (
            ('Empty', '_'),
            ('First', 'a'),
            ('Second', 'b'),
        )

    data = '$PADC,1,2*15'
    try :
        msg = pynmea2.parse(data)
    except pynmea2.nmea.ChecksumError:
        print "Checksum issue"
    print isinstance(msg, ADC)
    print msg.manufacturer == 'ADC'
    print msg.a == '1'
    assert msg.b == '2'
    assert repr(msg) == "<ADC(_='', a='1', b='2')>"

    print str(msg)

            
 
def main():
        if len(sys.argv) >1:
            datafile = sys.argv[1]
        else:
            datafile = "scan_simple_rs.log"
#    test_proprietary_type()
#        test_proprietary_types()
#        test_proprietary_types_PSCMGLL()

        
        Myread(datafile)


if __name__ == "__main__":
    main()
