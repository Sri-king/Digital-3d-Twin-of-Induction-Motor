import matplotlib.pyplot as plt
import collections
import warnings

warnings.filterwarnings("ignore", module="matplotlib")

class LivePlotter:
    def __init__(self):
        self.maxlen = 200
        
        self.times = collections.deque(maxlen=self.maxlen)
        self.rpms = collections.deque(maxlen=self.maxlen)
        self.currents = collections.deque(maxlen=self.maxlen)
        self.temps = collections.deque(maxlen=self.maxlen)
        self.vibs = collections.deque(maxlen=self.maxlen)
        
        plt.ion()
        self.fig, self.axs = plt.subplots(2, 2, figsize=(10, 6))
        self.fig.suptitle('Digital Twin Live Analytics')
        
        self.line_rpm, = self.axs[0,0].plot([], [], 'b-')
        self.axs[0,0].set_title('RPM vs Time')
        self.axs[0,0].set_ylabel('RPM')
        self.axs[0,0].grid(True)
        
        self.line_current, = self.axs[0,1].plot([], [], 'r-')
        self.axs[0,1].set_title('Current vs Time')
        self.axs[0,1].set_ylabel('Amps')
        self.axs[0,1].grid(True)
        
        self.line_temp, = self.axs[1,0].plot([], [], 'g-')
        self.axs[1,0].set_title('Temperature vs Time')
        self.axs[1,0].set_ylabel('°C')
        self.axs[1,0].grid(True)
        
        self.line_vib, = self.axs[1,1].plot([], [], 'm-')
        self.axs[1,1].set_title('Vibration vs Time')
        self.axs[1,1].set_ylabel('RMS')
        self.axs[1,1].grid(True)
        
        plt.tight_layout()
        plt.show(block=False)

    def update(self, sensor_data):
        self.times.append(sensor_data['Time'])
        self.rpms.append(sensor_data['RPM'])
        self.currents.append(sensor_data['Current'])
        self.temps.append(sensor_data['Temperature'])
        self.vibs.append(sensor_data['Vibration'])
        
        self.line_rpm.set_xdata(self.times)
        self.line_rpm.set_ydata(self.rpms)
        self.axs[0,0].relim()
        self.axs[0,0].autoscale_view()
        
        self.line_current.set_xdata(self.times)
        self.line_current.set_ydata(self.currents)
        self.axs[0,1].relim()
        self.axs[0,1].autoscale_view()
        
        self.line_temp.set_xdata(self.times)
        self.line_temp.set_ydata(self.temps)
        self.axs[1,0].relim()
        self.axs[1,0].autoscale_view()
        
        self.line_vib.set_xdata(self.times)
        self.line_vib.set_ydata(self.vibs)
        self.axs[1,1].relim()
        self.axs[1,1].autoscale_view()
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)
