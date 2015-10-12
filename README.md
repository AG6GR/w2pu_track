w2pu_track
=====
Antenna Rotator control program for the W2PU station. The program interfaces with two RC2800PX antenna rotators to allow tracking of various celestial bodies, such as the Sun and Moon, and man-made satellites.

The original w2pu_track program was written by K1JT, who kindly gave permission and the original celestial body tracking source code for AG6GR to continue development. More details are in the Development History section below.

Development History
-----

The original w2pu_track.py application was written by K1JT as a rotor control program for the W2PU station. During the winter of 2015, AG6GR worked on extending the program to allow satellite tracking. In addition, AG6GR performed some restructuring of the original w2pu_track source code including the abstraction of serial communications with the station's rotor controllers into a dedicated Rotator class. 

The primary goals of this project included:
<ul>
<li> <b>Backwards compatibility:</b> Since the station is also used by many other people, the UI and general code structure were preserved as much as possible. Researchers using the original celestial-body tracking functionality should not notice any difference between the versions with and without the added satellite tracking code.
<li> <b>Satellite tracking:</b> The program should fetch and decode Two-Line-Elements from the internet and accurately track satellites during passes.
</ul>

Program Structure
-----

The central script of this application is in w2pu_track.py. This script builds the UI using elements from the Pmw Python Megawidgets project. A central "update" method is called once every half second to update the UI, calculate the position of the entity being tracked, and send commands to update the rotor positions, if needed. In addition, several event handling methods are defined to handle user interaction with the user interface. Continuing to reorganizing this script will probably be the focus of further development of w2pu_track.

Rotator.py defines a Rotator class for commanding the RC2800PX antenna rotators over serial communications. TleDecoder.py contains the original TLE decoding code written by AG6GR and was mainly used for testing the functionality of the TLE decoding code outside of the rest of the w2pu_track program.

Usage
-----

Click on one of the radio buttons in the Pointing section to direct the antennas to your target of choice. By default, the available targets include celestial objects such as the sun and moon, the radio beacon W3CCX/B at 432.288 MHz, and the default Stow position. The final radio button enables satellite tracking mode.

<p align="center"><img src ="https://github.com/AG6GR/w2pu_track/blob/master/doc/TrackWindow.PNG" align="center" />
</p>
<p align="center"><em>Figure 1: Main Window</em></p>

When Manual pointing mode is selected, click on the scales below to request a specified Azimuth or Elevation. Valid ranges are 0-360 degrees in Azimuth, 0-75 degrees Elevation. The Azimuth stop is at 0 deg (due North). The antenna moves only when the Stop/Go button is toggled to Green background. Changing the currently targeted object, clicking on the azimuth or elevation displays, or clicking on the Stop/Go button while the antenna is moving will immediately stop the rotators.

Satellite Tracking
-----

When the program starts, it will create a database of satellites using two-line elements from one of two sources. The user may manually provide NORAD style two-line elements in the text file `TLE.txt` located in the `src` directory. Additionally, the program will attempt to fetch two-line elements from the web. By default, the program is configured to use the [AMSAT Keplerian Element Database.] (http://www.amsat.org/amsat-new/tools/keps.php) Both of these sources can be changed by modifying the values of global variables `TLEURL` and `TLEFILENAME` in `w2pu_track.py`.

Clicking on the last radio button labeled "Satellite" will switch to satellite tracking mode. A dialog should appear showing the satellites currently being tracked by the program. The name of each tracked satellite is listed along with its current position in the format `(elevation, azimuth)`
<p align="center"><img src ="https://github.com/AG6GR/w2pu_track/blob/master/doc/SatSelectDialog.PNG" align="center" />
</p>

<p align="center"><em>Figure 2: Satellite Selection Dialog</em></p>
Once a satellite has been selected, the radio button label will be updated to refer to the currently selected satellite. Clicking on the button again will reopen the selection dialog to allow a different satellite to be selected.
