import openpyxl
from openpyxl.chart import ScatterChart,Reference, Series
import datetime
from math import floor
import time
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import threading
import os
import pandas as pd
import tabulate
import math

class DataStorage:

    def __init__(self) -> None:
        # Empty arrays for data
        self.time = []
        self.volts = []
        self.current = []
        self.power = []


    # Function to add time value
    def addTime(self, Mtime_sec : float):
        self.time.append(float('{:.4f}'.format(Mtime_sec)))

    # Function to add voltage value
    def addVoltage(self, votls : float):
        self.volts.append(float('{:.4f}'.format(votls)))

    # Function to add current value
    def addCurrent(self, ampers : float):
        self.current.append(float('{:.4f}'.format(ampers)))

    # Function for creating a table
    def createTable(self, testName, c_rate : float, cycleNr : int, temperature : float, timeInterval : float, chargeTime = 0):
        # Get the number of measurements
        length = len(self.volts)
        # Fill in power list with voltage and current values
        for i in range(length):
            self.power.append(self.volts[i] * self.current[i])
        # Create a 2 dimensional list for the data
        data = [[]]
        # Fill the list with the results
        for j in range(len(self.volts)):
            d = [float(j) * timeInterval, self.time[j], self.volts[j], self.current[j], self.power[j]]
            data.append(d)
        head = ["Time in seconds", "time", "Volts", "Current", "Power"]
        # Store the table in a text file
        today = date.today() 
        # try:
        # Find the absolute path to the current file
        abs = os.path.abspath("").replace("\\", "/")
        # Use the absolute path to create a path to the Data folder
        # filePath = f"{abs}/Data/{testName} for {c_rate}C nr. {cycleNr + 1} at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S"))
        # Tímabundin breyting fyrir Dropbox
        filePath = f"C:/Users/runson/Dropbox/Sharing/Alor test/{testName}_{c_rate}C_no_{cycleNr + 1}_" + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S"))
 #       filePath = f"C:/Users/runson/Dropbox/Sharing/Alor test/{testName} for {c_rate}C nr. {cycleNr + 1} at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S"))
        # Display the Path for debug purposes
        print(abs)
        # Export to text file
        self.exportTXTFile(filePath, data, head)
        # Export to CSV file
        self.exportCSVFile(filePath, data, head) 
        # Export to XLSX file
        print(filePath)
        print("filePath just now")
        self.exportXLSXFile(filePath, chargeTime, timeInterval)
        print("export xlsx file just now")
        print(f"Chargetime is {chargeTime}")
        # except:
            # print("Data storage failed, check file path")
        # Empty the result values
        self.time = []
        self.volts = []
        self.current = []
        self.power = []

    def exportTXTFile(self, filePath , data, head):
        table = tabulate.tabulate(data, headers=head, tablefmt="simple")
        with open(filePath + ".txt", "w") as f:
                f.write(str(table))

    def exportCSVFile(self, filePath, data, head):
        df = pd.DataFrame(data, columns=head)
        df.to_csv(filePath + ".csv", index=False)

    def exportXLSXFile(self, filePath, chargeTime ,timeInterval):
        # Read in our csv file
        csvDataframe = pd.read_csv(filePath + ".csv")
        # Create our exel file
        xlsxDataframe = pd.ExcelWriter(filePath + ".xlsx")
        # Write from csv to exel
        csvDataframe.to_excel(xlsxDataframe, index=False)
        # Save our exel file
        xlsxDataframe.save()

        # Open up our exel file as a work book
        wb = openpyxl.load_workbook(xlsxDataframe)
        # Access the sheet
        sheet = wb.active

        if (chargeTime == 0):  # Only if chargetime is zero
            # Create a list of Values to graph  
            seconds = Reference(sheet, min_col = 2, min_row = 3, max_col = 2, max_row = len(csvDataframe))
            voltage = Reference(sheet, min_col = 3, min_row = 3, max_col = 3, max_row = len(csvDataframe))
            current = Reference(sheet, min_col = 4, min_row = 3, max_col = 4, max_row = len(csvDataframe))
            power   = Reference(sheet, min_col = 5, min_row = 3, max_col = 5, max_row = len(csvDataframe))

            # Create a graph for the Voltage
            voltageChart = ScatterChart()
            voltageSeries = Series(voltage, seconds, title_from_data=True)
            voltageChart.series.append(voltageSeries)
            voltageChart.title = "Voltage over Time"
            voltageChart.x_axis.title = "Time [s]"
            voltageChart.x_axis.title = "Voltage [V]"

            # Create a graph for the Current
            currentChart = ScatterChart()
            currentSeries = Series(current, seconds, title_from_data=True)
            currentChart.series.append(currentSeries)
            currentChart.title = "Current over Time"
            currentChart.x_axis.title = "Time [s]"
            currentChart.x_axis.title = "Current [mA]"

            # Create a graph for the Power
            powerChart = ScatterChart()
            powerSeries = Series(power, seconds, title_from_data=True)
            powerChart.series.append(powerSeries)
            powerChart.title = "Power over Time"
            powerChart.x_axis.title = "Time [s]"
            powerChart.x_axis.title = "Power [W]"

            # Add our graphs to the sheet
            sheet.add_chart(voltageChart, "E2")
            sheet.add_chart(currentChart, "E22")
            sheet.add_chart(powerChart, "E42")
        else:  # This is used normally
            # Create a list of Values to graph
            seconds = Reference(sheet, min_col = 2, min_row = 3, max_col = 2, max_row = len(csvDataframe))
            print(f"Charge time: {chargeTime}")
            print(f"Time interval:  {timeInterval}")
            voltageCharging = Reference(sheet, min_col = 3, min_row = 3, max_col = 3, max_row = int((float(chargeTime) * 60) / float(timeInterval)))
            currentCharging = Reference(sheet, min_col = 4, min_row = 3, max_col = 4, max_row = int((float(chargeTime) * 60) / float(timeInterval)))
            powerCharging   = Reference(sheet, min_col = 5, min_row = 3, max_col = 5, max_row = int((float(chargeTime) * 60) / float(timeInterval)))

            voltageDischarging = Reference(sheet, min_col = 3, min_row = int((float(chargeTime) * 60) / float(timeInterval) + 1), max_col = 3, max_row = len(csvDataframe))
            currentDischarging = Reference(sheet, min_col = 4, min_row = int((float(chargeTime) * 60) / float(timeInterval) + 1) , max_col = 4, max_row = len(csvDataframe))
            powerDischarging = Reference(sheet, min_col = 5, min_row = int((float(chargeTime) * 60) / float(timeInterval) + 1) , max_col = 5, max_row = len(csvDataframe))

            # Create a graph for the Voltage during Charging
            voltageChartCharging = ScatterChart()
            voltageChartCharging.legend = None
            voltageSeriesCharging = Series(voltageCharging, seconds, title_from_data=False)
            voltageChartCharging.series.append(voltageSeriesCharging)
            voltageChartCharging.title = "Voltage during charging (" + chargeTime + " s)"
            voltageChartCharging.x_axis.tickLblPos = "low"
            voltageChartCharging.x_axis.title = "Time [s]"
            voltageChartCharging.y_axis.title = "Voltage [V]"

            # Create a graph for the Current during Charging
            currentChartCharging = ScatterChart()
            currentChartCharging.legend = None
            currentSeriesCharging = Series(currentCharging, seconds, title_from_data=False)
            currentChartCharging.series.append(currentSeriesCharging)
            currentChartCharging.title = "Current during charging (" + chargeTime + " s)"
            currentChartCharging.x_axis.tickLblPos = "low"
            currentChartCharging.x_axis.title = "Time [s]"
            currentChartCharging.y_axis.title = "Current [mA]"

            # Create a graph for the Power during Charging
            powerChartCharging = ScatterChart()
            powerChartCharging.legend = None
            powerSeriesCharging = Series(powerCharging, seconds, title_from_data=False)
            powerChartCharging.series.append(powerSeriesCharging)
            powerChartCharging.title = "Power during charging (" + chargeTime + " s)"
            powerChartCharging.x_axis.tickLblPos = "low"
            powerChartCharging.x_axis.title = "Time [s]"
            powerChartCharging.y_axis.title = "Power [W]"

            # Create a graph for the Voltage during Disharging
            voltageChartDischarging = ScatterChart()
            voltageChartDischarging.legend = None
            voltageSeriesDischarging = Series(voltageDischarging, seconds, title_from_data=False)
            voltageChartDischarging.series.append(voltageSeriesDischarging)
            voltageChartDischarging.title = "Voltage during discharging (" + str(float(math.ceil((len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            voltageChartDischarging.x_axis.tickLblPos = "low"
            voltageChartDischarging.x_axis.title = "Time [s]"
            voltageChartDischarging.y_axis.title = "Voltage [V]"

            # Create a graph for the Current during Disharging
            currentChartDischarging = ScatterChart()
            currentChartDischarging.legend = None
            currentSeriesDischarging = Series(currentDischarging, seconds, title_from_data=False)
            currentChartDischarging.series.append(currentSeriesDischarging)
            currentChartDischarging.title = "Current during discharging (" + str(float(math.ceil((len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            currentChartDischarging.x_axis.tickLblPos = "low"
            currentChartDischarging.x_axis.title = "Time [s]"
            currentChartDischarging.y_axis.title = "Current [mA]"

            # Create a graph for the Power during Discharging
            powerChartDischarging = ScatterChart()
            powerChartDischarging.legend = None
            powerSeriesDischarging = Series(powerDischarging, seconds, title_from_data=False)
            powerChartDischarging.series.append(powerSeriesDischarging)
            powerChartDischarging.title = "Power during discharging (" + str(float(math.ceil((len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            powerChartDischarging.x_axis.tickLblPos = "low"
            powerChartDischarging.x_axis.title = "Time [s]"
            powerChartDischarging.y_axis.title = "Power [W]"

            # Add our graphs to the sheet
            sheet.add_chart(voltageChartCharging, "F2")
            sheet.add_chart(currentChartCharging, "F22")
            sheet.add_chart(powerChartCharging, "F42")

            sheet.add_chart(voltageChartDischarging, "P2")
            sheet.add_chart(currentChartDischarging, "P22")
            sheet.add_chart(powerChartDischarging, "P42")
            

        wb.save(filePath + ".xlsx")



    def graphCapacity(self, cyclenumber, temperature, C_rate):
        # Label the graph correctly
        plt.style.use("ggplot")
        plt.xlabel("Time (S)")
        plt.ylabel("Voltage (V)")
        plt.title(f"Capacity at {temperature}° celsius with {C_rate} C current")
        plt.plot(range(len(self.volts)), self.volts, color = "#3a55b4")
        # Calculate the amphour capacity
        ahCapacity = len(self.volts) / 3600
        # Inclue the amphour capacity in the graph
        plt.legend([f"{'{:.2f}'.format(ahCapacity)} aH Capacity"])
        # Store the graph in a file
        try:
            plt.savefig(f"Desktop/ALOR/Al-ion Battery Test Software/Data/Capacity test for {C_rate}C nr. {cyclenumber + 1} at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S")) + ".png")
        except:
            plt.savefig(os.path.abspath(f"Data/Capacity test for {C_rate}C nr. {cyclenumber + 1} at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S")) + ".png"))
        # Clear the graph
        plt.clf()
        

    def graphEndurance(self, temperature, C_rate, ampHours):
        # Label the graph correctly
        plt.style.use("ggplot")
        plt.ylabel("Capacity (Ah)")
        plt.xlabel("Cycle number")
        plt.title(f"Change in capacity at {temperature}° celsius with {C_rate} C current")
        plt.plot(range(len(ampHours)), ampHours, "o", color = "#3a55b4")
        # Store the graph in a file
        try:
            plt.savefig(f"Desktop/ALOR/Al-ion Battery Test Software/Data/Endurance test for {C_rate}C at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S")) + ".png")
        except:
            plt.savefig(os.path.abspath(f"Data/Endurance test for {C_rate}C at {temperature}° celsius     "  + str(datetime.now().strftime("%d_%m_%Y %H_%M_%S")) + ".png"))
        # Clear the graph
        plt.clf()

# Notað til að keyra sjálfvirk gröf á utanaðkomandi csv skrár
# dataStorage = DataStorage()
# dataStorage.exportXLSXFile("C:/Users/runson/Dropbox/Sharing/Alor test/UPS Test for 1C nr. 2 at 20° celsius     03_01_2023 15_21_10",chargeTime="180",timeInterval=0.2)

        

