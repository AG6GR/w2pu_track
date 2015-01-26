import urllib2
import ephem
import math
from Tkinter import *
import Pmw

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
	
# Main

#Initialize Tkinter, Pmw MegaWidgets
root = Tk()
root_geom=""
font1='Helvetica'

satellites = dict()
satellites.update(loadTLE(TLEURL))
print "Currently loaded " + str(len(satellites)) + " satellites"

# Define station location for pyephem
station = ephem.Observer()
station.long =  ephem.degrees('-74.625')     #W2PU location
station.lat = ephem.degrees('40.35417')
station.elevation = 43

printPosition(station, satellites)

# Define dialog

dialog = Pmw.ComboBoxDialog(root,
	title = 'Satellite Selection',
	buttons = ('OK','Cancel'),
	defaultbutton = 'OK',
	combobox_labelpos = 'n',
	label_text = 'Select satellite to track',
	scrolledlist_items = (satellites.keys()))

# Display dialog
buttonClicked = dialog.activate()
dialog.focus_force()
print dialog.get()