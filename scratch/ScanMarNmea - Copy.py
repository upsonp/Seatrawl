import pynmea2


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
    but extend the SCM class instaed of the TalkerSentence class used within pynmea2
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
#  measurement_id='B', measurement_val='', qf='0')>
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
        ('Wire Tension', 'tension'),
        ('Units', 'units'),
    )

# wire tension PORT winch
class SCMWTP(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'Wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension CENTRE or STARBOARD winch
class SCMWTC(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'Wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension PORT/CENTER winch
class SCMWTD(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'Wiretension'),
        ('Units', 'Tunits'),
    )

##############################
# Data processing functions
##############################
def process_gll(msg):
    print "hellohello gll"


def process_vtg(msg):
    print "hellohello vtg"


def process_zda(msg):
    print "hellohello zda"

def process_dbs(msg):
    print "hellohello dbs"

def process_wlp(msg):
    print "hellohello wlp"

def process_wtp(msg):
    print "hellohello wls"

def process_dvtlam(msg):
    print "hellohello dvtlam"


def process_dvtlas(msg):
    print "hellohello dvtlas"


def process_cvtlam(msg):
    print "hellohello cvtlam"


def process_ts(msg):
    print "hellohello ts"


def process_tsp(msg):
    print "hellohello tsp"


def process_tlt(msg):
    print "hellohello tlt"

def process_dp(msg):
    print "hellohello dp"

#########################################################################
# the SM2 messages have to be sub processed to get the specific sensor data
##########################################################################
def process_sm2(msg):
    print "hellohello sm2"
    if msg.sentence_type in TelegramDict:
        print TelegramDict[msg.sensor]
        TelegramDict[msg.sensor](msg)
    else:
        print "missing key", msg.sentence_type

#################################################################################
# Dictionaries to allow translation of sensor into the correct procedure to call
# GroupDict are the highest level ones that come from the pymea2 Sentence_type ;
# TelegramDict are the SM2 individual net sensors that are sub element of the SM2
#
# call it like this :
# TelegramDict[msg.sensor](msg)    ex. GroupDict["GLL](msg)
# would call the process_gll function and pass it the msg data

#################################################################################

GroupDict = {
    'SM2': process_sm2,
    'GLL': process_gll,
    'VTG': process_vtg,
    'ZDA': process_zda,
    'DBS': process_dbs,
    'WLP' : process_wlp,
    'WTP' : process_wtp,
}

TelegramDict = {
    'DVTLAM': process_dvtlam,
    'DVTLAS': process_dvtlas,
    'CVTLAM': process_cvtlam,
    'TS': process_ts,
    'TSP': process_tsp,
    'TLT': process_tlt,
    'DP' : process_dp,
}
