class Rotator :
	"""Class for serial control of RC2800PX antenna rotators"""

	def __init__(self, port) :
		self.rotor = serial.Serial(port,9600,timeout=0.1)
		
	def __del__(self):
		if (self.rotor != null) :
			self.rotor.close()
		
	def getAzimuth(self) :
		"""Returns the current Azimuth of the antenna"""
		self.rotor.flushInput();
		# Request Azimuth mode
		self.rotor.write("A\r")
		# Read response, example response: "A\r\nA=150.5 S=6 S\r\n"
		response = self.rotor.read(128)
		# Extract position value
		startIndex = response.find("A=") + 2
		endIndex = startIndex + response[startIndex:].find(" ")
		return float(response[startIndex:endIndex])
	
	def getElevation(self) :
		"""Returns the current Elevation of the antenna"""
		self.rotor.flushInput();
		# Request Elevation mode
		self.rotor.write("E\r")
		# Read response, example response: "E\r\nE=150.5 S=9 S\r\n"
		response = self.rotor.read(128)
		# Extract position value
		startIndex = response.find("E=") + 2
		endIndex = startIndex + response[startIndex:].find(" ")
		return float(response[startIndex:endIndex])
		
	def setPosition(self, reqAzimuth, reqElevation) :
		"""Commands rotor toward requested azimuth and elevation"""
		# Ensure requested position is within limits
		if reqAzimuth < 1: reqAzimuth = 1
		if reqAzimuth > 359: reqAzimuth = 359
		if reqElevation < 0: reqElevation = 0
		if reqElevation > 80: reqElevation = 80
		
		# Issue Azimuth command
		self.rotor.flushInput();
		self.rotor.write("A" + str(reqAzimuth) + "\r")
		##print "Written: " + "A" + str(reqAzimuth) + "\r"
		# readline() is critical to ensure correct timing
		response = self.rotor.readline()
		##print "Read: " + response
		
		# Issue Elevation command
		self.rotor.flushInput();
		self.rotor.write("E" + str(reqElevation) + "\r")
		##print "Written: " + "E" + str(reqElevation) + "\r"
		# readline() is critical to ensure correct timing
		response = self.rotor.readline()
		##print "Read: " + response
		return
		
	def stop(self) :
		"""Sends a stop command (S) to the rotator"""
		print "Stopping...\r\n"
		self.rotor.flushInput();
		self.rotor.flushOutput();
		self.rotor.write("S");
		print self.rotor.readline()
		return
		
	def printPosition(self) :
		"""Reads and prints the current azimuth and elevation of the antenna"""
		print("Azimuth: " + str(self.getAzimuth()) + " Elevation: " + str(self.getElevation()))
		return
# Test code
import serial

rotor = Rotator("COM1")
print rotor.printPosition()