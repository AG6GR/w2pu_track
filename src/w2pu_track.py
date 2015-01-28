#--------------------------------------------------------------  w2pu_track
from Tkinter import *
import Pmw, serial, os, time, math, ephem, pyaudio, urllib2
from array import array
from itertools import imap
from operator import mul
from Rotator import Rotator

CHUNK_SIZE = 12000
FORMAT = pyaudio.paInt16
RATE = 12000
##STATION = "K1JT"
STATION = "W2PU"
COMPORT = "COM1"
TLEURL = "http://www.amsat.org/amsat/ftp/keps/current/nasabare.txt"
DEGREES_PER_RADIAN = 57.2957795131

#Initialize Tkinter, Pmw MegaWidgets
root = Tk()
appdir=os.getcwd()
root_geom=""
font1='Helvetica'

# Initialize Serial Communications
if sys.platform=="win32":
    rotor = Rotator(COMPORT)
else:
    rotor = Rotator("/dev/ttyS0")

#Declare variables
moveok=False
naz0=-999
nel0=0
t0=0. # Possibly can be removed, seems to be repurposed as string in update()
# Center of azimuth display dial
x0=120
y0=120
# Manual mode requested position
azreq=150
elreq=20
# Used for db display calculations
s1=0
s2=0
s4=0
n1=0
n2=0
n4=0
# GUI Checkbox Values
nThreePoint=IntVar()
nWriteToFile=IntVar()
nRun=IntVar()
nWriteToFile0=0
# Log File object
logFile=""
# Related to pyAudio stream
running=False
stream=""

# Open azel.dat in writing mode
# Contains last known az/el position of rotators
f0=open(appdir+'/azel.dat',mode='w')

# Define station location for pyephem
telescope = ephem.Observer()
telescope.long =  ephem.degrees('-74.625')     #W2PU location
telescope.lat = ephem.degrees('40.35417')
telescope.elevation = 43

# Define dictionary for satellite database
satellites = dict()
# Define Tkinter string for currently selected satellite
selectedSatellite = StringVar()
selectedSatellite.set("Satellite")

# Setup fixed pyephem bodies
celestialBodies = dict()
# Sun
celestialBodies["Sun"] = ephem.Sun()
# Moon
celestialBodies["Moon"] = ephem.Moon()
# Pulsar B0329+54
celestialBodies["PSR B0329+54"] = ephem.FixedBody()
celestialBodies["PSR B0329+54"]._ra = ephem.hours('03:29:11')
celestialBodies["PSR B0329+54"]._dec = ephem.degrees('54:24:37')
celestialBodies["PSR B0329+54"]._epoch="1950/1/1 00:00:00"
# Cassiopeia A
celestialBodies["Cassiopeia A"] = ephem.FixedBody()
celestialBodies["Cassiopeia A"]._ra = ephem.hours('23:23:26')
celestialBodies["Cassiopeia A"]._dec = ephem.degrees('58:48:54')
celestialBodies["Cassiopeia A"]._epoch="2000/1/1 00:00:00"
# Cygnus
celestialBodies["Cygnus A"] = ephem.FixedBody()
celestialBodies["Cygnus A"]._ra = ephem.hours('19:59:28')
celestialBodies["Cygnus A"]._dec = ephem.degrees('40:44:01')
celestialBodies["Cygnus A"]._epoch="2000/1/1 00:00:00"
# Leo
celestialBodies["Leo"] = ephem.FixedBody()
celestialBodies["Leo"]._ra = ephem.hours('09:30:00')
celestialBodies["Leo"]._dec = ephem.degrees('30:00:00')
celestialBodies["Leo"]._epoch="2000/1/1 00:00:00"
# Sagittarius
celestialBodies["Sagittarius A"] = ephem.FixedBody()
celestialBodies["Sagittarius A"]._ra = ephem.hours('17:45:12')
celestialBodies["Sagittarius A"]._dec = ephem.degrees('-28:43:00')
celestialBodies["Sagittarius A"]._epoch="2000/1/1 00:00:00"
# Taurus
celestialBodies["Taurus A"] = ephem.FixedBody()
celestialBodies["Taurus A"]._ra = ephem.hours('05:34:32')
celestialBodies["Taurus A"]._dec = ephem.degrees('22:00:52')
celestialBodies["Taurus A"]._epoch="2000/1/1 00:00:00"
# Virgo
celestialBodies["Virgo A"] = ephem.FixedBody()
celestialBodies["Virgo A"]._ra = ephem.hours('12:30:49')
celestialBodies["Virgo A"]._dec = ephem.degrees('12:23:28')
celestialBodies["Virgo A"]._epoch="2000/1/1 00:00:00"

