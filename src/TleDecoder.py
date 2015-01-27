import urllib2
import ephem
import math
from Tkinter import *
import Pmw

TLEURL = "http://www.amsat.org/amsat/ftp/keps/current/nasabare.txt"

DEGREES_PER_RADIAN = 180.0 / math.pi

# Method for fetching list of TLE from a website, parsing, and loading into a dictionary (hash table)
def fetchTLE(url) :
	satlist = dict()
	# Download AMSAT TLE file
	tledatafile = urllib2.urlopen(TLEURL)
	tledata = tledatafile.read()
	tleEntries = tledata.split("\n")
	for i in range(0, len(tleEntries) - 2, 3) :
		satellites[tleEntries[i]] = ephem.readtle(tleEntries[i].rstrip("\r\n"), tleEntries[i + 1].rstrip("\r\n"), tleEntries[i + 2].rstrip("\r\n"))
	return satlist

# Method for printing current az/alt of tracked satellites
def printPosition(station, satellites) :
	for satname in satellites :
		station.date = ephem.now()
		satellites[satname].compute(station)
		altitude = satellites[satname].alt * DEGREES_PER_RADIAN
		azimuth = satellites[satname].az * DEGREES_PER_RADIAN
		#if (altitude > 0) :
		print(satname + ":   \taltitude = " + str(altitude) + " deg \tazimuth = " + str(azimuth) + " deg")
	return
	
def selectSatellite(station, satellites, tkRoot) :
	# Calculate current position for each satellite, append to name for display in dialog
	listSatNames = []
	for satname in satellites :
		station.date = ephem.now()
		satellites[satname].compute(station)
		altitude = satellites[satname].alt * DEGREES_PER_RADIAN
		azimuth = satellites[satname].az * DEGREES_PER_RADIAN
		if altitude > 0 :
			# Put visible satellites at top of list
			listSatNames.insert(0, satname + " (" + "{0:.2f}".format(altitude) + ", " 
				+ "{0:.2f}".format(azimuth) + ")")
		else :
			listSatNames.append(satname + " (" + "{0:.2f}".format(altitude) + ", " 
				+ "{0:.2f}".format(azimuth) + ")")
	# Define dialog
	dialog = Pmw.ComboBoxDialog(tkRoot,
		title = 'Satellite Selection',
		buttons = ('OK','Cancel'),
		defaultbutton = 'OK',
		combobox_labelpos = 'n',
		label_text = 'Select satellite to track',
		scrolledlist_items = listSatNames)
	# Display dialog
	buttonClicked = ""
	buttonClicked = dialog.activate()
	dialog.focus_force()
	response = dialog.get()
	return response[:(response.find("(") - 1)]
# Main

#Initialize Tkinter, Pmw MegaWidgets
root = Tk()
root_geom=""
font1='Helvetica'

satellites = dict()
satellites.update(fetchTLE(TLEURL))
print "Currently loaded " + str(len(satellites)) + " satellites"

# Define station location for pyephem
station = ephem.Observer()
station.long =  ephem.degrees('-74.625')     #W2PU location
station.lat = ephem.degrees('40.35417')
station.elevation = 43

printPosition(station, satellites)
print selectSatellite(station, satellites, root)