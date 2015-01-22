#--------------------------------------------------------------  w2pu_track
#
from Tkinter import *
from tkFileDialog import *
import Pmw, serial, os, time, math, stat, ephem

root = Tk()

Win32=0
if sys.platform=="win32":
    Win32=1
    try:
        root.option_readfile('station_rc.win')
    except:
        pass
else:
    try:
        root.option_readfile('station_rc')
    except:
        pass

appdir=os.getcwd()
root_geom=""
font1='Helvetica'

isec0=0
az=0
az0=-999
az00=-999
c2=0
moveok=0
naz0=az0
el0=-999
nel0=0
t0=0.
x0=120
y0=120
azreq=153
azreq0=0
elreq=0
azSun=0.
elSun=0.
azMoon=0.
elMoon=0.
azPSR=0.
elPSR=0.

if sys.platform=="win32":
#Rotor control port    
    rotor=serial.Serial("COM1",9600,timeout=0.1)
else:
    rotor=serial.Serial("/dev/ttyS0",9600,timeout=0.1)         #Rotor control port

telescope = ephem.Observer()
telescope.long =  ephem.degrees('-74.625')
telescope.lat = ephem.degrees('40.35417')
telescope.elevation = 43


#---------------------------------------------------------- rotors
def set_rotors(az_command,el):
    global az,az0,el0,moveok,az00,t0

    rotor.write("A\r")
    s=rotor.read(128)
    i0=s.find("A=")+2
    i1=i0 + s[i0:].find(" ")
    try:
        az=float(s[i0:i1])
        i2=s.find("S=")+2
        speed=int(s[i2:i2+1])
    except:
        pass
##    if abs(az-az00)>=0.1:
    if abs(az-az00)>=0:
        hms=time.asctime(time.localtime(time.time()))
        try:
            print "%s %8.2f  %7.1f   %d" % (hms,time.clock()-t0,az,speed)
        except:
            pass
        az00=az

    if moveok:
        if az_command < 1: az_command=1
        if az_command > 359: az_command=359
        if el < 0: el=0
        if el > 80: el=80

        if abs(az_command-az0) >= 2.5:
            utc=time.gmtime(time.time())
            s=rotor.read(128)
            t="A" + str(az_command) + "\r"
            rotor.write(t)
            az0=az_command

        if abs(el-el0) >= 1.5:
            utc=time.gmtime(time.time())
            rotor.flushInput()
            t="E" + str(el) + "\r"
#            print "Written (El): ",t
#            rotor.write(t)
#            s=rotor.read(14)
#            print "Read (El): ",s
            el0=el


#--------------------------------------------------------- move_rotors
def move_rotors(event=NONE):
    global moveok,t0
    moveok=1-moveok
    if moveok:
        move.configure(bg='green')
        t0=time.clock()
    else:
        move.configure(bg='red')

#--------------------------------------------------------- freeze_rotors
def freeze_rotors(event=NONE):
    global moveok
    moveok=0
    move.configure(bg='red')

#-------------------------------------------------------------- nint
def nint(x):
    if(x>0):
        return int(x+0.5)
    else:
        return int(x-0.5)

#------------------------------------------------------ msgbox
def msgbox(t):
    msg=Pmw.MessageDialog(root,buttons=('OK',),message_text=t)
    result=msg.activate()
    msg.focus_set()

#------------------------------------------------------ mouse_click_g1
def mouse_click_g1(event):
    global x0,azreq,t0
    x=event.x - x0
    y=event.y - x0
    azreq=nint(57.2957795*math.atan2(x,-y))
    if(azreq<0): azreq=azreq+360
    t0=time.clock()

#------------------------------------------------------ mouse_click_g2
def mouse_click_g2(event):
    global elreq,t0
    y=event.y
    if y<20: y=20
    if y>220: y=220
    elreq = (220-y)*(80.0/200.0)
    t0=time.clock()

