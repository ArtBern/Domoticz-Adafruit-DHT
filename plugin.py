#		   CCS811 Plugin
"""
<plugin key="CCS811Reader" name="CO2 CCS811 Reader" author="artbern" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
	<description>
		<h2>CCS811 Reader</h2><br/>
		Overview...
		<h3>Features</h3>
		<ul style="list-style-type:square">
			<li>Feature one...</li>
			<li>Feature two...</li>
		</ul>
		<h3>Devices</h3>
		<ul style="list-style-type:square">
			<li>Device Type - What it does...</li>
		</ul>
		<h3>Configuration</h3>
		Configuration options...
	</description>
	<params>
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal"  default="true" />
			</options>
		</param>    
	</params>
</plugin>
"""
import Domoticz

class BasePlugin:
	enabled = False
	
	def __init__(self):
		self.ccs811 = None
		self.lastGoodMeasured = dict(temp=20,humi=30,co2=800)
		
		

	def onStart(self):

		Domoticz.Log("onStart called")
	
		if Parameters["Mode6"] == "Debug":
			Domoticz.Debugging(1)

		if (len(Devices) == 0):
			Domoticz.Device(Name="CCS811 C02", Unit=1, TypeName="Air Quality", Used=1).Create()

		Domoticz.Debug("Device created.")
		DumpConfigToLog()

		try:
			#installed with 
			#sudo pip3 install adafruit-circuitpython-ccs811
			import board
			import busio
			import adafruit_ccs811
			 
			i2c = busio.I2C(board.SCL, board.SDA)
			ccs811 = adafruit_ccs811.CCS811(i2c)        
			
			# Wait for the sensor to be ready and calibrate the thermistor
			i = 0
			while not ccs811.data_ready and i < 10000:
				i = i + 1
				pass
			
			self.ccs811 = ccs811
			
		except ImportError as e:
			Domoticz.Log("Error loading Adafruit_CCS811: {0}:{1}".format(e.__class__.__name__, e.message)) 
		except RuntimeError as er:
			Domoticz.Log("Error running Adafruit_CCS811: {0}:{1}".format(er.__class__.__name__, str(er))) 
		
		Domoticz.Heartbeat(10)
		
	def onStop(self):
		Domoticz.Log("onStop called")

	def onConnect(self, Connection, Status, Description):
		Domoticz.Log("onConnect called")

	def onMessage(self, Connection, Data):
		Domoticz.Log('received')
		strData = Data.decode("utf-8", "ignore")
		Domoticz.Debug("onMessage called with Data: '"+str(Data)+"'")

	def onCommand(self, Unit, Command, Level, Hue):
		Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

	def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
		Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

	def onDisconnect(self, Connection):
		Domoticz.Log("onDisconnect called")

	def onHeartbeat(self):
		try:

			Domoticz.Debug("In onHeartBeat. Prev value:       '" + str(self.lastGoodMeasured["co2"]) + "'")
		
			if self.ccs811 is not None:
				self.lastGoodMeasured = dict(temp=self.ccs811.temperature,humi=40,co2=self.ccs811.eco2)

			#if (rawHumi is not None and rawHumi < 101) and rawTemp is not None:
			#   self.temperatureBuffer.append(rawTemp)
			#print "@%s, Average: %s" % (self.temperatureBuffer, self.temperatureBuffer.average)
			 #  self.lastGoodMeasured = dict(temp=self.temperatureBuffer.average,humi=rawHumi,co2=800)

		except OSError as e:
			Domoticz.Log("OSError reading Adafruit_CCS811: {0}:{1}".format(e.__class__.__name__, str(e)))
		except RuntimeError as e:
			Domoticz.Log("RuntimeError reading Adafruit_CCS811: {0}:{1}".format(e.__class__.__name__, str(e)))

		UpdateDevice(1,self.lastGoodMeasured["co2"],'',100)
		
def UpdateDevice(Unit, nValue, sValue, batterylevel):
	# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
	if (Unit in Devices):
		if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
			Devices[Unit].Update(nValue, str(sValue),BatteryLevel=batterylevel)
			Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")

global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
	global _plugin
	_plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
	global _plugin
	_plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()

	# Generic helper functions
def DumpConfigToLog():
	for x in Parameters:
		if Parameters[x] != "":
			Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
	Domoticz.Debug("Device count: " + str(len(Devices)))
	for x in Devices:
		Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
		Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
		Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
		Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
		Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
		Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
	return		