#--------------------------------------------------------- dot()
def dot(a, b):
    return sum(imap(mul, a, b))

#--------------------------------------------------------- toggle_stop_go()
def toggle_stop_go(event=NONE):
    """Event handler for click event on Stop/Go button"""
    global moveok,t0
    print "toggle_stop_go() called"
    if moveok:
        # Was enabled, now stopped
        disable_move(event)
    else:
        # Was stopped, now enabled
        moveok = True
        moveButton.configure(bg='green')
        t0=time.clock()
        update()

#--------------------------------------------------------- disable_move()
def disable_move(event=NONE):
    """Called after radio button is changed"""
    global moveok, rotor
    print "disable_move()"
    moveok = False
    moveButton.configure(bg='red')
    rotor.stop()

#-------------------------------------------------------------- nint()
def nint(x):
    """Rounds x to the nearest integer"""
    if(x>0):
        return int(x+0.5)
    else:
        return int(x-0.5)

#-------------------------------------------------------------- msgbox()
def msgbox(t):
    """Generates and displays a message dialog with text t"""
    msg=Pmw.MessageDialog(root,buttons=('OK',),message_text=t)
    result=msg.activate()
    msg.focus_set()

#------------------------------------------------------ mouse_click_az
def mouse_click_az(event):
    """Event handler for click event on azimuth display dial"""
    global x0,azreq,t0
    print "Detected click on azimuth dial"
    # Find and set the new requested azimuth
    x=event.x - x0
    y=event.y - x0
    azreq=nint(DEGREES_PER_RADIAN*math.atan2(x,-y))
    if(azreq<0): azreq=azreq+360
    # Disable movement, change to manual mode
    disable_move(event)
    ntrack.set('Manual')
    t0=time.clock()
    update()

#------------------------------------------------------ mouse_click_el
def mouse_click_el(event):
    """Event handler for click event on elevation display meter"""
    global elreq,t0
    print "Detected click on elevation dial"
    # Find and set the new requested elevation
    y=event.y
    if y<20: y=20
    if y>220: y=220
    elreq = (220-y)*(80.0/200.0)
    # Disable movement, change to manual mode
    disable_move(event)
    ntrack.set('Manual')
    t0=time.clock()
    update()
#------------------------------------------------------ fetchTLE  
def fetchTLE(url) :
    """Method for fetching list of TLE from a website, parsing, and loading into a dictionary"""
    satlist = dict()
    # Download AMSAT TLE file
    tledatafile = urllib2.urlopen(TLEURL)
    tledata = tledatafile.read()
    tleEntries = tledata.split("\n")
    for i in range(0, len(tleEntries) - 2, 3) :
        satellites[tleEntries[i]] = ephem.readtle(tleEntries[i].rstrip("\r\n"), tleEntries[i + 1].rstrip("\r\n"), tleEntries[i + 2].rstrip("\r\n"))
    return satlist
#------------------------------------------------------ printPosition  
def printPosition(station, satellites) :
    """Method for printing current az/alt of tracked satellites"""
    for satname in satellites :
        station.date = ephem.now()
        satellites[satname].compute(station)
        altitude = satellites[satname].alt * DEGREES_PER_RADIAN
        azimuth = satellites[satname].az * DEGREES_PER_RADIAN
        #if (altitude > 0) :
        print(satname + ":   \taltitude = " + str(altitude) + " deg \tazimuth = " + str(azimuth) + " deg")
    return
