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
from sqlalchemy import create_engine


# Class used to control test procedures
class TestController:
    """
        This object is a wrapper for all tests and data gathering. It automatically stores information into the Alor-DB
        and assigns it to the correct battery ID.

        Args:
                no arguments needed

        Returns:
                nothing, only sets internal functions
        """
    # Initiating function
    def __init__(self):
        """
            initializer for the test object

            Args:
                no arguments needed

            Returns:
                nothing, only sets internal variables
            """
        try:
            # Trying to connect to the real device controllers
            self.powerSupplyController = PowerSupplyController()
            print("Testcontroller succesfully connected to Power Supply")
            self.electronicLoadController = ElectronicLoadController()
            print("Testcontroller succesfully connected to Electronic Load")

            # uncomment line below if multimeter will be used
            # self.multimeterController = MultimeterController()
            # print("Testcontroller succesfully connected to Multimeter")
        except:
            # Connecting to the mock device controllers
            print("Connection not successful, using mock objects")
            self.powerSupplyController = PowerSupplyControllerMock()
            self.electronicLoadController = ElectronicLoadControllerMock()
            self.multimeterController = MultimeterControllerMock()
            print("This connection should be successful unless your hardware is incorrectly set up")
            raise ConnectionError
            # Indicates the number of seconds between each measurement
        # default waiting period between measurements
        self.timeInterval = 0.5
        # Variable for keeping track of the open circuit voltage of a full battery
        self.OCVFull = 0.0
        # Variable for keeping track of the open circuit voltage of an empty battery
        self.OCVEmpty = 0.0
        # Variable for keeping track of the C-rate of the battery
        self.C_rate = 0.0

        # Create an event to indicate if test is running
        # this is legacy code for the older tests.
        self.event = threading.Event()

        # what battery data is assigned to in the database. 0 will be the default and is a dummy battery.
        self.batteryID = 0
        # this variable is a trigger, so that different threads can know if the panic button is pressed.
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

    def dischargeCC(self, amper):
        self.electronicLoadController.dischargeCC(amper)

    def dischargeCV(self, volts):
        self.electronicLoadController.dischargeCV(volts)

    def dischargeCP(self, watts):
        self.electronicLoadController.dischargeCP(watts)

    def getVoltageELC(self):
        # returns load voltage
        x = self.electronicLoadController.getVoltage()
        return float(x)

    def getCurrentELC(self):
        # returns load current
        x = self.electronicLoadController.getCurrent()
        return float(x)

    def getVoltagePSC(self):
        # returns power supply voltage
        x = self.powerSupplyController.getVoltage()
        return float(x)

    def getCurrentPSC(self):
        # returns power supply current
        x = self.powerSupplyController.getCurrent()
        return float(x)

    # def stopDischarge(self):
    #     self.electronicLoadController.stopDischarge()

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply
    def create_battery(self, **kwargs):
        """
        A function to create new batteries in the database with some attributes.

        Args:
            'attribute1' (str),
            'attribute2' (str),
            'attribute3' (str),
            'attribute4' (str),
            'attribute5' (str),
            'date_made' (str)
            these values are expected, but they are all handled if empty ( in any configuration)
        Returns:
            does not return anything. It internally sets what battery the object assigns test data to in the database.
        """
        database = "Alor - DB"
        user = "postgres"
        password = "1234"
        port = 5432
        host = "localhost"

        # data setup for database insertions

        data = {'attribute1': [],
                'attribute2': [],
                'attribute3': [],
                'attribute4': [],
                'attribute5': [],
                'date_made': []}

        # handling of empty variables
        try:
            data["attribute1"].append(kwargs['attribute1'])
        except:
            print('You need to have at least the first attribute')
            raise ValueError

        try:
            data["attribute2"].append(kwargs['attribute2'])
        except:
            data["attribute2"].append("")

        try:
            data["attribute3"].append(kwargs['attribute3'])
        except:
            data["attribute3"].append("")

        try:
            data["attribute4"].append(kwargs['attribute4'])
        except:
            data["attribute4"].append("")

        try:
            data["attribute5"].append(kwargs['attribute5'])
        except:
            data["attribute5"].append("")

        try:
            data["date_made"].append(kwargs["date_made"])
        except:
            data["date_made"].append(str(datetime.today()))


        # turn the data into dataframes
        DF = pd.DataFrame(data)

        # INSERT INTO public.battery_table(
        # battery_id, attribute1, attribute2, attribute3, attribute4, attribute5, date_made)
        # VALUES (?, ?, ?, ?, ?, ?, ?);

        # Create a database connection
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

        # Insert the DataFrame into the database table
        try:
            DF.to_sql('battery_table', engine, if_exists='append', index=False)
        except:
            print("Data was not inserted into the sql server")

        # close the connection to the database
        engine.dispose()

    def set_battery(self, **kwargs):
        """
        A function to assign already existing batteries, if 'batteryID' is not provided then the user is prompted on the
        available batteries that fulfill the criteria provided by the user.

        Args:
            'attribute1' (str),
            'attribute2' (str),
            'attribute3' (str),
            'attribute4' (str),
            'attribute5' (str),
            'date_made' (str)
            these values are expected to identify batteries, but they are all handled if empty ( in any configuration).

            If a certain battery ID is given using the variable name 'batteryID' then that id will be assigned and the
            prompts will not execute.
        Returns:

        Returns:
            does not return anything. It internally sets what battery the object assigns test data to in the database.
        """
        database = "Alor - DB"
        user = "postgres"
        password = "1234"
        port = 5432
        host = "localhost"
        try:
            # if the ID is provided then it is used.
            self.batteryID = kwargs['batteryID']
            return
        except:
            pass

        # handling of empty variables
        try:
            attribute1 = '\''+ kwargs['attribute1'] + '\''
        except:
            attribute1 = 'NULL'

        try:
            attribute2 = '\''+ kwargs['attribute2'] + '\''
        except:
            attribute2 = 'NULL'

        try:
            attribute3 = '\''+ kwargs['attribute3'] + '\''
        except:
            attribute3 = 'NULL'

        try:
            attribute4 = '\''+ kwargs['attribute4'] + '\''
        except:
            attribute4 = 'NULL'

        try:
            attribute5 = '\''+ kwargs['attribute5'] + '\''
        except:
            attribute5 = 'NULL'

        try:
            date_made ='\''+  kwargs["date_made"]  + '\''
        except:
            date_made = 'NULL'

        # database connection established
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

        # selecting all the batteries that fulfill the description provided by the user
        query = f'SELECT battery_id, date_made, attribute1, attribute2, attribute3, attribute4, attribute5 ' \
                f'FROM public.battery_table ' \
                f'where attribute1 = COALESCE({attribute1}, attribute1)  ' \
                f'and attribute2 = COALESCE({attribute2}, attribute2) ' \
                f'and attribute3 = COALESCE({attribute3}, attribute3)' \
                f'and attribute4 = COALESCE({attribute4}, attribute4)' \
                f'and attribute5 = COALESCE({attribute5}, attribute5)' \
                f'and date_made = COALESCE({date_made}, date_made)  '
        # get the result
        result = engine.execute(query)

        # reformat the result
        result = result.all()
        if len(result) == 0:
            print("There were no batteries compatible with your criteria, try again")
            print("Program ending")
            quit()
        elif len(result) == 1:
            # the first result
            row = result[0]
            print('Only one battery is compatible with your criteria, it will be automatically assigned to the test object')
            print(f'The ID: {row[0]}, the date: {str(row[1])}, the attributes: {row[2]}-{row[3]}-{row[4]}-{row[5]}-{row[6]}')
            # the first element of the first result is used.
            self.batteryID = int(row[0])
        else:
            # many results found
            print("These are the batteries that are compatible with your criteria:")
            id_list = []
            for row in result:
                # all id elements gathered in a list
                id_list.append(row[0])

                print(f'The ID: {row[0]}, the date: {str(row[1])}, the attributes: {row[2]}-{row[3]}-{row[4]}-{row[5]}-{row[6]}')
            while True:
                print("which battery would you like to choose? (q to quit)")
                battery_id_input = input()

                if battery_id_input == 'q':
                    print("Quitting the program, you can't perform tests without assigning them to a battery")
                    quit()
                elif int(battery_id_input) in id_list:
                    self.batteryID = int(battery_id_input)
                    print("Battery successfully assigned to the test object")
                    break
                else:
                    print("Incorrect battery id input, try again with a valid one from the following list:")
                    print(id_list)
        # close the connection
        engine.dispose()


    def run(self, testType, **kwargs):
        """
        This function operates the threads that run the killswitch and the ongoing test. It runs the threads in parallel
        and listens to the user input.

        Args:
            arguments needed depend on the test type being ran, this function is flexible.
            These arguments are the minimum needed.

            "DCharge_current_max" (str),
            "Charge_power_max" (str),
            "Slew_current" (str),
            "Slew_volt" (str),
            "Charge_current_max" (str),
            "Charge_volt_end" (str),
            "keep_data" (bool)

        Returns:
            dictionary:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
        """
        DCharge_current_max = kwargs["DCharge_current_max"]
        Charge_power_max = kwargs["Charge_power_max"]
        Slew_current = kwargs["Slew_current"]
        Slew_volt = kwargs["Slew_volt"]
        Charge_current_max = kwargs["Charge_current_max"]
        Charge_volt_end = kwargs["Charge_volt_end"]
        keep_data = kwargs["keep_data"]

        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")
        print("===========================")
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

        print(f"Max Discharge Current {DCharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        # a switch to select what function to run
        if testType == "capacityTest":
            testRunner = self.capacityTest
        elif testType == "enduranceTest":
            testRunner = self.enduranceTest
        elif testType == "PhotoVoltaicTest":
            testRunner = self.PhotoVoltaicTest
        elif testType == "charging":
            testRunner = self.charging
        elif testType == "constantCurrentTest":
            testRunner = self.constantCurrentTest
        elif testType == "constantVoltageTest":
            testRunner = self.constantVoltageTest
        elif testType == "CC":
            testRunner = self.CC
        elif testType == "CV":
            testRunner = self.CV
        else:
            print("The testType chosen is not recognized")
            raise ValueError

        class runnerThread(threading.Thread):
            # class that inherits from the threading.Thread class, but adds a return functionality for our purposes
            def __init__(self, target, args=(), kwargs={}):
                # pass on the arguments
                super().__init__(target=target, args=args)
                self._kwargs = kwargs
                self._result = None

            def run(self):
                # check if bogus target
                if self._target is not None:
                    self._result = self._target(**self._kwargs)

            def result(self):
                # crucial line for passing on the test results from the thread when terminated
                return self._result

        def check_keyboard_input():
            while True:
                # constantly checking if the specific key is pressed
                trigger_key = 'left shift'
                if keyboard.is_pressed(trigger_key):
                    print("Program stopped.")
                    self.breaker = True
                    break
                if self.breaker:
                    # if killswitch was activated elsewere, terminate this thread
                    break

        # run the test
        thread_runner = runnerThread(target=testRunner, args=(), kwargs=kwargs)
        thread_runner.start()

        # Start the keyboard input checking thread
        thread_keyboard = threading.Thread(target=check_keyboard_input)
        thread_keyboard.start()

        # Wait for the threads to finish
        thread_runner.join()
        thread_keyboard.join()

        print("Closing the testing processes")
        self.stopPSOutput()
        self.stopDischarge()
        print("-- Closure successful --")

        # store the data
        data = thread_runner.result()

        # if user does not want to keep, only return the data
        if not keep_data:
            return data

        database = "Alor - DB"
        user = "postgres"
        password = "1234"
        port = 5432
        host = "localhost"

        # Create a database connection
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

        # handle the database serialization ourselves

        query = f"SELECT MAX(data_id) FROM public.data_table"
        query_result = engine.execute(query)

        # get the result
        first_item = query_result.one()
        # get the first element of the first result
        result = first_item[0]

        # make the next data_id be one higher than the previous highest datapoint
        data['data_id'] = result + 1
        step = 0
        for row in data['data_id']:
            # incrementally add 1 for each datapoint that will be added to the database
            data.loc[step, ('data_id')] = row + step

            # slower way of doing this, but simpler
            #data['data_id'][step] = row + step

            step += 1

        test = data[['data_id']].copy()
        test['battery_id'] = self.batteryID
        try:
            # we are appending to the test_table, after the highest test_id value
            query = f"SELECT MAX(test_id) FROM public.test_table"
            query_result = engine.execute(query)
            first_item = query_result.one()
            result = first_item[0]

            if result is None:
                # check for inconsistency in the data insertion process, this should not occur.
                raise TypeError
        except:
            # if database is empty
            result = 0
        test['test_id'] = result + 1

        # Insert the DataFrame into the database table
        try:
            data.to_sql('data_table', engine, if_exists='append', index=False)
            test.to_sql('test_table', engine, if_exists='append', index=False)
        except:
            print("Data was not inserted into the sql server")

        engine.dispose()

        return data

    def constantCurrentTest(self, **kwargs):
        """
        Charging to reach a certain voltage at a predetermined current
        This is particularly useful because there is no time limit, the hardware
        charges the batteries until the goal is reached, however long that takes.

        Args:
            Charge_Volt_start (float),
            Charge_volt_end (float),
            DCharge_volt_min (float),
            DCharge_current_max (float),
            Slew_current (float),
            numCycles (int),
            Goal_voltage (float),
            c_rate (float),
        Returns:
            dataframe:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
            pd.DataFrame(data)
        """

        Charge_Volt_start = kwargs["Charge_Volt_start"]
        Charge_volt_end = kwargs["Charge_volt_end"]
        DCharge_volt_min = kwargs["DCharge_volt_min"]
        DCharge_current_max = kwargs["DCharge_current_max"]
        Slew_current = kwargs["Slew_current"]
        numCycles = kwargs["numCycles"]
        Goal_voltage = kwargs["Goal_voltage"]
        c_rate = kwargs["c_rate"]

        datasetup = {'testtype': [],
                     'time': [],
                     'volts': [],
                     'current': [],
                     'power': [],
                     'c_rate': [],
                     'cycle_number': [],
                     'date': []}
        DF = pd.DataFrame(datasetup)
        testtype = "constantCurrentTest"

        ## Charging/Discharging loop starts

        for cycleNumber in range(1, int(numCycles) + 1):

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
                data["testtype"].append(testtype)
                data["cycle_number"].append(int(cycleNumber))
                secs = datetime.now() - DischargestartTime
                secs = float(f"{secs.seconds}.{str(secs.microseconds)[:2]}")
                data["time"].append(secs)

                # while Discharging do the following
                if self.breaker:
                    return DF
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now() - DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load

                data["volts"].append(v)
                data["current"].append(c * -1)
                data["power"].append(v * c)
                data["c_rate"].append(c_rate)

                data["date"].append(str(datetime.today()))

                print(f"{cycleNumber} of {numCycles} -DISCHARGING- {tmp.total_seconds():03.2f} s - V:{v:.2f} C:{c:.2f}")
                dataStorage.addTime(float(tmp.total_seconds()))
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if (v < DCharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {DCharge_volt_min} volts")
                    break

                new_df = pd.DataFrame(data)

                DF = pd.concat([DF, new_df], ignore_index=True)

            self.stopDischarge()  # Inactivate the electronic load

            ## Discharging loop ends

            self.startPSOutput()
            self.setVoltage(Volt_start)
            print('Charging')

            before_voltage = 0
            before_current = 0
            while float(self.getVoltageELC()) < Goal_voltage:
                if self.breaker:
                    return DF

                data = copy.deepcopy(datasetup)
                data["testtype"].append(testtype)
                data["cycle_number"].append(int(cycleNumber))
                secs = datetime.now() - DischargestartTime
                secs = float(str(secs.seconds) + "." + str(secs.microseconds))
                data["time"].append(secs)

                # while Charging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now() - ChargestartTime
                v_ps = self.getVoltagePSC()  # read the voltage from Power Supply - this is the applied voltage
                v = self.getVoltageELC()  # read voltage from electronic load - this is the voltage of the cell
                c = self.getCurrentPSC()  # read the current from Power Supply

                data["volts"].append(v)
                data["current"].append(c)
                data["power"].append(v * c)
                data["c_rate"].append(c_rate)

                data["date"].append(str(datetime.today()))

                loopDelta_C = c - before_current
                loopDelta_V = v - before_voltage
                change_string = "positive"

                # a semi random correction, this is to prevent oscillating corrections
                # this can be tuned further
                lower_bound = 0.015
                upper_bound = 0.03
                Correction = rand.uniform(lower_bound, upper_bound)

                if loopDelta_C > Slew_current or c > c_rate:
                    # we're over the slew current rate or current rate so we need to step back the voltage a little bit
                    Correction *= -1
                    change_string = "negative"

                # apply the correction
                Volt_start += Correction

                if Volt_start > Charge_volt_end:
                    # undo the correction so that we don't go over the limit
                    Volt_start -= Correction

                elif c < 0.01:
                    # check for when the current is near 0
                    # should be able to go much faster, this is a catch-up check
                    Volt_start += Correction * 5

                if Volt_start < v:
                    # check for if the battery voltage is higher than the PSC output voltage
                    # at current time
                    # this can happen but only and makes the process slower
                    # should be able to go much faster
                    Volt_start = v

                print("\n" * 15)
                print(f"--- voltage correction {change_string} --->"
                      f" max output Volt : {Charge_volt_end}, output Volt : {Volt_start:.1f}, goal Volt : {Goal_voltage}")
                self.setVoltage(Volt_start)

                print(
                    f"{cycleNumber} of {numCycles} -CHARGING- Voltage_PSC:{v_ps:.1f} Voltage_ELC:{v:.2f} Current:{c:.3f}")

                print(f"Voltage delta for the iteration {loopDelta_V:.3f}")
                print(f"Current delta for the iteration {loopDelta_C:.3f}")

                before_voltage = v
                before_current = c

                new_df = pd.DataFrame(data)

                DF = pd.concat([DF, new_df], ignore_index=True)

            print("Goal voltage reached")
            # how long you want to charge the cell at the final voltage
            charging_duration = 0

            # stop the output from the power supply, when done charging
            self.stopPSOutput()
            ## Charging loop ends
        self.breaker = True
        return DF

    def constantVoltageTest(self, chargeTime: int, dischargeTime: int, waitTime: int, numCycles: int, CPar, temp: int,
                            **kwargs):
        """ legacy code, not used currently. but not nececcary to delete """
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
    def PhotoVoltaicTest(self, waitTime: int, numCycles: int, CParCharge, CParDischarge, temp: int, **kwargs):
        """ legacy code, not used currently. but not nececcary to delete """
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
                        print("Testing has been manually stopped")
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
    # Test protocal for testing the capacity of a battery
    def capacityTest(self, chargeTime: int, waitTime: int, numCycles: int, CPar, temp: int):
        """ legacy code, not used currently. but not nececcary to delete """
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
        """ legacy code, not used currently. but not nececcary to delete """
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
                    time.sleep(0.01)
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

    def CC(self, **kwargs):
        """
        A function to greet a person by name.

        Args:
            name (str): The name of the person to greet.

        Returns:
            dictionary:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
        """
        Charge_Volt_start = kwargs["Charge_Volt_start"]
        numCycles = kwargs["numCycles"]
        c_rate = kwargs["c_rate"]
        Slew_current = kwargs["Slew_current"]
        Charge_volt_end = kwargs["Charge_volt_end"]
        testtype = kwargs["testtype"]
        cycleNumber = kwargs["cycleNumber"]
        duration = kwargs["duration"]
        Goal_voltage = kwargs["Goal_voltage"]
        try:
            following = kwargs["following"]
        except:
            following = False
        previous_run_time = 0
        try:
            data = kwargs["data"]
            # if the previous part of the charging process was also charging then we want to
            # count the time from where the last charging section ended
            if testtype == data["testtype"][-1]:
                previous_run_time = data["time"][-1]

                if following:
                    Charge_Volt_start = data["volts"][-1] + (12.0860 - 11.2660)
        except:
            data = {'testtype': [],
                    'time': [],
                    'volts': [],
                    'current': [],
                    'power': [],
                    'c_rate': [],
                    'cycle_number': [],
                    'date': []}





        ChargestartTime = datetime.now()
        Cend_time = ChargestartTime + duration

        testtype = "charging"
        ChargestartTime = datetime.now()
        self.setCurrent(c_rate)

        Volt_start = Charge_Volt_start

        before_current = 0

        while (datetime.now() < Cend_time):

            if self.breaker:
                return data

            data["testtype"].append(testtype)
            data["cycle_number"].append(int(cycleNumber))
            secs = datetime.now() - ChargestartTime
            secs = float(str(secs.seconds) + "." + str(secs.microseconds))
            data["time"].append(secs+previous_run_time)

            # while Charging do the following
            tmp = datetime.now() - ChargestartTime

            v_ps = self.getVoltagePSC()  # read the voltage from Power Supply - this is the applied voltage
            v = self.getVoltageELC()  # read voltage from electronic load - this is the voltage of the cell
            c = self.getCurrentPSC()  # read the current from Power Supply

            loopDelta_C = c - before_current
            Correction = 0.03 * rand.uniform(0.1, 0.75)

            if loopDelta_C > Slew_current or c > c_rate:
                # we're over the slew current rate or current rate so we need to step back the voltage a little bit
                Correction *= -1

            # apply the correction
            Volt_start += Correction

            if Volt_start > Charge_volt_end:
                # undo the correction so that we don't go over the limit
                Volt_start -= Correction

            elif c < 0.01:
                # check for when the current is near 0
                # should be able to go much faster, this is a catch-up check
                Volt_start += Correction * 2

            if Volt_start < v:
                # check for if the battery voltage is higher than the PSC output voltage
                # at current time
                # this can happen but only and makes the process slower
                # should be able to go much faster
                Volt_start = v

            data["volts"].append(v)
            data["current"].append(c)
            data["power"].append(v * c)
            data["c_rate"].append(c_rate)

            data["date"].append(str(datetime.today()))
            print(f"{cycleNumber} of {numCycles} - CC CHARGING- ",end="")
            print(f"{tmp.total_seconds()+previous_run_time:03.2f}",end="")
            print(f" s of {duration.total_seconds()+previous_run_time:.1f} s - ",end="")
            print(f"V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}, diff of V:{v_ps-v:.4f}")
            self.setVoltage(Volt_start)
            time.sleep(self.timeInterval)

            before_current = c
        return data

    def CV(self, **kwargs):
        """
        A function to greet a person by name.

        Args:
            name (str): The name of the person to greet.

        Returns:
            dictionary:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
        """
        numCycles = kwargs["numCycles"]
        c_rate = kwargs["c_rate"]
        Charge_volt_end = kwargs["Charge_volt_end"]
        testtype = kwargs["testtype"]
        cycleNumber = kwargs["cycleNumber"]
        duration = kwargs["duration"]
        Goal_voltage = kwargs["Goal_voltage"]

        try:
            following = kwargs["following"]
        except:
            following = False

        previous_run_time = 0
        try:
            data = kwargs["data"]
            # if the previous part of the charging process was also charging then we want to
            # count the time from where the last charging section ended
            if testtype == data["testtype"][-1]:
                previous_run_time = data["time"][-1]
                if following:
                    Goal_voltage = data["volts"][-1] + (12.0860-11.2660)
        except:
            data = {'testtype': [],
                         'time': [],
                         'volts': [],
                         'current': [],
                         'power': [],
                         'c_rate': [],
                         'cycle_number': [],
                         'date': []}

        ChargestartTime = datetime.now()
        Cend_time = ChargestartTime + duration



        self.setVoltage(Goal_voltage)

        while (datetime.now() < Cend_time):

            if self.breaker:
                return data

            data["testtype"].append(testtype)
            data["cycle_number"].append(int(cycleNumber))
            secs = datetime.now() - ChargestartTime
            secs = float(str(secs.seconds) + "." + str(secs.microseconds))
            data["time"].append(secs+previous_run_time)
            data["date"].append(str(datetime.today()))

            # while Charging do the following
            tmp = datetime.now() - ChargestartTime

            v_ps = self.getVoltagePSC()  # read the voltage from Power Supply - this is the applied voltage
            v = self.getVoltageELC()  # read voltage from electronic load - this is the voltage of the cell
            c = self.getCurrentPSC()  # read the current from Power Supply

            print(f"{cycleNumber} of {numCycles} - CV CHARGING- ", end="")
            print(f"{tmp.total_seconds()+previous_run_time:03.2f}", end="")
            print(f" s of {duration.total_seconds()+previous_run_time:.1f} s - ", end="")
            print(f"V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}")

            data["volts"].append(v)
            data["current"].append(c)
            data["power"].append(v * c)
            data["c_rate"].append(c_rate)
            time.sleep(self.timeInterval)
        return data

    def charging(self, **kwargs):
        """
        A function to greet a person by name.

        Args:
            name (str): The name of the person to greet.

        Returns:
            dataframe:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
            pd.DataFrame(data)
        """
        Charge_Volt_start = kwargs["Charge_Volt_start"]
        numCycles = kwargs["numCycles"]
        c_rate = kwargs["c_rate"]
        Charge_time = kwargs["Charge_time"]
        DCharge_time = kwargs["DCharge_time"]
        DCharge_current_max = kwargs["DCharge_current_max"]
        Charge_power_max = kwargs["Charge_power_max"]
        Slew_current = kwargs["Slew_current"]
        Slew_volt = kwargs["Slew_volt"]
        Charge_current_max = kwargs["Charge_current_max"]
        Charge_volt_end = kwargs["Charge_volt_end"]
        try:
            Charge_routine = kwargs["Charge_routine"]
        except:
            Charge_routine = False
            print("There was no routine specified, the default charging method is constant current charging")

        datasetup = {'testtype': [],
                     'time': [],
                     'volts': [],
                     'current': [],
                     'power': [],
                     'c_rate': [],
                     'cycle_number': [],
                     'date': []}
        DF = pd.DataFrame(datasetup)

        Cduration = timedelta(seconds=Charge_time)  # Charge each cycle for Charge_time seconds
        Dduration = timedelta(seconds=DCharge_time)  # Discharge each cycle for DCharge_time seconds

        ## Charging/Discharging loop starts
        for cycleNumber in range(1, int(numCycles) + 1):

            Dend_time = datetime.now() + Dduration  # set the time when to stop Discharging
            ## Discharging loop

            self.stopDischarge()
            self.setCCLmode()  # set the DC to CC low range mode

            self.setCCcurrentL1(c_rate)  # Set the desired current of channel L1&L2
            self.startDischarge()  # turn on DC load

            print('Discharging')
            testtype = "discharging"
            DischargestartTime = datetime.now()
            while (datetime.now() < Dend_time):
                if self.breaker:
                    return DF

                data = copy.deepcopy(datasetup)
                data["testtype"].append(testtype)
                data["cycle_number"].append(int(cycleNumber))
                secs = datetime.now() - DischargestartTime
                secs = float(str(secs.seconds) + "." + str(secs.microseconds))
                data["time"].append(secs)

                # while Discharging do the following
                time.sleep(0.01)  # Wait between measurements
                tmp = datetime.now() - DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load
                print(
                    f"{cycleNumber} of {numCycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}")

                data["volts"].append(v)
                data["current"].append(c * -1)
                data["power"].append(v * c)
                data["c_rate"].append(DCharge_current_max)

                data["date"].append(str(datetime.today()))

                new_df = pd.DataFrame(data)

                DF = pd.concat([DF, new_df], ignore_index=True)
                time.sleep(self.timeInterval)
            self.stopDischarge()

            # Charging loop
            self.startPSOutput()
            self.setVoltage(Charge_Volt_start)
            print('Charging')

            testtype = "charging"

            if Charge_routine == False:
                data = self.CC(duration=Cduration, cycleNumber=cycleNumber, data=data, testtype=testtype, **kwargs)
            else:
                for command in Charge_routine:

                    commandType = command[0]
                    duration = timedelta(seconds=command[1])

                    if commandType == "CC":
                        data = self.CC(duration=duration, cycleNumber=cycleNumber, data=data, testtype=testtype, following = True, **kwargs)
                    elif commandType == "CV":
                        data = self.CV(duration=duration, cycleNumber=cycleNumber, data=data, testtype=testtype, following = True, **kwargs)
                    else:
                        print("Faulty routine provided")
                        raise ValueError
            new_df = pd.DataFrame(data)

            DF = pd.concat([DF, new_df], ignore_index=True)

            self.stopPSOutput()  # stop the output from the power supply
        # self.event.set()
        self.breaker = True
        return DF

    def getData(self, fromID=None, toID=None):
        """
        A function to greet a person by name.

        Args:
            name (str): The name of the person to greet.

        Returns:
            dataframe:
            with the following structure
            data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}
            pd.DataFrame(data)
        """
        if fromID is None or toID is None or toID < fromID:
            print("You need to correctly identify the data you're trying to retrieve'")
            print(f'the following are not valid, fromID:{fromID}, toID{toID}')
            raise ValueError

        from sqlalchemy import create_engine

        data = {'testtype': [],
                'data_id': [],
                'time': [],
                'volts': [],
                'current': [],
                'power': [],
                'c_rate': [],
                'cycle_number': [],
                'date': []}

        database = "Alor - DB"
        user = "postgres"
        password = "1234"
        port = 5432
        host = "localhost"

        # Create a database connection
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

        # Execute the SQL query and retrieve data
        query = f"SELECT testtype, time, volts, current, power, c_rate, cycle_number, date FROM public.testdata where id >= {fromID} and id <= {toID}"
        result = engine.execute(query)

        # Populate the datasetup dictionary with the retrieved data
        for row in result:
            data['data_id'].append(row['data_id'])
            data['testtype'].append(row['testtype'])
            data['time'].append(row['time'])
            data['volts'].append(row['volts'])
            data['current'].append(row['current'])
            data['power'].append(row['power'])
            data['c_rate'].append(row['c_rate'])
            data['cycle_number'].append(row['cycle_number'])
            data['date'].append(row['date'])

        engine.dispose()
        return pd.DataFrame(data)
