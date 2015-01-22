import urllib2
import ephem
import math

TLEURL = "http://www.amsat.org/amsat/ftp/keps/current/nasabare.txt"

DEGREES_PER_RADIAN = 180.0 / math.pi

# Method for fetching list of TLE from a website, parsing, and loading into a dictionary (hash table)
def loadTLE(url) :
	satlist = dict()
	# Download AMSAT TLE file
	tledatafile = urllib2.urlopen(TLEURL)
	tledata = tledatafile.read()
	tleEntries = tledata.split("\n")
	for i in range(0, len(tleEntries) - 2, 3) :
		satelites[tleEntries[i]] = ephem.readtle(tleEntries[i].rstrip("\r\n"), tleEntries[i + 1].rstrip("\r\n"), tleEntries[i + 2].rstrip("\r\n"))
	return satlist

# Main
satelites = dict()
satelites.update(loadTLE(TLEURL))
print "Currently loaded " + str(len(satelites)) + " satelites"

# Define station location for pyephem
station = ephem.Observer()
station.long =  ephem.degrees('-74.625')     #W2PU location
station.lat = ephem.degrees('40.35417')
station.elevation = 43

station.date = ephem.now()
print "Currently Overhead:"
for satname in satelites :
	station.date = ephem.now()
	satelites[satname].compute(station)
	altitude = satelites[satname].alt * DEGREES_PER_RADIAN
	azimuth = satelites[satname].az * DEGREES_PER_RADIAN
	#if (altitude > 0) :
	print(satname + ": altitude = " + str(altitude) + " deg azimuth = " + str(azimuth) + " deg")