#------------------------------------------------------ selectSatellite
def selectSatellite():
    global telescope, satellites, selectedSatellite, root, satelliteRadioButton
    """Event handler for click on Satellite radio button"""
    disable_move()
    # Calculate current position for each satellite, append to name for display in dialog
    listSatNames = []
    telescope.date = ephem.now()
    for satname in satellites :
        satellites[satname].compute(telescope)
        altitude = satellites[satname].alt * DEGREES_PER_RADIAN
        azimuth = satellites[satname].az * DEGREES_PER_RADIAN
        if altitude > 0 :
            # Put visible satellites at top of list
            listSatNames.insert(0, satname + " (" + "{0:.2f}".format(altitude) + ", " 
                + "{0:.2f}".format(azimuth) + ")")
        else :
            listSatNames.append(satname + " (" + "{0:.2f}".format(altitude) + ", " 
                + "{0:.2f}".format(azimuth) + ")")
    # Define satellite selection dialog
    satSelectDialog = Pmw.ComboBoxDialog(root,
        title = 'Satellite Selection',
        buttons = ('OK','Cancel'),
        defaultbutton = 'OK',
        combobox_labelpos = 'n',
        label_text = 'Select satellite to track',
        scrolledlist_items = listSatNames)
    satSelectDialog.withdraw()
    # Display dialog
    buttonClicked = ""
    buttonClicked = satSelectDialog.activate()
    satSelectDialog.focus_force()
    # Extract name of selected satellite
    response = satSelectDialog.get()
    # Set name of radio buttion
    selectedSatellite.set(response[:(response.find("(") - 1)])
    print "Selected: " + selectedSatellite.get()
    
#------------------------------------------------------ update
def update():
    global root_geom, celestialBodies, rotor, naz0,nel0, azDisplayRedLine, elDisplayRedLine, \
    azreq,elreq,selectedSatellite, nWriteToFile0,logFile,running, stream
    # nRun from "Enable A/D" checkbutton
    if(not running and nRun.get()):
    	# p is pyAudio stream
        stream = p.open(format=FORMAT, channels=1, rate=RATE,input=True,
                        frames_per_buffer=CHUNK_SIZE)
        running=True
    # get the number of seconds
    utc=time.gmtime(time.time())
    # Update clock label
    lst=str(telescope.sidereal_time())
    # lst format : "hh:mm:ss.ss"
    t = time.strftime('%Y %b %d\nUTC: %H:%M:%S',utc)
    if(lst[1]==':'): lst='0'+lst
    t = t + '\nLST: ' + lst[0:8]
    utcLabel.configure(text = t) 
    
    #s=rotor.read(40)
    # default: azreq and elreq are "manual mode" inputs
    el = elreq
    az = azreq
    # Find radiobutton setting
    i = ntrack.get()
    # Find desired body
    telescope.date = ephem.now()
    if i == "Manual":
        el = elreq
        az = azreq
    elif i == "W3CCX/B":                      #W3CCX/B
        az=227
        el=0
    elif i == "Stow":                       #Stow
        az=150
        el=20
    elif i in celestialBodies:            # Celestial body in dictionary
        celestialBodies[i].compute(telescope)
        az=celestialBodies[i].az * DEGREES_PER_RADIAN
        el=celestialBodies[i].alt * DEGREES_PER_RADIAN
    elif i == "Satellite" :
        if selectedSatellite.get() in satellites :
            satellites[selectedSatellite.get()].compute(telescope)
            az=satellites[selectedSatellite.get()].az * DEGREES_PER_RADIAN
            el=satellites[selectedSatellite.get()].alt * DEGREES_PER_RADIAN
        else :
            print "Invalid satellite: " + selectedSatellite.get()
            az = 150
            el = 20
    else :
        az=150
        el=20
    #else:                                #From azel.dat (NOTE: does not seem to access azel.dat)
    #    try:
    #        az=float(s[i-2][9:14])
    #        el=float(s[i-2][15:20])
    #    except:
    #       az=naz0
    #       el=nel0
    
    # Offset radio buttons
    eloff=float(offset.get()) # Value in offset textbox
    azoff=eloff/math.cos(el/DEGREES_PER_RADIAN)
    noff=noffset.get() # ID number for currently selected radio button
    # Three point scanning mode
    if nThreePoint.get():
        n=(int(time.clock())/15) % 4
        if n==0: noff=1
        if n==1: noff=2
        if n==2: noff=1
        if n==3: noff=4
        noffset.set(noff)
    # Determine correct offset
    if noff==2:
        az=az - azoff
    elif noff==3:
        el=el + eloff
    elif noff==4:
        az=az + azoff
    elif noff==5:
        el=el-eloff

    # Update "requested" textbox
    naz=nint(az)
    nel=nint(el)
    t=str(naz) + '  ' + str(nel)
    azelreq.configure(text=t)

    azpc=0                          #Pointing corrections
    elpc=0                          #was -1
    az_command=naz+azpc
    el_command=nel+elpc
    
    # Prevent negative elevation
    if el_command<0: el_command=0
    
    # Move the rotors
    if moveok :
        rotor.setPosition(az_command,el_command)
        
    # Update current position display
    azNow = rotor.getAzimuth()
    elNow = rotor.getElevation()
    azmove = (rotor.getSpeed("A")) > 0
    elmove = rotor.getSpeed("E") > 0
    # aa = current az
    # ae = current el
    # az/elmove = bool is currently moving?
    #if aa != -99: azNow = aa
    #if ee != -99: elNow = ee
    azelActual.configure(text = (str(nint(azNow)) + '  ' + str(nint(elNow))))
    # dB Display
    pwr=0
    db=0
    if(nRun.get()):
        data = array('h', stream.read(CHUNK_SIZE))
        pwr=dot(data,data)/len(data)
        if pwr<1.0: pwr=1.0
        rms=math.sqrt(pwr)
        db=10.0*math.log10(pwr)
        if noffset.get()==1:
            s1=s1+pwr
            n1+=1
        if noffset.get()==2:
            s2=s2+pwr
            n2+=1
        if noffset.get()==4:
            s4=s4+pwr
            n4+=1
        y=1.0
        ydb=0.0
        if n2+n4>0 and azmove==0:
            base=float(s2+s4)/(n2+n4)
            if n1>0:
                y=float(s1/n1)/base
