import tkinter as tk
from tkinter import ttk
import numpy as np
import joblib
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set dark style for matplotlib
plt.style.use('dark_background')

class SmartWatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartWatch Energy Harvesting")
        self.root.configure(bg='#2B2B2B')  # Dark theme background
        
        # Configure style
        style = ttk.Style()
        style.configure('Custom.TLabel', background='#2B2B2B', foreground='#FFFFFF', font=('Helvetica', 12))
        style.configure('Notification.TLabel', background='#1C1C1C', foreground='#FF6666', font=('Helvetica', 12, 'italic'))

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # State vars
        self.battery = 50.0
        self.ke_value = 2.0
        self.harvested = False
        
        # Header
        header = ttk.Label(main_frame, text="Smart Watch Energy Monitor", style='Custom.TLabel', font=('Helvetica', 16, 'bold'))
        header.pack(pady=10)
        
        # Metrics frame
        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        # KE display
        ke_frame = ttk.Frame(metrics_frame)
        ke_frame.pack(side=tk.LEFT, expand=True, padx=10)
        ttk.Label(ke_frame, text="Kinetic Energy", style='Custom.TLabel').pack()
        self.ke_label = ttk.Label(ke_frame, text=f"{self.ke_value:.2f}", style='Custom.TLabel', font=('Helvetica', 24))
        self.ke_label.pack()
        
        # Battery display
        bat_frame = ttk.Frame(metrics_frame)
        bat_frame.pack(side=tk.LEFT, expand=True, padx=10)
        ttk.Label(bat_frame, text="Battery Level", style='Custom.TLabel').pack()
        self.battery_label = ttk.Label(bat_frame, text=f"{self.battery:.1f}%", style='Custom.TLabel', font=('Helvetica', 24))
        self.battery_label.pack()

        # Matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.patch.set_facecolor('#2B2B2B')
        
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#1C1C1C')
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#404040')
        
        self.ax1.set_title("Battery Level", color='white', pad=10)
        self.ax2.set_title("Kinetic Energy", color='white', pad=10)
        
        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 10)
        
        self.x = np.arange(30)
        self.battery_data = np.full(30, self.battery)
        self.ke_data = np.full(30, self.ke_value)
        
        self.battery_line, = self.ax1.plot(self.x, self.battery_data, color='#00ff00', linewidth=2)
        self.ke_line, = self.ax2.plot(self.x, self.ke_data, color='#ff3366', linewidth=2)
        
        plt.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

        # Notification bar
        ttk.Label(main_frame, text="Notifications", style='Custom.TLabel').pack(pady=(10, 0))
        self.notification_label = ttk.Label(main_frame, text="", style='Notification.TLabel', anchor='center', wraplength=600)
        self.notification_label.pack(fill=tk.X, padx=10, pady=5)

        # Start simulation loop
        self.update()

    def generate_notification(self, ke_value):
        if 1.5 <= ke_value < 2.0:
            return f"KE {ke_value:.2f}: Gentle movement detected. Energy harvesting initiated."
        elif 2.0 <= ke_value < 2.5:
            return f"KE {ke_value:.2f}: Light activity. Battery charging slowly."
        elif 2.5 <= ke_value < 3.0:
            return f"KE {ke_value:.2f}: Moderate motion. Keep moving!"
        elif 3.0 <= ke_value < 3.5:
            return f"KE {ke_value:.2f}: Good pace! Energy harvesting is efficient."
        elif 3.5 <= ke_value < 4.0:
            return f"KE {ke_value:.2f}: Strong movement. Battery boost incoming!"
        elif 4.0 <= ke_value < 4.5:
            return f"KE {ke_value:.2f}: High kinetic energy. Excellent performance."
        elif 4.5 <= ke_value < 5.0:
            return f"KE {ke_value:.2f}: Peak efficiency! You're maximizing energy capture."
        elif 5.0 <= ke_value < 5.5:
            return f"KE {ke_value:.2f}: Intense motion. Keep an eye on device temperature."
        elif 5.5 <= ke_value < 6.0:
            return f"KE {ke_value:.2f}: High surge detected. Maintain steady movement."
        elif 6.0 <= ke_value < 6.5:
            return f"KE {ke_value:.2f}: Device working hard. Consider slowing down soon."
        elif 6.5 <= ke_value < 7.0:
            return f"KE {ke_value:.2f}: Very high kinetic energy. Monitor battery health."
        elif 7.0 <= ke_value < 7.5:
            return f"KE {ke_value:.2f}: Risk of overload. Reduce motion intensity."
        elif 7.5 <= ke_value < 8.0:
            return f"KE {ke_value:.2f}: Safety alert. Movement too intense."
        elif 8.0 <= ke_value < 8.5:
            return f"KE {ke_value:.2f}: Critical threshold approaching. Slow down."
        elif 8.5 <= ke_value <= 10.0:
            return f"KE {ke_value:.2f}: Maximum limit reached. Stop and rest."
        else:
            return ""  # No message outside 1.5–5.0 range

    def update(self):
        previous_ke = self.ke_value

        if self.ke_value > 6.0:
            self.ke_value = max(1.0, self.ke_value * 0.7)
        else:
            base_change = random.uniform(-0.6, 0.6)
            spike_prob = 0.1 * (1 - self.ke_value / 8.0)
            if random.random() < spike_prob:
                spike = random.uniform(4.5, 9.0)
                spike *= (1 - self.ke_value / 8.0)
                self.ke_value += spike
            self.ke_value += base_change

        self.ke_value = max(0.5, min(8.0, self.ke_value))
        ke_change = self.ke_value - previous_ke

        if ke_change < 0:
            drain = abs(ke_change) * 2.0
            self.battery = max(0, self.battery - drain)
            self.harvested = False
        else:
            charge = ke_change * 3.0
            if self.battery < 100:
                self.battery = min(100, self.battery + charge)
                self.harvested = True
            else:
                self.harvested = False

        self.ke_label.config(text=f"{self.ke_value:.2f}")
        self.battery_label.config(text=f"{self.battery:.1f}%")

        message = self.generate_notification(self.ke_value)
        self.notification_label.config(text=message)

        ke_color = plt.cm.RdYlGn(self.ke_value / 8)
        bat_color = plt.cm.RdYlGn(self.battery / 100)

        self.battery_line.set_color(bat_color)
        self.ke_line.set_color(ke_color)

        status = 'Charging' if self.harvested else 'Standby'
        self.ax1.set_title(f"Battery: {self.battery:.1f}% | {status}", color='white')
        self.ax2.set_title(f"Kinetic Energy: {self.ke_value:.2f}", color='white')

        self.battery_data = np.roll(self.battery_data, -1)
        self.battery_data[-1] = self.battery
        self.battery_line.set_ydata(self.battery_data)

        self.ke_data = np.roll(self.ke_data, -1)
        self.ke_data[-1] = self.ke_value
        self.ke_line.set_ydata(self.ke_data)

        self.canvas.draw()
        self.root.after(500, self.update)

# Run
root = tk.Tk()
app = SmartWatchApp(root)
root.mainloop()
