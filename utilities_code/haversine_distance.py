import sys

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2.) ** 2. + cos(lat1) * cos(lat2) * sin(dlon / 2.) ** 2.
    c = 2. * asin(sqrt(a))
    r = 6371.8  # approx Radius of earth in kilometers. Use 3959.87433 for miles , 3440 for nautical
    km =  c * r
    nm=  km /1.853
    return nm


def main() :
    print len(sys.argv)
    if len(sys.argv) != 5:
        print "supply lon1 lat1 lon2 lat2"
        quit()

    print sys.argv[0], sys.argv[1], sys.argv[2] , sys.argv[3]  , sys.argv[4]
    lon1 = float(sys.argv[1])
    lat1 = float(sys.argv[2])
    lon2 = float(sys.argv[3])
    lat2 = float(sys.argv[4])

    dist = haversine(lon1,lat1,lon2,lat2)
    print (dist)

if __name__ == '__main__':
    main()
