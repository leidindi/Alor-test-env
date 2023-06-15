import copy
from math import floor
import time
import datetime
from datetime import datetime
from datetime import timedelta
import threading
from AlIonTestSoftwareDeviceDrivers import PowerSupplyController, ElectronicLoadController
from AlIonTestSoftwareDeviceDriversMock import PowerSupplyControllerMock, ElectronicLoadControllerMock, \
    MultimeterControllerMock
from AlIonTestSoftwareDataManagement import DataStorage
import random as rand
import keyboard
import pandas as pd

# Class used to control test procedures
class TestController:
    # Initiating function
    def __init__(self):
        try:
            # Trying to connect to the real device controllers
            self.powerSupplyController = PowerSupplyController()
            print("Testcontroller succesfully connected to Power Supply")
            self.electronicLoadController = ElectronicLoadController()
            print("Testcontroller succesfully connected to Electronic Load")
            # self.multimeterController = MultimeterController()
            # print("Testcontroller succesfully connected to Multimeter")
        except:
            # Connecting to the mock device controllers
            print("Connection not successful, using mock objects")
            self.powerSupplyController = PowerSupplyControllerMock()
            self.electronicLoadController = ElectronicLoadControllerMock()
            self.multimeterController = MultimeterControllerMock()
        # Indicates the number of seconds between each measurement
        self.timeInterval = 0.2
        # Variable for keeping track of the open circuit voltage of a full battery
        self.OCVFull = 0.0
        # Variable for keeping track of the open circuit voltage of an empty battery
        self.OCVEmpty = 0.0
        # Variable for keeping track of the C-rate of the battery
        self.C_rate = 0.0
        # Create an event to indicate if test is running
        self.event = threading.Event()

        self.breaker = False

    # Defining basic functionality of all remote devices through the device controller
    #####  62000P Power supply #####
    # Function for constant CURRENT charging, taking in current in ampers
    def chargeCC(self, ampers):
        self.powerSupplyController.chargeCC(ampers)

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def chargeCV(self, volts):
        self.powerSupplyController.chargeCV(volts)

    # Function for constant POWER charging, taking in power in watts
    def chargeCP(self, watts):
        self.powerSupplyController.chargeCP(watts)

    # def startCharge(self):
    #     self.powerSupplyController.st
    # Functions to START/STOP the powersupply from charging
    def startPSOutput(self):
        self.powerSupplyController.startOutput()

    def stopPSOutput(self):
        self.powerSupplyController.stopOutput()

    # Functions that allow user to set the maximum voltage, current and power for safety
    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    def setVoltage(self, volts: float):
        self.powerSupplyController.setVoltage(volts)

    def setVoltageLimMax(self, volts: float):
        self.powerSupplyController.setVoltageLimMax(volts)

    def setVoltageLimMin(self, volts: float):
        self.powerSupplyController.setVoltageLimMin(volts)

    def setVoltageProt(self, volts: float):
        self.powerSupplyController.setVoltageProt(volts)

    def setVoltageSlew(self, volts: float):
        self.powerSupplyController.setVoltageSlew(volts)

    # def setMaxVoltageMax(self):
    #     self.powerSupplyController.setVoltageMax()

    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def setCurrent(self, amps: float):
        self.powerSupplyController.setCurrent(amps)

    def setCurrentLimMax(self, amps: float):
        self.powerSupplyController.setCurrentLimMax(amps)

    def setCurrentLimMin(self, amps: float):
        self.powerSupplyController.setCurrentLimMin(amps)

    def setCurrentProt(self, amps: float):
        self.powerSupplyController.setCurrentProt(amps)

    def setCurrentSlew(self, amps: float):
        self.powerSupplyController.setCurrentSlew(amps)

    # def setMaxCurrentMax(self):
    #     self.powerSupplyController.setCurrentMax()

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def setPowerProt(self, watts: float):
        self.powerSupplyController.setPowerProt(watts)

    # def setMaxPowerMax(self):
    #     self.powerSupplyController.setPowerMax()

    ###### DISCHARGE functions ###### DC LOAD 63600-5

    def startDischarge(self):
        self.electronicLoadController.startDischarge()  # Activates the electronic load

    def stopDischarge(self):
        self.electronicLoadController.stopDischarge()  # Inactivates the electronic load

    def setCCLmode(self):
        self.electronicLoadController.setCCLmode()  # Switch to CC mode Low Range (max 0.8 amper)

    def setCCMmode(self):
        self.electronicLoadController.setCCMmode()  # Switch to CC mode Medium Range (max 8 amper)

    def setCCcurrentL1(self, amper: float):
        self.electronicLoadController.setCCcurrentL1(amper)  # Set the desired current of Channel L1

    def setCCcurrentL1MAX(self, amper: float):
        self.electronicLoadController.setCCcurrentL1MAX(amper)  # Set the desired current of Channel L1

    def getCCcurrentL1MAX(self):
        return self.electronicLoadController.getCCcurrentL1MAX()  # Read the maximum amp setting of Channel 1

    ###### ###### á eftir að taka til fyrir neðan ###### ######

    def dischargeCC(self, amper):
        self.electronicLoadController.dischargeCC(amper)

    def dischargeCV(self, volts):
        self.electronicLoadController.dischargeCV(volts)

    def dischargeCP(self, watts):
        self.electronicLoadController.dischargeCP(watts)

    def getVoltageELC(self):
        x = self.electronicLoadController.getVoltage()
        return float(x)

    def getCurrentELC(self):
        x = self.electronicLoadController.getCurrent()
        return float(x)

    def getVoltagePSC(self):
        x = self.powerSupplyController.getVoltage()
        return float(x)

    def getCurrentPSC(self):
        x = self.powerSupplyController.getCurrent()
        return float(x)

    # def stopDischarge(self):
    #     self.electronicLoadController.stopDischarge()

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply

    # Test protocal for testing the capacity of a battery
    def capacityTest(self, chargeTime: int, waitTime: int, numCycles: int, CPar, temp: int):
        # Clear event to indicate that test is currently running
        self.event.clear()
        # Create a loop that will run one time for each element of the eather CPar or TempPar
        for cParameter in CPar:
            # Create a list that will keep track of the estemated capacity of the battery
            ampHourCapacity = []
            # Create a loop for each cycle for the cParameter
            for cycleNumber in range(int(numCycles)):
                # dataStorage object to keep track of test data
                dataStorage = DataStorage()
                # Variable to keep track of Amp second capacity
                ASeconds = 0
                # Charge with a constant voltage of self.OCVFull
                self.chargeCV(self.OCVFull)
                # Wait the desired amount of minutes
                print(f"Charging for {chargeTime} min")
                for i in range(floor(float(chargeTime) * 60)):
                    # If the test is manually stopped, break the loop
                    if self.event.is_set():
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    time.sleep(1)
                # Once the OCV has reached OCVFull we can start discharging
                self.stopCharge()
                # Wait the desired number of seconds
                print(f"Wating for {waitTime} min")
                for i in range(floor(float(waitTime) * 60)):
                    if self.event.is_set():
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    time.sleep(1)
                # Discharging at c rate current
                self.dischargeCC(self.C_rate * cParameter)

                # Creating a loop that will break once voltage has reached desired levels
                print(f"Starting discharge in cycle nr.{cycleNumber + 1} with discharge rate {cParameter}C")
                while (True):
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    # optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    if (float(v) < self.OCVEmpty):
                        break
                    time.sleep(1)
                    ASeconds += self.C_rate * cParameter
                # Stop discharging the battery
                self.electronicLoadController.stopDischarge()
                # Graph results of current test
                dataStorage.graphCapacity(cycleNumber, temp, cParameter)
                # Put results of current test in a table
                dataStorage.createTable("Capacity Test", cParameter, cycleNumber, temp, self.timeInterval, chargeTime)
                print(f"Capacity stored for cycle nr.{cycleNumber + 1} with C-rate of {cParameter}")
                # Store the amp hour capacity for the current test
                ampHourCapacity.append([ASeconds / 3600])
            print(ampHourCapacity)
        # Set the event to indicate that testing is done
        self.event.set()

    def enduranceTest(self, chargeTime: int, waitTime: int, numCycles: int, CPar, temp: int):
        self.event.clear()
        # Create a loop that will run one time for each element of the eather CPar or TempPar
        for cParameter in CPar:
            # Create a list that will keep track of the estemated capacity of the battery
            ampHourCapacity = []
            # Create a loop for each cycle for the cParameter
            for cycleNumber in range(int(numCycles)):
                # dataStorage object to keep track of tets data
                dataStorage = DataStorage()
                # Variable to keep track of Amp second capacity
                ASeconds = 0
                # Charge with a constant voltage of self.OCVFull
                self.chargeCV(self.OCVFull)
                # Wait the desired amount of minutes
                print(f"Charging for {chargeTime} min")
                for i in range(floor(float(chargeTime) * 60)):
                    # Break the loop if the testing has been manualy stopped
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    time.sleep(1)
                # Once the OCV has reached OCVFull we can start discharging
                self.stopCharge()
                # Wait the desired number of seconds
                print(f"Wating for {waitTime} min")
                for i in range(floor(float(waitTime) * 60)):
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    time.sleep(1)
                # Discharging at c rate current
                self.dischargeCC(self.C_rate * cParameter)

                # Creating a loop that will break once voltage has reached desired levels
                print(f"Starting discharge in cycle nr.{cycleNumber + 1} with discharge rate {cParameter}C")
                while (True):
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    # Optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    if (float(v) < self.OCVEmpty):
                        break
                    time.sleep(1)
                    ASeconds += self.C_rate * cParameter
                # Stop discharging battery
                self.electronicLoadController.stopDischarge()
                # Create a table from the current test data
                dataStorage.createTable("Endurance Test", cParameter, cycleNumber, temp, self.timeInterval, chargeTime)

                ampHourCapacity.append([ASeconds / 3600])
            # Create a graph from the current test data
            dataStorage.graphEndurance(temp, cParameter, ampHourCapacity)
            print(ampHourCapacity)
        # Set the event to indicate that testing is finished
        self.event.set()

    def NEWupsTest(self, Charge_Volt_start: float, Charge_volt_end: float,
                   Charge_current_max: float, Charge_power_max: float, DCharge_volt_min: float,
                   DCharge_current_max: float, Slew_volt: float, Slew_current: float,
                   LeadinTime: int, Charge_time: int, DCharge_time: int, numCycles: int, Goal_voltage: float):

        TotstartTime = datetime.now()
        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")

        #        self.powerSupplyController.setVoltage(Charge_Volt_start)
        #        print(f"Set the initial voltage to {Charge_Volt_start}")
        print("===========================")
        print(f"Charge time {Charge_time}")
        self.setVoltageLimMax((Charge_volt_end - 0.01))
        print(f"Set the final Charge voltage to {(Charge_volt_end - 0.01)}")

        self.setVoltageProt(Charge_volt_end)
        print(f"Set the Charging Over Voltage Protection to {Charge_volt_end}")

        self.setCurrentLimMax(Charge_current_max - 0.01)
        print(f"Set the max Charge Current to {Charge_current_max - 0.01}")

        self.setCurrentProt(Charge_current_max)
        print(f"Set the Over Current Protection to {Charge_current_max}")

        self.setVoltageSlew(Slew_volt)
        print(f"Set the Charging Voltage Slew rate to {Slew_volt}")

        self.setCurrentSlew(Slew_current)
        print(f"Set the Charging Current Slew rate to {Slew_current}")

        self.setPowerProt(Charge_power_max)
        print(f"Set the Charging Over Power Protection  {Charge_power_max}")
        print("===========================")

        print(f"Discharge time {DCharge_time}")
        print(f"Max Discharge Current {DCharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        Cduration = timedelta(seconds=Charge_time)  # Charge each cycle for Charge_time seconds
        Dduration = timedelta(seconds=DCharge_time)  # Discharge each cycle for DCharge_time seconds
        Lduration = timedelta(seconds=LeadinTime)  # Leadin time in seconds
        DeltaV = Charge_volt_end - Charge_Volt_start  # the amount to increase the start Volt to get to end Volt

        def testRunner(Charge_Volt_start):

            datasetup = {'testtype': [],
                         'time': [],
                         'volts': [],
                         'current': [],
                         'power': [],
                         'c_rate': [],
                         'cycle_number': [],
                         'date': []}

            DF = pd.DataFrame(datasetup)


            ## Charging/Discharging loop starts
            first_cycle = True

            for cycleNumber in range(int(numCycles)+1):

                # this is to wait for the battery recovery after loading, it is skipped if this is the initial cycle
                if first_cycle:
                    first_cycle = False
                else:
                    time.sleep(25)

                # reset the PSU initial voltage output so that it always starts from the same place
                Volt_start = Charge_Volt_start

                # dataStorage object to keep track of test data
                dataStorage = DataStorage()  # one for each cycle
                ChargestartTime = datetime.now()

                ## Discharging loop

                self.stopDischarge()
                self.setCCLmode()  # set the DC to CC low range mode

                # if (DCharge_current_max>float(self.getCCcurrentL1MAX())):
                #    self.setCCcurrentL1MAX(DCharge_current_max)
                #    print(self.getCCcurrentL1MAX())

                self.setCCcurrentL1(DCharge_current_max)  # Set the desired current of channel L1&L2
                self.startDischarge()  # turn on DC load

                # self.dischargeCC(DCharge_current_max)

                DischargestartTime = datetime.now()
                print("\n" * 15)
                print('Discharging')
                while True:
                    data = copy.deepcopy(datasetup)
                    data["testtype"] = "NEWupsTest"
                    data["cycle_number"] = int(cycleNumber)
                    secs = datetime.now() - DischargestartTime
                    secs = float(str(secs.seconds) + "." + str(secs.microseconds))
                    data["time"] = secs

                    # while Discharging do the following
                    if self.breaker:
                        return
                    time.sleep(0.1)  # Wait between measurements
                    tmp = datetime.now() - DischargestartTime
                    # v = self.getVoltage()  # read the voltage from multimeter 12061
                    v = self.getVoltageELC()  # read voltage from electronic load
                    c = self.getCurrentELC()  # read the current from electronic load

                    data["volts"] = v
                    data["current"] = c
                    data["power"] = v*c
                    data["c_rate"] = DCharge_current_max

                    data["date"] = str(datetime.today())

                    print(f"{cycleNumber} of {numCycles} -DISCHARGING- {tmp.total_seconds():03.2f} s - V:{v:.2f} C:{c:.2f}")
                    dataStorage.addTime(float(tmp.total_seconds()))
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    if (v < DCharge_volt_min):  # Breaking out if minimum voltage has been reached
                        print(f"below {DCharge_volt_min} volts")
                        break

                    DF = DF.append(data, ignore_index=True)

                self.stopDischarge()  # Inactivate the electronic load
                ## Discharging loop ends
                time.sleep(5)
                # Create a table from the measurements made in this cycle (27.0 is the temperature - now kept fixed)


                # Charging loop

                dataStorage.addTime(0)  # for finding where discharging ends and charging starts
                dataStorage.addVoltage(0)  # for finding where discharging ends and charging starts
                dataStorage.addCurrent(0)  # for finding where discharging ends and charging starts

                self.startPSOutput()
                self.setVoltage(Volt_start)
                print('Charging')

                before_voltage = 0
                before_current = 0
                while float(self.powerSupplyController.getVoltage()) < Goal_voltage:
                    if self.breaker:
                        return DF

                    data = copy.deepcopy(datasetup)
                    data["testtype"] = "NEWupsTest"
                    data["cycle_number"] = int(cycleNumber)
                    secs = datetime.now() - DischargestartTime
                    secs = float(str(secs.seconds) + "." + str(secs.microseconds))
                    data["time"] = secs


                    # while Charging do the following
                    time.sleep(self.timeInterval)  # Wait between measurements
                    tmp = datetime.now() - ChargestartTime
                    v_ps = self.getVoltagePSC()  # read the voltage from Power Supply - this is the applied voltage
                    v = self.getVoltageELC()  # read voltage from electronic load - this is the voltage of the cell
                    c = self.getCurrentPSC()  # read the current from Power Supply

                    data["volts"] = v
                    data["current"] = c
                    data["power"] = v*c
                    data["c_rate"] = DCharge_current_max

                    data["date"] = str(datetime.today())

                    loopDelta_C = c - before_current
                    loopDelta_V = v - before_voltage
                    change_string = "positive"
                    # a semi random correction, this is to prevent oscillating corrections
                    Correction = 0.05 * rand.uniform(0.75,0.1)

                    if loopDelta_C > Slew_current or c > 0.05:
                        # we're over the slew current rate or current rate so we need to step back the voltage a little bit
                        Correction *= -1
                        change_string = "negative"

                    # apply the correction
                    Volt_start += Correction

                    if Volt_start > Charge_volt_end:
                        # undo the correction so that we don't go over the limit
                        Volt_start -= Correction

                    elif c < 0.001:
                        # check for when the current is near 0
                        # should be able to go much faster, this is a catch-up check
                        Volt_start += Correction*3

                    if Volt_start < v:
                        # check for if the battery voltage is higher than the PSC output voltage
                        # at current time
                        # this can happen but only and makes the process slower
                        # should be able to go much faster
                        Volt_start = v

                    print("\n"*15)
                    print(f"--- voltage correction {change_string} --->"
                          f" max output Volt : {Charge_volt_end}, output Volt : {Volt_start:.1f}, goal Volt : {Goal_voltage}")
                    self.setVoltage(Volt_start)

                    print(
                        f"{cycleNumber} of {numCycles} -CHARGING- Voltage_PSC:{v_ps:.1f} Voltage_ELC:{v:.1f} Current:{c:.3f}")

                    print(f"Voltage delta for the iteration {loopDelta_V:.3f}")
                    print(f"Current delta for the iteration {loopDelta_C:.3f}")
                    dataStorage.addTime(float(tmp.total_seconds()))
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)

                    before_voltage = v
                    before_current = c

                    DF = DF.append(data, ignore_index=True)

                self.stopPSOutput()  # stop the output from the power supply
                print("Goal voltage reached")
                ## Charging loop ends

                # insert data to SQL database
                #dataStorage.createTable("UPS_", DCharge_current_max, cycleNumber, 27.0, self.timeInterval, str(Charge_time))

            self.breaker = True
            return DF

        class MyThread(threading.Thread):
            def __init__(self, target, args=()):
                super().__init__(target=target, args=args)
                self._result = None

            def run(self):
                if self._target is not None:
                    self._result = self._target(*self._args)

            def result(self):
                return self._result

        def check_keyboard_input():
            while True:
                if keyboard.is_pressed('left shift'):
                    print("Program stopped.")
                    self.breaker = True
                    break
                if self.breaker:
                    break

        # Create and start the threads
        thread_runner = MyThread(target=testRunner, args=(Charge_Volt_start,))
        thread_runner.start()

        # Start the keyboard input checking thread
        thread_keyboard = threading.Thread(target=check_keyboard_input)
        thread_keyboard.start()

        # Wait for the threads to finish
        thread_runner.join()
        thread_keyboard.join()
        print("Closing the charging and discharging processes")
        self.stopPSOutput()
        self.stopDischarge()
        print("-- Closure successful --")
        self.event.set()

        return thread_runner.result()

    def upsTest(self, chargeTime: int, dischargeTime: int, waitTime: int, numCycles: int, CPar, temp: int):
        startTime = time.time()
        currentMeasurement = 1.0
        self.event.clear()
        # Create a loop that will run one time for each element of the eather CPar or TempPar
        for cParameter in CPar:
            # Create a loop for each cycle for the cParameter
            for cycleNumber in range(int(numCycles)):
                # dataStorage object to keep track of test data
                dataStorage = DataStorage()
                # Charge with a constant voltage of self.OCVFull
                self.chargeCV(self.OCVFull)
                # Wait the desired amount of minutes
                print(f"Charging for {chargeTime} min")
                for i in range(floor(float(chargeTime) * 60 * (1 / self.timeInterval))):
                    nextMeasurement = startTime + (currentMeasurement - 1) * self.timeInterval - time.time()
                    if (nextMeasurement > 0.0):
                        time.sleep(nextMeasurement)
                    # Break the loop if the testing has been manually stopped
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    # Optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    currentMeasurement += 1
                    if (v > 7.2):  # 2.31
                        print("exceeded 7.2 volts")
                        break
                # Once the OCV has reached OCVFull we can start discharging
                self.stopCharge()
                # Wait the desired number of seconds
                print(f"Waiting for {waitTime} min")
                for i in range(floor(float(waitTime) * 60.0 * (1 / self.timeInterval))):
                    nextMeasurement = startTime + (currentMeasurement - 1) * self.timeInterval - time.time()
                    if (nextMeasurement > 0.0):
                        time.sleep(nextMeasurement)
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    time.sleep(1)
                # Discharging at c rate current
                self.dischargeCC(float(self.C_rate) * float(cParameter))
                # Creating a loop that will break once voltage has reached desired levels
                print(f"Starting discharge in cycle nr.{cycleNumber + 1} with discharge rate {cParameter}C")
                for i in range(floor(float(dischargeTime) * 60.0 * (1 / self.timeInterval))):
                    nextMeasurement = startTime + (currentMeasurement - 1) * self.timeInterval - time.time()
                    if (nextMeasurement > 0.0):
                        time.sleep(nextMeasurement)
                    if (self.event.is_set()):
                        print("Testing has been manually stopped")
                        self.event.clear()
                        exit()
                    # Optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    currentMeasurement += 1
                    if (v < 1.2):  # 0.4
                        print("below 1.2 volts")
                        break
                # Stop discharging battery
                self.electronicLoadController.stopDischarge()
                # Create a table from the current test data
                dataStorage.createTable("UPS Test", cParameter, cycleNumber, temp, self.timeInterval, chargeTime)
        # Set the event to indicate that testing is finished
        self.event.set()

    def PhotoVoltaicTest(self, waitTime: int, numCycles: int, CParCharge, CParDischarge, temp: int):
        startTime = time.time()
        currentMeasurement = 1.0
        self.event.clear()
        # Create a loop that will run one time for each element of the eather CPar or TempPar
        for cParameter in CParCharge:
            # Create a loop for each cycle for the cParameter
            for cycleNumber in range(int(numCycles)):
                # dataStorage object to keep track of tets data
                dataStorage = DataStorage()
                # Charge with a constant current
                self.chargeCC(float(cParameter) * float(self.C_rate))
                # Wait until the desired voltage is reached
                print(f"Charging")
                chargingStartTime = time.time()
                while (True):
                    nextMeasurement = startTime + (currentMeasurement - 1) * self.timeInterval - time.time()
                    if (nextMeasurement > 0.0):
                        time.sleep(nextMeasurement)
                    if (self.event.is_set()):
                        print("Testing has beed manually stopped")
                        self.event.clear()
                        exit()
                    # Optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    print("Volts: " + str(v), end=" ")
                    print("Amps: " + str(c) + "\n")
                    if (float(v) > self.OCVFull or float(time.time() - chargingStartTime > 36000)):
                        break
                # Once the OCV has reached OCVFull we can start discharging
                self.stopCharge()
                # Discharging at c rate current
                self.dischargeCC(float(self.C_rate) * float(CParDischarge))
                # Creating a loop that will break once voltage has reached desired levels
                print(f"Starting discharge in cycle nr.{cycleNumber + 1} with discharge rate {cParameter}C")
                while (True):
                    nextMeasurement = startTime + (currentMeasurement - 1) * self.timeInterval - time.time()
                    if (nextMeasurement > 0.0):
                        time.sleep(nextMeasurement)
                    if (self.event.is_set()):
                        print("Testing has beed manually stopped")
                        self.event.clear()
                        exit()
                    # Optain and store voltage and current
                    v = self.getVoltage()
                    c = self.getCurrent()
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                    print(self.OCVEmpty)
                    if (float(v) < self.OCVEmpty):
                        break
                # Stop discharging battery
                self.electronicLoadController.stopDischarge()
                # Create a table from the current test data
                dataStorage.createTable("Endurance Test", cParameter, cycleNumber, temp, self.timeInterval)
        # Set the event to indicate that testing is finished
        self.event.set()