#---------------------------------------------------------- track
def track():
    global azSun,elSun,azMoon,elMoon,azPSR,elPSR
    telescope.date = ephem.now()
    s = ephem.Sun()
    s.compute(telescope)
    azSun=s.az*57.2957795131
    elSun=s.alt*57.2957795131
##    print "Sun:          %7.2f  %7.2f" % (azSun,elSun)

    m = ephem.Moon()
    m.compute(telescope)
    azMoon=m.az*57.2957795131
    elMoon=m.alt*57.2957795131
##    print "Moon:         %7.2f  %7.2f" % (azMoon,elMoon)
    
    psr = ephem.FixedBody()
    psr._ra = ephem.hours('03:29:11')
    psr._dec = ephem.degrees('54:24:37')
    #print psr._epoch
    psr._epoch="1950/1/1 00:00:00"
    #print psr._epoch
    psr.compute(telescope)
    azPSR=psr.az*57.2957795131
    elPSR=psr.alt*57.29577951
##    print "PSR B0329+54: %7.2f  %7.2f" % (azPSR,elPSR)

#------------------------------------------------------ update
def update():
    global root_geom,isec0,naz0,nel0,c,c2,azreq,elreq,azreq0,azSun,elSun, \
        azMoon,elMoon,azPSR,elPSR

    utc=time.gmtime(time.time())
    isec=utc[5]
    if isec != isec0:                           #Do once per second
##        isec0=isec
        isec=-999
        s=rotor.read(40)
        track()
        el=elreq
        az=azreq

        i=ntrack.get()
        if i==1:                                #Manual
            az=azreq
        elif i==2:                              #
            az=azMoon
            el=elMoon
        elif i==3:                              #
            az=azSun
            el=elSun
        elif i==4:                              #
            az=azPSR
            el=elPSR
        elif i==5:                              #Service position
            az=297
            el=30
        elif i==6:                              #Stow position
            az=147                              #was 153
            el=0
        else:                                   #From azel.dat
            try:
                az=float(s[i-2][9:14])
                el=float(s[i-2][15:20])
            except:
                az=naz0
                el=nel0

        naz=nint(az)
        if naz<>naz0:
            naz0=naz
            x=75*math.sin(az/57.2957795)
            y=-75*math.cos(az/57.2957795)
            x1=x0-x
            x2=x0+x
            y1=y0-y
            y2=y0+y
            graph1.delete(c)
            c=graph1.create_line(x1,y1,x2,y2,width=4,arrow='last',
                fill='red',tags='azpointer')

        nel=nint(el)
        if el<>nel0:
            nel0=nel
            graph2.delete(c2)
            y=220 - nel*(200.0/80.0)
            c2=graph2.create_line(25,y,32,y,fill='red',width=4)

        eloff=float(offset.get())
        azoff=eloff/math.cos(el/57.2957795)
        if noffset.get()==2:
            az=az - azoff
        elif noffset.get()==3:
            el=el + eloff
        elif noffset.get()==4:
            az=az + azoff
        elif noffset.get()==5:
            el=el-eloff
        else:
            pass

        naz=nint(az)
        nel=nint(el)
        t=str(naz) + '  ' + str(nel)
        azelreq.configure(text=t)
        azpc=0                          #Pointing corrections
        elpc=0                          #was -1
        az_command=naz+azpc
        el_command=nel+elpc
        if el_command<0: el_command=0
        set_rotors(az_command,el_command)
    root_geom=root.geometry()
    graph1.after(200,update)

#------------------------------------------------------ Top level frame
frame = Frame(root)

iframe2 = Frame(frame, bd=1, relief=FLAT)
iframe2.pack(expand=1, fill=X, padx=4)

#-------------------------------------------------------------- Option buttons
cbLoad=IntVar()
cbRxLinrad=IntVar()
cbLinToWSJT=IntVar()
cbTxV=IntVar()

