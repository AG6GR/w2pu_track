class Rotator :
	"""Class for serial control of RC2800PX antenna rotators"""

	def __init__(self, port) :
		"""Constructs Rotator object attached to the specified port.
		
		Args:
			port: (String) the serial port corresponding to the antenna rotator."""
		self.rotor = serial.Serial(port = port, baudrate = 9600, timeout = 0.1)
		
	def __del__(self):
		if (self.rotor != null) :
			self.rotor.close()
		
	def getAzimuth(self) :
		"""Returns the current Azimuth of the antenna.
		
		Returns:
			(float) Current azimuth in degrees."""
		response = ""
		while (len(response) < 4) :
			self.rotor.flushInput();
			# Request Azimuth mode
			self.rotor.write("A\r")
			# Read response, example response: "A\r\nA=150.5 S=6 S\r\n"
			response = self.rotor.read(128)
		# Extract position value
		startIndex = response.find("A=") + 2
		endIndex = startIndex + response[startIndex:].find(" ")
		try:
			return float(response[startIndex:endIndex])
		except:
			# Possible communications error, try again
			return self.getAzimuth()
	
	def getElevation(self) :
		"""Returns the current Elevation of the antenna.
		
		Returns:
			(float) Current elevation in degrees."""
		response = ""
		while (len(response) < 4) :
			self.rotor.flushInput();
			# Request Elevation mode
			self.rotor.write("E\r")
			# Read response, example response: "A\r\nA=150.5 S=6 S\r\n"
			response = self.rotor.read(128)
		# Extract position value
		startIndex = response.find("E=") + 2
		endIndex = startIndex + response[startIndex:].find(" ")
		try:
			return float(response[startIndex:endIndex])
		except:
			# Possible communications error, try again
			return self.getAzimuth()
	def getSpeed(axis) :
		"""Returns the current speed for the given axis (A or E).
		
		Args:
			axis: (String) Either "A" for Azimuth or "E" for Elevation.
		Returns:
			(int) Speed value for the selected axis."""
		self.rotor.flushInput();
		self.rotor.write(axis + "\r")
		response = self.rotor.read(128)
		# Extract position value
		try:
			index = response.find("S=") + 2
			return int(response[index])
		except:
			# Possible communications error, try again
			return self.getSpeed(axis)
		
	def setPosition(self, reqAzimuth, reqElevation) :
		"""Commands rotor toward requested azimuth and elevation.
		
		Args:
			reqAzimuth: (float) Requested azimuth in degrees.
			reqElevation: (float) Requested elevation in degrees."""
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
	
	def setSpeed(newSpeed, axis) :
		"""Sets speed for selected axis (A or E).
		
		Args:
			newSpeed: (int) Desired speed.
			axis: (String) Either "A" for Azimuth or "E" for Elevation.
		Returns:
			(String) Response received after axis select command."""
		# Limit to reasonable values
		if newSpeed < 1: newSpeed = 1
		if newSpeed > 9: newSpeed = 9
		# Issue axis command
		self.rotor.flushInput();
		self.rotor.write(axis + "\r")
		##print "Written: " + axis + "\r"
		# readline() is critical to ensure correct timing
		response = self.rotor.readline()
		self.rotor.write("S" + newSpeed + "\r")
		return response
		
	def stop(self) :
		"""Sends a stop command (S) to the rotator."""
		print "Stopping...\r\n"
		self.rotor.flushInput();
		self.rotor.flushOutput();
		self.rotor.write("S\r");
		print self.rotor.readline()
		# Send twice for redundancy, ensures that both axises stop
		self.rotor.write("S\r");
		print self.rotor.readline()
		return
		
	def printPosition(self) :
		"""Reads and prints the current azimuth and elevation of the antenna."""
		print("Azimuth: " + str(self.getAzimuth()) + " Elevation: " + str(self.getElevation()))
		return
# Test code
if __name__ == '__main__':
	import serial
	
	rotor = Rotator("COM1")
	print rotor.printPosition()