##                    print s1,s2,s4,n1,n2,n4,(s1/n1),base,y
                if y>0:
                    ydb=10.0*math.log10(y)
        t=" P:%7.2f dB\n Y:%7.3f dB" % (db-50,ydb)
        noiseLab.configure(text=t)
##            print "%15.3f  %10.3f %8.2f %8.0f %8.3f" % \
##                (time.time(),time.clock(),rms,pwr,db)

    t0="%7.1f  %d %7.1f  %d  %d" % (azNow,azmove,elNow,elmove,noffset.get())
    f0.seek(0)
    f0.write(t0+'\n')
    
    # Update red arrow on display
    naz=nint(az)
    if naz!=naz0:
        naz0=naz
        x=75*math.sin(az/DEGREES_PER_RADIAN)
        y=-75*math.cos(az/DEGREES_PER_RADIAN)
        x1=x0-x
        x2=x0+x
        y1=y0-y
        y2=y0+y
        graph1.delete(azDisplayRedLine)
        azDisplayRedLine=graph1.create_line(x1,y1,x2,y2,width=4,arrow='last',
            fill='red',tags='azpointer')

    nel=nint(el)
    if el!=nel0:
        nel0=nel
        graph2.delete(elDisplayRedLine)
        y=220 - nel*(200.0/80.0)
        elDisplayRedLine=graph2.create_line(25,y,32,y,fill='red',width=4)
    
    # Write to log if checkbox for "Write to File" is enabled
    if nWriteToFile.get():
        if nWriteToFile0==0:
            t=str(int(time.clock()))
            logFile=open(appdir+'/'+t+'.dat',mode='w')
        t1="%9.1f  %6.1f  %d  %6.1f  %d  %d %8.0f %8.2f" % \
            (time.clock(),azNow,azmove,elNow,elmove,noffset.get(),pwr,db)
        t2=time.strftime('%H:%M:%S',utc) + " " + lst[:8] + t1
        print t2
        logFile.write(t2+'\n')
        logFile.flush()
    else:
        print t0
        if nWriteToFile0==1:
            logFile.close()
    nWriteToFile0=nWriteToFile.get()
    # End section repeated every second
    root_geom=root.geometry()

#------------------------------------------------------ mainUpdateLoop
def mainUpdateLoop() :
    global root
    """Actions performed once per second"""
    update()
    root.after(1000,mainUpdateLoop)

#------------------------------------------------------ Top level frame
frame = Frame(root)

iframe2 = Frame(frame, bd=1, relief=FLAT)
iframe2.pack(expand=1, fill=X, padx=4)

#-------------------------------------------------------------- Option buttons
cbLoad=IntVar()
cbRxLinrad=IntVar()
cbLinToWSJT=IntVar()
cbTxV=IntVar()

