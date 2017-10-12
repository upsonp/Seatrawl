import math

#This is a function does a great circle calculation

def haversine(key,lat1, lon1, lat2, lon2):
    R = 6372.8 # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dLat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2)**2
    c = 2* math.asin(math.sqrt(a))
    #calculating KM
    a = R * c
    return a


#    https://impythonist.wordpress.com/2014/12/11/anatomy-and-application-of-parallel-programming-in-python/


#