import pynmea2
import json
from collections import OrderedDict

class SCM(pynmea2.ProprietarySentence):
    sentence_types = {}
    """
        Generic ScanMar Message
    """

    def __new__(_cls, manufacturer, data):
        '''
            Return the correct sentence type based on the first field
        '''
        sentence_type = data[0] or data[1]
        name = manufacturer + sentence_type
        cls = _cls.sentence_types.get(name, _cls)
        return super(SCM, cls).__new__(cls)

    def __init__(self, manufacturer, data):
        self.sentence_type = data[0] or data[1]
        self.name = manufacturer + self.sentence_type
        super(SCM, self).__init__(manufacturer, data)


    """
    SCMGLL SCMVTG SCMZDA SCMDBS  are same as standard nmea sentences but have the proprietery prefix
    rather than the standard neam GP prefix these classes have been borrowed from pynmea2 talker defintions but
    but extend the SCM class instead of the TalkerSentence class used within pynmea2
    """

class SCMGLL(SCM, pynmea2.ValidStatusFix, pynmea2.LatLonFix):
    fields = (
        ('Telegram', 'tel'),
        ('Latitude', 'lat'),
        ('Latitude Direction', 'lat_dir'),
        ('Longitude', 'lon'),
        ('Longitude Direction', 'lon_dir'),
        ('Timestamp', 'timestamp', pynmea2.timestamp),
        ('Status', 'status'),  # contains the 'A' or 'V' flag
        ("FAA mode indicator", "faa_mode"),
    )


class SCMVTG(SCM):
    """
    Track Made Good and Ground Speed
    """
    fields = (
        ('Telegram', 'tel'),
        ("True Track made good", "true_track", float),
        ("True Track made good symbol", "true_track_sym"),
        ("Magnetic Track made good", "mag_track", pynmea2.Decimal),
        ("Magnetic Track symbol", "mag_track_sym"),
        ("Speed over ground knots", "spd_over_grnd_kts", pynmea2.Decimal),
        ("Speed over ground symbol", "spd_over_grnd_kts_sym"),
        ("Speed over ground kmph", "spd_over_grnd_kmph", float),
        ("Speed over ground kmph symbol", "spd_over_grnd_kmph_sym"),
        ("FAA mode indicator", "faa_mode"),
    )


class SCMZDA(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ("Day", "day", int),  # 01 to 31
        ("Month", "month", int),  # 01 to 12
        ("Year", "year", int),  # Year = YYYY
        ("Local Zone Description", "local_zone", int),  # 00 to +/- 13 hours
        ("Local Zone Minutes Description", "local_zone_minutes", int),  # same sign as hours
    )


# DBS - Depth below surface
# Used by simrad devices (f.e. EK500)
# Deprecated and replaced by DPT
class SCMDBS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ('Depth below surface, feet', 'depth_feet', pynmea2.Decimal),
        ('Feets', 'feets'),
        ('Depth below surface, meters', 'depth_meter', pynmea2.Decimal),
        ('Meters', 'meters'),
        ('Depth below surface, fathoms', 'depth_fathoms', pynmea2.Decimal),
        ('Fathoms', 'fathoms'),
    )


# DPT - water depth relative to the transducer and offset of the measuring
# transducer
# Used by simrad devices (f.e. EK500)
# class SCMDPT(TalkerSentence):
#    fields = (
#        ('Water depth, in meters', 'depth', pynmea2.Decimal),
#        ('Offset from the trasducer, in meters', 'offset', pynea2.Decimal),
#        ('Maximum range scale in use', 'range', pynmea2.Decimal),
#    )

######################################################################################################
# Proprietary Scanmar  NMEA sentence class definitions, all extend the base SCM class
# MEASUREMENTS from net sensors - the sensor field determines the meanings of following fields
# SAMPLE :
# <SCMSM2(tel='SM2', timestamp=datetime.time(13, 13, 23), status='V', sensor='DVTLAM', sensor_id='1',
#  measurement_id='B', measurement_val='6.2', qf='0')>
######################################################################################################

class SCMSM2(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('Status', 'status'),
        ('Sensor Type', 'sensor'),
        ('Sensor_ID', 'sensor_id'),
        ('Mesurement Id', 'measurement_id'),
        ('Measurement Value', 'measurement_val'),
        ('Quality Factor', 'qf'),
    )