group1=Pmw.Group(frame,tag_pyclass=None)
group1.pack(fill=BOTH,expand=1,padx=6,pady=6)
utcLabel=Label(group1.interior(), bg='black', fg='yellow', width=14, bd=4,
    text='UTC: 01:23:45', relief=RIDGE,justify=CENTER, font=(font1,16))
utcLabel.pack(side=LEFT,padx=5,pady=5)

frame1a = Frame(group1.interior(), bd=0, relief=FLAT)
Checkbutton(frame1a,text="Enable A/D",variable=nRun).pack(side=TOP,anchor=W)
Checkbutton(frame1a,text="3 Point",variable=nThreePoint).pack(side=TOP,anchor=W)
Checkbutton(frame1a,text="Write to File",variable=nWriteToFile).pack(side=TOP,anchor=W)
frame1a.pack(side=LEFT)

noiseLab=Label(group1.interior(), width=12, bd=4, text='0.0 dB',font=(font1,14))
noiseLab.pack(side=LEFT)

# Radiobuttons for target selection
ntrack=StringVar()
ntrack.set('Stow')
group3=Pmw.Group(frame,tag_text='Pointing')
group3.pack(fill=BOTH,expand=1,padx=6,pady=6)
Radiobutton(group3.interior(),text='Manual',anchor=W,variable=ntrack, \
    value='Manual',command=disable_move).grid(row=0,column=0,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Moon',anchor=W,variable=ntrack, \
    value='Moon',command=disable_move).grid(row=0,column=1,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Sun',anchor=W,variable=ntrack, \
    value='Sun',command=disable_move).grid(row=0,column=2,sticky=W,padx=5)
Radiobutton(group3.interior(),text='0329+54',anchor=W,variable=ntrack, \
    value="PSR B0329+54",command=disable_move).grid(row=0,column=3,sticky=W,padx=5)
