import datetime

from AlIonBatteryTestSoftware import TestController
import threading
import datetime as date
from sqlalchemy import create_engine
import pandas as pd

def main():
    # sjá def og niðri


    it=1
    # 5 cells in series, max 12V, max 20mA, min 2V
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.001, 0.001, 0.001, 10, 120, 30, it)
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.002, 0.001, 0.002, 10, 120, 30, it)  # 02mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.003, 0.001, 0.002, 10, 120, 30, it)  # 03mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.004, 0.001, 0.002, 10, 120, 30, it)  # 04mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.005, 0.001, 0.002, 10, 120, 30, it)  # 05mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.010, 0.001, 0.002, 10, 120, 30, it)  # 10mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.015, 0.001, 0.002, 10, 120, 30, it)  # 15mA discharge
#    time.sleep((120+30+2)*it)  # Brute force method - modify using event and event.wait()
#    print("=========================N E X T L I N E========================================")
#    TObj.runUPSTest(11.99, 12.00, 0.09, 1.2, 2.0, 0.020, 0.001, 0.002, 10, 120, 30, it)  # 20mA discharge


# 3 cells in series, max 7.2V, max 20mA, min 1.2V
#    TObj.runUPSTest(7.19, 7.20, 0.09, 0.3, 1.2, 0.001, 0.001, 0.001, 10, 100, 30, 50) # 2mA discharge
#    TObj.runUPSTest(7.19, 7.20, 0.1, 0.3, 1.2, 0.004, 0.001, 0.001, 60, 100, 30, 30) # 5mA discharge

# 12V test battery
#    def NEWupsTest(self, Charge_Volt_start: float, Charge_volt_end: float,
#                   Charge_current_max: float, Charge_power_max: float, DCharge_volt_min: float,
#                   DCharge_current_max: float, Slew_volt: float, Slew_current: float,
#                   LeadinTime: int, Charge_time: int, DCharge_time: int, numCycles: int):

    Base = 4

    TObj = TestController()  # initiating a TestObject:: TObj
    TObj.event.clear()
    data = TObj.run("NEWupsTest", Charge_Volt_start=Base, Charge_volt_end=16,
                    Charge_current_max=2.0, Charge_power_max=9.9,
                    DCharge_volt_min=Base, DCharge_current_max=0.05,
                    Slew_volt=0.005, Slew_current=0.005,
                    LeadinTime=5, Charge_time=10,
                    DCharge_time=10, numCycles=20, Goal_voltage=12)

    database = "Alor - DB"
    user = "postgres"
    password = "1234"
    port = 5432
    host = "localhost"

    # Create a database connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    # Insert the DataFrame into the database table
    try:
        data.to_sql('testdata', engine, if_exists='append', index=False)
    except:
        print("Data was not inserted into the sql server")

if __name__ == "__main__":
    main()
    ####################    ####################    ####################
    ####################    ##### UPS TEST #####    ####################
    ####################    ####################    ####################
    ##### CHARGING #####
    # Charging_Volt_start=1.2
    # Charging_Volt_end=7.2q
    # Charging_Current_max=0.4
    ##### DISCHARGING #####
    # Discharging_Volt_min= 1.2
    # Discharging_Current_max=0.4
    ##### OTHER PARAMETERS #####
    # Slew rate Volt = 0.001V/ms
    # Slew rate Current = 0.001A/ms
    # Lead in time = 60 sec
    # Charging time = 180 sec
    # Discharging time = 30 sec
    # Number of cycles: X