###################################
# MEASUREMENTS from winch sensors -
###################################


# wirelength and speed PORT winch
class SCMWLP(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed STARBOARD winch
class SCMWLS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed CENTRE or CENTRE.STARBOARD winch
class SCMWLC(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed PORT/CENTER winch
class SCMWLD(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wire tension STARBOARD winch
class SCMWTS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('Wire Tension', 'wiretension'),
        ('Units', 'units'),
    )

# wire tension PORT winch
class SCMWTP(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension CENTRE or STARBOARD winch
class SCMWTC(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension PORT/CENTER winch
class SCMWTD(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

##############################
# Data processing functions class
##############################

class SCAN_MSG():



#    def process_gll(self,msg):
#        print "hellohello gll"
#        self.current['LATITUDE'] = msg.latitude
#        self.current['LONGITUDE'] = msg.longitude
#        self.current['GLL_TIMESTAMP'] = msg.timestamp

##########
    def serialize_instance(self,obj):
        d = { '__classname__' : type(obj).__name__ }
        d.update(vars(obj))
        return d

    def jsonDefault(self,object):
        return object.__dict__

#    def unserialize_object(d):
#        clsname = d.pop('__classname__', None)
#        if clsname:
#            cls = classes[clsname]
#            obj = cls.__new__(cls)  # Make instance without calling __init__
#            for key, value in d.items():
#                setattr(obj, key, value)
#                return obj
#        else:
#            return d
##########

    def process_gll(self, msg):
        GLL = dict()
        GLL['LATITUDE'] = msg.latitude
        GLL['LONGITUDE'] = msg.longitude
        GLL['TIMESTAMP'] = msg.timestamp
        self.current['GLL'] = msg
        self.current['GLL_TIMESTAMP'] = msg.timestamp
        self.current["SENSOR"] = "GLL"
        r = json.dumps(msg, default=self.jsonDefault)
        s = json.dumps(msg.data, default=self.jsonDefault)
#        print "Jason GLL msg", r
#        print "Jasom GLL msg.data", s

    def process_vtg(self,msg):
        VTG = dict()
        VTG['TRACK_TRUE'] = msg.true_track
        VTG['SPEED_KNOTS'] =  msg.spd_over_grnd_kts
        self.current['VTG'] = msg
        self.current["SENSOR"] = "VTG"

    def process_zda(self,x,self2):
        print "int process_zda"
        self2.Current["ZDA"] = x
        self2.disp_text["GPSZDA"].Data_text["ZDA_DATE"].SetValue(
            str(str(x.year).zfill(2) + '-' + str(x.month).zfill(2) + '-' + str(x.day).zfill(2)))
        self2.disp_text["GPSZDA"].Data_text["ZDA_TS"].SetValue(str(x.timestamp))

        self2.P_String["ZDA_DATETIME"] = str(x.year).zfill(2) + '-' + str(x.month).zfill(2) + '-' + str(x.day).zfill(
            2) + 'T' + str(x.timestamp)



    def process_dbs(self,msg):
        self.current['DBS_METERS'] = msg.depth_meter
        self.current["SENSOR"] = "DBS"

    def process_wl(self,msg):
        self.current[msg.sentence_type+'_LEN'] = msg.wireout
        self.current[msg.sentence_type+'_SPD'] = msg.wirespeed
        self.current["SENSOR"] = "WL"

    def process_wt(self,msg):
        self.current[msg.sentence_type+'_TEN'] = msg.wiretension
        self.current["SENSOR"] = "WT"

    def process_dvt(self,msg):
        self.current[msg.sentence_type] = msg


#    def process_dvtlam(self,msg):
#        print "hellohello dvtlam"
#        self.current[msg.sentence_type] = msg

#    def process_dvtlas(self,msg):
#        print "hellohello dvtlas"
#        self.current[msg.sentence_type] = msg

#    def process_cvtlam(self,msg):
#        print "hellohello cvtlam"
#        self.current[msg.sentence_type] = msg

    def process_cvt(self, msg):
        self.current[msg.sentence_type] = msg


    def process_ts(self,msg):
        self.current[msg.sentence_type] = msg


    def process_tsp(self,msg):
        self.current[msg.sentence_type] = msg


    def process_tlt(self,msg):
        self.current[msg.sentence_type] = msg


    def process_dp(self,msg):
        self.current[msg.sentence_type] = msg


    def process_sm2_org(self, msg):
        if msg.sensor in self.TelegramDict:
#            print self.TelegramDict[msg.sensor]
            self.TelegramDict[msg.sensor](self,msg)
        else:
            print "missing key not in TelegramDict=", msg.sentence_type

    def process_sm2(self, msg):
        m = msg.sensor + '_' + msg.sensor_id + '_' + msg.measurement_id
        self.current[msg.sentence_type] = msg   # DVTLAS
        self.current["SENSOR"] = msg.sentence_type              # DVTLAS_1_A
        self.current["SENSOR_ELEMENT"] = m              # DVTLAS_1_A

        r = json.dumps(msg, default=self.jsonDefault)
        s = json.dumps(msg.data,default=self.jsonDefault)
#        t = json.dumps(msg.data,default = self.serialize_instance)
#        print "Jason R", r
#        print "Jasom S", s
#        print "Jason T", t

#################################################################################
# Dictionaries to allow translation of sensor into the correct procedure to call
# GroupDict are the highest level ones that come from the pymea2 Sentence_type ;
# TelegramDict are the SM2 individual net sensors (msg.sensor) for a SM2 message)
#  that are sub element of the SM2 GroupDict sentence type
#
# call it like this :
# GroupDict[msg.sensor](msg)    ex. GroupDict["GLL](msg)
# would call the process_gll function and pass it the msg data
#################################################################################

    GroupDict = {
        'SM2': process_sm2,
        'GLL': process_gll,
        'VTG': process_vtg,
        'ZDA': process_zda,
        'DBS': process_dbs,
        'WLP' : process_wl,
        'WTP' : process_wt,
        'WLS': process_wl,
        'WTS': process_wt,
    }
# for sm2 messages
    TelegramDict = {
#       'DVTLAM': process_dvtlam,
#       'DVTLAS': process_dvtlas,- sensor types
        'DVTLAM': process_dvt,
        'DVTLAS': process_dvt,
#        'CVTLAM': process_cvtlam,
#        'CVTLAS': process_cvtlas,
        'CVTLAM': process_cvt,
        'CVTLAS': process_cvt,
        'TS': process_ts,
        'TSP': process_tsp,
        'TLT': process_tlt,
        'DP': process_dp,
    }

    ###########################################################################
    #Process the messages based on thier sentence type
    ###########################################################################


    def process_message_new(self, msg):
        self.current = dict()
        if isinstance(msg, SCM):
            if msg.sentence_type in self.GroupDict:
                if msg.sentence_type == "SM2":
                    m = msg.sensor + '_' + msg.sensor_id + '_' + msg.measurement_id
                    self.current[msg.sentence_type] = msg  # DVTLAS
                    self.current["SENSOR"] = msg.sentence_type  # DVTLAS_1_A
                    self.current["SENSOR_ELEMENT"] = m  # DVTLAS_1_A
                else:
                    self.current["SENSOR"] = msg.sentence_type
                    self.current[msg.sentence_type] = msg
                self.current['OK'] = True
            else:
                print "missing key, not in GroupDict=", msg.sentence_type
                self.current['OK'] = False
            print "in SCM instance",msg,"!!"
        else:
            print "NOT SCM instance",msg,"!!"


    #########################################################################
    # the SM2 messages have to be sub processed to get the specific sensor data
    ##########################################################################

class SMN_TOOLS:

    def process_sm2(self,y,disp_text,Raw_String,JDict):
        if y.measurement_id == '':  # issue with CVTLAM having no id value in test data
            y.measurement_id = 'R'
        disp_text[y.sensor].Data_text[y.measurement_id].SetValue(y.measurement_val)
        disp_text["CLOCK"].Data_text["CLOCK"].SetValue(str(y.timestamp))

#        JDict[z] = OrderedDict ([("SENSOR_ID",y.sensor_id),("measurement_id",y.measurement_id),("measurement_val",y.measurement_val),("QF",y.qf),("STATUS",y.status) ])
        Sensor_Element = y.sensor + '_' + y.sensor_id + '_' + y.measurement_id
        JDict[Sensor_Element] = OrderedDict ([("measurement_val",y.measurement_val),("QF",y.qf),("STATUS",y.status) ])
        Raw_String[Sensor_Element] = y

    def process_gll(self,x,disp_text,Raw_String,JDict):
        disp_text["GPS"].Data_text["LA"].SetValue('{:>7.7}'.format(str(x.latitude)))

        disp_text["GPS"].Data_text["LO"].SetValue('{:>8.8}'.format(str(x.longitude)))
        Raw_String["GLL"] = x

        JDict["Latitude"]= x.latitude
        JDict["Longitude"] = x.longitude

    def process_vtg(self,x,disp_text,Raw_String,JDict):
        disp_text["GPS"].Data_text["H"].SetValue(str(x.true_track))
        disp_text["GPS"].Data_text["SP"].SetValue(str(x.spd_over_grnd_kts))
        Raw_String["VTG"] = x
        JDict["VTG_TRACK"] = str(x.true_track)
        JDict["VTG_SPD"] = str(x.spd_over_grnd_kts)

    def process_zda(self,x,disp_text,Raw_String,JDict):
        print "int process_zda"
#        Current["ZDA"] = x
        disp_text["GPSZDA"].Data_text["ZDA_DATE"].SetValue(
            str(str(x.year).zfill(2) + '-' + str(x.month).zfill(2) + '-' + str(x.day).zfill(2)))
        disp_text["GPSZDA"].Data_text["ZDA_TS"].SetValue(str(x.timestamp))

        Raw_String["ZDA"] = x
        JDict["DATATIME"] = str(x.year).zfill(2) + '-' + str(x.month).zfill(2) + '-' + str(x.day).zfill(
            2) + 'T' + str(x.timestamp)

    def process_dbs(self,x,disp_text,Raw_String,JDict):
        disp_text["DBS"].Data_text["DBS"].SetValue(str(x.depth_meter))
        Raw_String["DBS"] = x
        JDict["DBS"] = str(x.depth_meter)

    def process_wts(self,x,disp_text,Raw_String,JDict):
#        disp_text["WTS"].Data_text["DBS"].SetValue(str(x.depth_meter))
        Raw_String["WTS"] = x
        JDict["WTS"] = str(x.wiretension)


    def process_wtp(self, x, disp_text, Raw_String, JDict):
#        disp_text["WTS"].Data_text["DBS"].SetValue(str(x.depth_meter))
        Raw_String["WTP"] = x
        JDict["WTP"] = str(x.wiretension)




    def process_wlp(self, x, disp_text, Raw_String, JDict):
        #        disp_text["WLP"].Data_text["WLP"].SetValue(str(x.depth_meter))
        Raw_String["WLP"] = x
        JDict["WLPT"] = str(x.wirespeed)
        JDict["WLPT"] = str(x.wireout)

    def process_wls(self, x, disp_text, Raw_String, JDict):
        #        disp_text["WLS].Data_text["WLS"].SetValue(str(x.depth_meter))
        Raw_String["WLS"] = x
        JDict["WLST"] = str(x.wirespeed)
        JDict["WLST"] = str(x.wireout)

    GroupDict = {
        'SM2': process_sm2,
        'GLL': process_gll,
        'VTG': process_vtg,
        'ZDA': process_zda,
        'DBS': process_dbs,
# these could be precessed more like an SM2 since they are same format
        'WLP': process_wlp,
        'WLS': process_wls,
        'WTP': process_wtp,
        'WTS': process_wtp,
       }

    def dispatch_message(self,sentence_type, line_x ,disp_text,Raw_String,JDict):
            if sentence_type in self.GroupDict:

                if sentence_type == "SM2":
                    # process sm2 messages since they are in a nested dictionary withing the block
                    for z in line_x:
                        y = line_x[z]
                        self.GroupDict[sentence_type](self,y,disp_text,Raw_String,JDict)
                else:
                    self.GroupDict[sentence_type](self,line_x,disp_text,Raw_String,JDict)

#                current['OK'] = True
            else:
                print "missing key, not in GroupDict=", sentence_type
#                current['OK'] = False