Radiobutton(group3.interior(),text='W3CCX/B',anchor=W,variable=ntrack, \
    value='W3CCX/B',command=disable_move).grid(row=0,column=4,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Stow',anchor=W,variable=ntrack, \
    value='Stow',command=disable_move).grid(row=0,column=5,sticky=W,padx=5)

Radiobutton(group3.interior(),text='Cas',anchor=W,variable=ntrack, \
    value="Cassiopeia A",command=disable_move).grid(row=1,column=0,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Cyg',anchor=W,variable=ntrack, \
    value="Cygnus A",command=disable_move).grid(row=1,column=1,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Leo',anchor=W,variable=ntrack, \
    value="Leo",command=disable_move).grid(row=1,column=2,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Sgr',anchor=W,variable=ntrack, \
    value="Sagittarius A",command=disable_move).grid(row=1,column=3,sticky=W,padx=5)
Radiobutton(group3.interior(),text='Tau',anchor=W,variable=ntrack, \
    value="Taurus A",command=disable_move).grid(row=1,column=4,sticky=W,padx=5)
Radiobutton(group3.interior(),textvariable = selectedSatellite,anchor=W,variable=ntrack, \
    value="Satellite",command=selectSatellite).grid(row=1,column=5,sticky=W,padx=5)

# Azimuth display dial
iframe4 = Frame(frame, bd=2, relief=GROOVE)
graph1=Canvas(iframe4, width=240, height=240,cursor='crosshair')
graph1.create_oval(20,20,220,220)

r=8 # Radius of center circle
graph1.create_oval(x0-r,y0-r,x0+r,y0+r,outline='red',fill='red')
azDisplayRedLine=graph1.create_line(x0-1,y0-1,x0+1,y0+1,fill='red')
# Draw small hash marks
for i in range(0,360,10):
    x1=x0 + 90*math.sin(i/DEGREES_PER_RADIAN)
    y1=y0 - 90*math.cos(i/DEGREES_PER_RADIAN)
    x2=x0 + 100*math.sin(i/DEGREES_PER_RADIAN)
    y2=y0 - 100*math.cos(i/DEGREES_PER_RADIAN)
    graph1.create_line(x1,y1,x2,y2)
# Draw large hash marks every 30 deg
for i in range(0,360,30):
    x1=x0 + 80*math.sin(i/DEGREES_PER_RADIAN)
    y1=y0 - 80*math.cos(i/DEGREES_PER_RADIAN)
    x2=x0 + 100*math.sin(i/DEGREES_PER_RADIAN)
    y2=y0 - 100*math.cos(i/DEGREES_PER_RADIAN)
    graph1.create_line(x1,y1,x2,y2)
    x3=x0 + 110*math.sin(i/DEGREES_PER_RADIAN)
    y3=y0 - 110*math.cos(i/DEGREES_PER_RADIAN)
    # Draw text labels
    t=str(i)
    graph1.create_text(x3,y3,text=t)
# Bind event handlers
Widget.bind(graph1,"<Button-1>",mouse_click_az)
graph1.pack(side=LEFT)
iframe4.pack(side=LEFT)

# Elevation meter
graph2=Canvas(frame, width=32, height=240,cursor='crosshair')
for i in range(0,81,10):
    y=220 - i*(200.0/80.0)
    graph2.create_line(20,y,27,y)
    t=str(i)
    graph2.create_text(10,y,text=t)
# Bind event handler
Widget.bind(graph2,"<Button-1>",mouse_click_el)
elDisplayRedLine=graph2.create_line(25,220,32,220,fill='red',width=4)
graph2.pack(side=LEFT,padx=20)

# Offset widget
noffset=IntVar() # ID for direction of offset
iframe5 = Frame(frame, bd=0, relief=FLAT)

group4=Pmw.Group(iframe5,tag_text='Offset')
group4.pack(side=TOP,expand=0,padx=6,pady=1)
Radiobutton(group4.interior(),variable=noffset, \
    value=1).grid(row=1,column=1)
Radiobutton(group4.interior(),variable=noffset, \
    value=2).grid(row=1,column=0)
Radiobutton(group4.interior(),variable=noffset, \
    value=3).grid(row=0,column=1)
Radiobutton(group4.interior(),variable=noffset, \
    value=4).grid(row=1,column=2)
Radiobutton(group4.interior(),variable=noffset, \
    value=5).grid(row=2,column=1)
noffset.set(1)
offset=StringVar()
Entry(group4.interior(),width=5,textvariable=offset).grid(row=4,column=1,pady=1)
offset.set(' 16.0') # offset is string with current value of offset textbox

# Requested rotator setting display
group5=Pmw.Group(iframe5,tag_text='Requested')
group5.pack(side=TOP,expand=0,padx=6,pady=1)
azelreq=Label(group5.interior(), bg='black', fg='yellow', width=8, bd=4,
    text='145  0', relief=RIDGE,justify=CENTER, font=(font1,18))
azelreq.pack(side=TOP,padx=5,pady=1)

# Actual rotator setting display
group6=Pmw.Group(iframe5,tag_text='Actual')
group6.pack(side=TOP,expand=0,padx=6,pady=1)
azelActual=Label(group6.interior(), bg='black', fg='yellow', width=8, bd=4,
    text='145  0', relief=RIDGE,justify=CENTER, font=(font1,18))
azelActual.pack(side=TOP,padx=5,pady=1)

# Stop/Go button
moveButton=Button(iframe5,text='Stop/Go',command=toggle_stop_go,padx=4,pady=1,bg='red')
moveButton.pack(side=TOP,pady=5)
iframe5.pack()
frame.pack()

#----------------------------------------------- Restore params from ini file
try:
    f=open('track.ini',mode='r')
    params=f.readlines()
except:
    params=""

# Sets window position
try:
    for i in range(len(params)):
        key,value=params[i].split()
        if   key == 'StationGeometry': root.geometry(value)
        else:
            pass
except:
    t='Error reading track.ini, continuing with defaults.'
    msgbox(t)
    try:
        t='key='+key+ "   value=" + value
        msgbox(t)
    except:
        pass

# Define and open an audio stream
p = pyaudio.PyAudio()

# Fetch and load TLE elements from url
satellites.update(fetchTLE(TLEURL))
print "Currently loaded " + str(len(satellites)) + " satellites"
# Starts update loop
graph1.after(100,mainUpdateLoop) 
root.title('  W2PU Track')
root.mainloop()

if(running):
    stream.stop_stream()                            #Stop and close the audio stream
    stream.close()
p.terminate()                                   #Terminate pyaudio

f=open(appdir+'/track.ini',mode='w')
root_geom=root_geom[root_geom.index("+"):]
f.write("StationGeometry " + root_geom + "\n")
f.close()