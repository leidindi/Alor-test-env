from AlIonBatteryTestSoftware import TestController
class TestTypes:
    def __init__(self):
        self.testController = TestController()

    def runUPSTest(self, Charge_Volt_start: float, Charge_volt_end: float,
                   Charge_current_max: float, Charge_power_max: float, DCharge_volt_min: float,
                   DCharge_current_max: float, Slew_volt: float, Slew_current: float,
                   LeadinTime: int, Charge_time: int, DCharge_time: int, numCycles: int):
        import threading
        self.testController.event.clear()
        self.upsThread = threading.Thread(target=self.testController.NEWupsTest,
                                          args=(Charge_Volt_start, Charge_volt_end,
                                                Charge_current_max, Charge_power_max,
                                                DCharge_volt_min, DCharge_current_max,
                                                Slew_volt, Slew_current,
                                                LeadinTime, Charge_time,
                                                DCharge_time, numCycles))
        self.upsThread.start()

def main():
    # sjá def og niðri
    TObj = TestTypes()  # initiating a TestObject:: TObj
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
    TObj.runUPSTest(13.0, 13.1, 2.0, 9.9, 11.0, 0.02, 0.001, 0.001, 10, 20, 22, 2)

if __name__ == "__main__":
    main()
    ####################    ####################    ####################
    ####################    ##### UPS TEST #####    ####################
    ####################    ####################    ####################
    ##### CHARGING #####
    # Charging_Volt_start=1.2
    # Charging_Volt_end=7.2
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
