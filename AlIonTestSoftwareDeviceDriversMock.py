from random import randrange
from tkinter import *
import pyvisa

# Class for communication with the NI-VISA driver to control the power supply
class PowerSupplyControllerMock:
    # Variable to keep the resource name of the power supply

    def __init__(self) -> None:
        self.powerSupplyName = "USB0::0x1698::0x0837::011000000136::INSTR"
        self.Voltage_limmax = 10
        self.Current_limmax = 10
        self.Power_limmax = 10
        self.resourceManager = pyvisa.ResourceManager()
        self.powerSupply = self.resourceManager.open_resource(self.powerSupplyName)

    # Function that returns the name of connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")

    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    # Functions that allow user to set the maximum voltage, current and power for safety
    def setVoltage(self, volts : float):
        self.setVoltage = volts

    def setVoltageLimMax(self, volts : float):
        self.Voltage_limmax = volts

    def setVoltageSlew(self, volts : float):
        self.Voltage_slew = volts


    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def setCurrentLimMax(self, amps : float):
        self.Current_limmax = amps

    def setCurrentSlew(self, amps : float):
        self.Voltage_slew = amps

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def setMaxPower(self, watts : float):
        self.Power_limmax = watts

    def setVoltageProt(self, *volts):
        self.powerSupply.write("SOUR:VOLT:PROT:HIGH " + str((volts[0])))


    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply
    def getVoltage(self):
        print("mock)")
        return randrange(self.VoltageLimMax * 10000000) / 100000000

    def getCurrent(self):
        return randrange(self.Current_limmax * 10000000) / 100000000

    def getPower(self):
        return randrange(self.Power_limmax * 10000000) / 100000000
        

    # Function for constant CURRENT charging, taking in current in ampers
    def chargeCC (self, ampers : float):
        pass

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def chargeCV(self, volts : float):
        pass

    # Function for constant POWER charging, taking in power in watts
    def chargePW(self, watts : float):
        pass

    # Function for constant POWER charging, taking in power in watts
    def startOutput(self):
        pass

    def stopOutput(self):
        pass

# Class for communication with the NI-VISA driver to control the electronic load
class ElectronicLoadControllerMock:
    # Variable to keep the resource name of the electronic load
    electronicLoadName = "USB0::0x0A69::0x083E::000000000001::INSTR"

    maxVoltage = 10
    maxCurrent = 10
    maxPower = 10

    # Function that returns the name of the connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")

    def setMaxCurrent(self, amps):
        self.maxCurrent = amps

    def getVolts(self):
        return randrange(self.maxVoltage * 10000000) / 10000000

    def getCurrent(self):
        return randrange(self.maxCurrent * 10000000) / 10000000

    def getPower(self):
        return randrange(self.maxPower * 10000000) / 10000000


    

    def dischargeCV(self, volts):
        pass

    def dischargeCC(self, amps):
        pass

    def dischargeCP(self, watts):
        pass

    def stopDischarge(self):
        pass

# Class for communication with the NI-VISA driver to control the multimeter
class MultimeterControllerMock:
    
    # Variable to keep the resource name of the mutimeter
    multimeterName = "USB0::0x1698::0x083F::TW00014586::INSTR"

    # Function that returns the name of the connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")


    def getTemperature(self):
        return randrange(10000000) / 10000000

    def getVolts(self):
        return randrange(10000000) / 10000000

    def getResistance(self):
        return randrange(10000000) / 10000000

