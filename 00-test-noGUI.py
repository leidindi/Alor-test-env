import datetime

from AlIonBatteryTestSoftware import TestController
import threading
import datetime as date
from sqlalchemy import create_engine
import pandas as pd
from visualizer import showTest



def main():
    Base = 10.7
    goal = 11.5
    cycles = 1
    data = []

    TObj = TestController()  # initiating a TestObject:: TObj
    TObj.event.clear()
    # set how many datapoints you want per second
    datapoints = 3
    TObj.timeInterval = 1/datapoints

    #TObj.create_battery(attribute1="vision",attribute2="Tester",attribute3="Fusion-batdtery")
    TObj.set_battery()

    """
    data = TObj.run("constantCurrentTest", Charge_Volt_start=Base, Charge_volt_end=16,
                    Charge_current_max=0.1, Charge_power_max=10,
                    DCharge_volt_min=Base, DCharge_current_max=0.1,
                    Slew_volt=0.005, Slew_current=0.005,
                    LeadinTime=5, Charge_time=10, c_rate=0.05,
                    DCharge_time=10, numCycles=cycles, Goal_voltage=goal)
    """
    """
    """
    data = TObj.run("charging", Charge_Volt_start=Base, Charge_volt_end=16,
                    Charge_current_max=0.2, Charge_power_max=10,
                    DCharge_volt_min=Base, DCharge_current_max=0.2,
                    Slew_volt=0.005, Slew_current=0.005,
                    LeadinTime=5, Charge_time=100, c_rate=0.05,
                    DCharge_time=100, numCycles=cycles, Goal_voltage=goal,Charge_routine=[["CC",30],["CV",30],["CC",30],["CV",30],["CC",30],["CV",30],["CC",30]])

    #data = TObj.getData(fromID=1600, toID=1700)

    showTest.plot(data=data)


if __name__ == "__main__":
    main()
