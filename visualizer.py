
import pandas as pd
import matplotlib.pyplot as plt

class showTest:
    def __init__(self):
        self.vis = True
    def plot(self = None, data = 0):
        if type(data) != type(pd.DataFrame([])):
            print("You need to provide some data to be able to plot it")
            raise ValueError

        # I assume that the user wants to plot the last cycle of the test
        # this lines filters for the last cycle
        Filter = data[data['cycle_number'] == data['cycle_number'].max()]

        #print(Filter.index)
        start = Filter.index[0]
        # this start fixes the problem when you examine data that is not at the first cycle.
        # we need to find the starting point at this current cycle


        title = Filter['testtype'][start]

        if title == "constantVoltageTest" or title == "NEWupsTest"  or title == "upsTest"  or\
                title == "constantCurrentTest":

            for i, x in enumerate(Filter['current']):
                if i == 0:
                    continue
                else:
                    # Filter['current'][i + start] = Filter['current'][i + start] + Filter['current'][i + start-1]
                    Filter.loc[i + start, 'current'] = Filter.loc[i + start, 'current'] + Filter.loc[i + start - 1, 'current']

            max = Filter['volts'].max()
            min = Filter['volts'].min()
            corrVolts = 1-(max-Filter['volts'])/(max-min)
            plt.plot(corrVolts,Filter['current'])
            plt.ylabel('current')
            plt.xlabel('goal voltage %')
            title = Filter['testtype'][start]
            plt.title(f"Voltage path for {title}")
            plt.grid(True)

        elif title == "discharging" or title == "charging":
            charging = Filter[Filter['testtype'] == "charging"]
            discharging = Filter[Filter['testtype'] == "discharging"]

            plt.plot(charging['time'], charging['volts'],label='charging')
            plt.plot(discharging['time'], discharging['volts'],label='discharging')

            plt.ylabel('volts')
            plt.xlabel('time')
            plt.legend()
            plt.title(f"Voltage path for regular discharging/charging")
            plt.grid(True)
            #plt.xlim(0, Filter['time'].max())
            #plt.ylim(0, Filter['volts'].max())
        plt.show()