ntrack=IntVar()
ntrack.set(1)
group3=Pmw.Group(frame,tag_text='Pointing')
group3.pack(fill=BOTH,expand=1,padx=6,pady=6)
Radiobutton(group3.interior(),text='Manual',anchor=W,variable=ntrack, \
    value=1,command=freeze_rotors).grid(row=0,column=0,sticky=W,padx=2)
Radiobutton(group3.interior(),text='Moon',anchor=W,variable=ntrack, \
    value=2,command=freeze_rotors).grid(row=0,column=1,sticky=W,padx=2)
Radiobutton(group3.interior(),text='Sun',anchor=W,variable=ntrack, \
    value=3,command=freeze_rotors).grid(row=0,column=2,sticky=W,padx=2)
Radiobutton(group3.interior(),text='PSR B0329+54',anchor=W,variable=ntrack, \
    value=4,command=freeze_rotors).grid(row=0,column=3,sticky=W,padx=2)
Radiobutton(group3.interior(),text='Service',anchor=W,variable=ntrack, \
    value=5,command=freeze_rotors).grid(row=0,column=4,sticky=W,padx=2)
Radiobutton(group3.interior(),text='Stow',anchor=W,variable=ntrack, \
    value=6,command=freeze_rotors).grid(row=0,column=5,sticky=W,padx=2)

iframe4 = Frame(frame, bd=2, relief=GROOVE)
graph1=Canvas(iframe4, width=240, height=240,cursor='crosshair')
graph1.create_oval(20,20,220,220)

r=8
graph1.create_oval(x0-r,y0-r,x0+r,y0+r,outline='red',fill='red')
c=graph1.create_line(x0-1,y0-1,x0+1,y0+1,fill='red')

for i in range(0,360,10):
    x1=x0 + 90*math.sin(i/57.2957795)
    y1=y0 - 90*math.cos(i/57.2957795)
    x2=x0 + 100*math.sin(i/57.2957795)
    y2=y0 - 100*math.cos(i/57.2957795)
    graph1.create_line(x1,y1,x2,y2)
for i in range(0,360,30):
    x1=x0 + 80*math.sin(i/57.2957795)
    y1=y0 - 80*math.cos(i/57.2957795)
    x2=x0 + 100*math.sin(i/57.2957795)
    y2=y0 - 100*math.cos(i/57.2957795)
    graph1.create_line(x1,y1,x2,y2)
    x3=x0 + 110*math.sin(i/57.2957795)
    y3=y0 - 110*math.cos(i/57.2957795)
    t=str(i)
    graph1.create_text(x3,y3,text=t)

Widget.bind(graph1,"<Button-1>",mouse_click_g1)
graph1.pack(side=LEFT)
iframe4.pack(side=LEFT)

graph2=Canvas(frame, width=32, height=240,cursor='crosshair')
for i in range(0,81,10):
    y=220 - i*(200.0/80.0)
    graph2.create_line(20,y,27,y)
    t=str(i)
    graph2.create_text(10,y,text=t)
Widget.bind(graph2,"<Button-1>",mouse_click_g2)
c2=graph2.create_line(25,220,32,220,fill='red',width=4)
graph2.pack(side=LEFT,padx=20)

noffset=IntVar()
iframe5 = Frame(frame, bd=0, relief=FLAT)

group4=Pmw.Group(iframe5,tag_text='Offset')
group4.pack(side=TOP,expand=0,padx=6,pady=6)
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
Entry(group4.interior(),width=5,textvariable=offset).grid(row=4,column=1,pady=5)
offset.set('  9.0')

azelreq=Label(iframe5, bg='black', fg='yellow', width=8, bd=4,
    text='145  0', relief=RIDGE,justify=CENTER, font=(font1,18))
azelreq.pack(side=TOP,pady=15)

move=Button(iframe5,text='Stop/Go',command=move_rotors,padx=4,pady=4,bg='red')
move.pack(side=TOP,pady=5)

iframe5.pack()

frame.pack()

elreq=0

graph1.after(100,update)
root.title('  W2PU Track')
root.mainloop()

