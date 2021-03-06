#          Adafruit DHT Plugin
"""
<plugin key="AdafruitDHT" name="Adafruit DHT Sensors Reader" author="artbern" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <description>
        <h2>Adafruit DHT Sensors Reader</h2><br/>
        Plugin for reading onboard DHT sensors (DHT11, DHT22, AM2301)
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
        <param field="Mode1" label="GPIO Port" width="30px"  required="true" default="22"/>
        <param field="Mode2" label="DHT Type" width="80px"  required="true">
            <options>
                <option label="DHT11" value="11"/>
                <option label="DHT22/AM2302" value="22"  default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="80px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>        
    </params>
</plugin>
"""
import Domoticz
from collections import deque

class CircularBuffer(deque):
    def __init__(self, size=0):
         super(CircularBuffer, self).__init__(maxlen=size)
    @property
    def average(self):
        return sum(self)/len(self)
        
class BasePlugin:
    enabled = False

    def __init__(self):
        self.lastGoodMeasured = dict(temp=20,humi=30)
        self.temperatureBuffer = CircularBuffer(size=20)
        
    def onStart(self):

        Domoticz.Log("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="Adafruit DHT", Unit=1, TypeName="Temp+Hum", Used=1).Create()

        Domoticz.Debug("Device created.")
        DumpConfigToLog()

        try:
            #installed with
            #sudo pip3 install Adafruit_DHT
            #sudo apt-get install libgpiod2
            import Adafruit_DHT
            Domoticz.Debug("Adafruit_DHT imported.")

        except ImportError as e:
            Domoticz.Log("Error loading Adafruit_DHT: {0}:{1}".format(e.__class__.__name__, e.message))
        except RuntimeError as er:
            Domoticz.Log("Error running Adafruit_DHT: {0}:{1}".format(er.__class__.__name__, str(er)))

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
        #Domoticz.Debug("In onHeartBeat. Prev value:       '" + str(self.lastGoodMeasured["temp"]) + "'")

        import Adafruit_DHT
        rawHumi, rawTemp = Adafruit_DHT.read_retry(int(Parameters["Mode2"]), int(Parameters["Mode1"]))

        if (rawHumi is not None and rawHumi < 101) and rawTemp is not None:
            self.temperatureBuffer.append(rawTemp)
            #print "@%s, Average: %s" % (self.temperatureBuffer, self.temperatureBuffer.average)
            self.lastGoodMeasured = dict(temp=self.temperatureBuffer.average,humi=rawHumi)

        humStatus = 0
        if rawHumi <= 25:
            humStatus = 2
        elif rawHumi > 60:
            humStatus = 3
        elif rawHumi > 25 and rawHumi <= 60:
            humStatus = 1
        else:
            humStatus = 0

        UpdateDevice(1, 0, str(round(self.lastGoodMeasured["temp"], 1)) + ";" + str(round(rawHumi,1)) + ";" + str(humStatus), 100)
        
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
 
