import tkinter as tk
from tkinter import ttk
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Set dark style for matplotlib
plt.style.use('dark_background')

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

class SmartWatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartWatch Energy Harvesting")
        self.root.configure(bg='#2B2B2B')

        style = ttk.Style()
        style.configure('Custom.TLabel', background='#2B2B2B', foreground='#FFFFFF', font=('Helvetica', 12))
        style.configure('Notification.TLabel', background='#1C1C1C', foreground='#FF6666', font=('Helvetica', 12, 'italic'))
        style.configure('Download.TButton',
                        background='#000000',
                        foreground='black',
                        font=('Helvetica', 12, 'bold'),
                        padding=6)
        style.map('Download.TButton',
                  background=[('active', '#1A1A1A')],
                  foreground=[('disabled', '#030303')])

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.battery = 50.0
        self.ke_value = 2.0
        self.harvested = False
        self.ke_history = []

        header = ttk.Label(main_frame, text="Smart Watch Energy Monitor", style='Custom.TLabel', font=('Helvetica', 16, 'bold'))
        header.pack(pady=10)

        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.pack(fill=tk.X, pady=10)

        ke_frame = ttk.Frame(metrics_frame)
        ke_frame.pack(side=tk.LEFT, expand=True, padx=10)
        ttk.Label(ke_frame, text="Kinetic Energy", style='Custom.TLabel').pack()
        self.ke_label = ttk.Label(ke_frame, text=f"{self.ke_value:.2f}", style='Custom.TLabel', font=('Helvetica', 24))
        self.ke_label.pack()

        bat_frame = ttk.Frame(metrics_frame)
        bat_frame.pack(side=tk.LEFT, expand=True, padx=10)
        ttk.Label(bat_frame, text="Battery Level", style='Custom.TLabel').pack()
        self.battery_label = ttk.Label(bat_frame, text=f"{self.battery:.1f}%", style='Custom.TLabel', font=('Helvetica', 24))
        self.battery_label.pack()

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

        ttk.Label(main_frame, text="Notifications", style='Custom.TLabel').pack(pady=(10, 0))
        self.notification_label = ttk.Label(main_frame, text="", style='Notification.TLabel', anchor='center', wraplength=600)
        self.notification_label.pack(fill=tk.X, padx=10, pady=5)

        download_btn = ttk.Button(main_frame, text="Download Energy Report", style='Download.TButton', command=self.download_report)
        download_btn.pack(pady=10)

        self.update()

    def generate_notification(self, ke_value):
        thresholds = [
            (1.5, 2.0, "Gentle movement detected. Energy harvesting initiated."),
            (2.0, 2.5, "Light activity. Battery charging slowly."),
            (2.5, 3.0, "Moderate motion. Keep moving!"),
            (3.0, 3.5, "Good pace! Energy harvesting is efficient."),
            (3.5, 4.0, "Strong movement. Battery boost incoming!"),
            (4.0, 4.5, "High kinetic energy. Excellent performance."),
            (4.5, 5.0, "Peak efficiency! You're maximizing energy capture."),
            (5.0, 5.5, "Intense motion. Keep an eye on device temperature."),
            (5.5, 6.0, "High surge detected. Maintain steady movement."),
            (6.0, 6.5, "Device working hard. Consider slowing down soon."),
            (6.5, 7.0, "Very high kinetic energy. Monitor battery health."),
            (7.0, 7.5, "Risk of overload. Reduce motion intensity."),
            (7.5, 8.0, "Safety alert. Movement too intense."),
            (8.0, 8.5, "Critical threshold approaching. Slow down."),
            (8.5, 10.0, "Maximum limit reached. Stop and rest.")
        ]
        for low, high, message in thresholds:
            if low <= ke_value < high or (low <= ke_value <= high and high == 10.0):
                return f"KE {ke_value:.2f}: {message}"
        return ""

    def generate_energy_summary(self):
        if not self.ke_history:
            return "No kinetic energy data available."

        avg_ke = sum(self.ke_history) / len(self.ke_history)
        prompt = f"""Generate a short energy harvesting report based on the following:
- Average kinetic energy: {avg_ke:.2f}
- Battery level: {self.battery:.1f}%

Include 2 helpful tips for improving energy harvesting and 1 caution if KE is too high. Keep it formal and concise."""

        try:
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print("Gemini error:", e)
            return "⚠️ Could not generate summary."

    def create_pdf_report(self, summary):
        summary = summary.encode('latin-1', 'ignore').decode('latin-1')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, "Smart Watch Energy Harvesting Report", ln=True, align='C')
        pdf.set_font("Helvetica", '', 12)
        pdf.set_text_color(60, 60, 60)
        pdf.ln(10)
        pdf.multi_cell(0, 10, summary)
        pdf.set_y(-30)
        pdf.set_font("Helvetica", 'I', 10)
        pdf.cell(0, 10, "Generated by SmartWatchApp", align='C')
        pdf.output("Smartwatch_Energy_Report.pdf")

    def download_report(self):
        summary = self.generate_energy_summary()
        self.create_pdf_report(summary)
        self.notification_label.config(text="✅ PDF saved as Smartwatch_Energy_Report.pdf")

    def update(self):
        previous_ke = self.ke_value

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
                self.harvested = False

        # Track KE history for summary
        self.ke_history.append(self.ke_value)

        # Update UI labels
        self.ke_label.config(text=f"{self.ke_value:.2f}")
        self.battery_label.config(text=f"{self.battery:.1f}%")

        # Update notification
        message = self.generate_notification(self.ke_value)
        self.notification_label.config(text=message)

        # Update chart colors
        ke_color = plt.cm.RdYlGn(self.ke_value / 8)
        bat_color = plt.cm.RdYlGn(self.battery / 100)
        self.battery_line.set_color(bat_color)
        self.ke_line.set_color(ke_color)

        # Update chart titles
        status = 'Charging' if self.harvested else 'Standby'
        self.ax1.set_title(f"Battery: {self.battery:.1f}% | {status}", color='white')
        self.ax2.set_title(f"Kinetic Energy: {self.ke_value:.2f}", color='white')

        # Update chart data
        self.battery_data = np.roll(self.battery_data, -1)
        self.battery_data[-1] = self.battery
        self.battery_line.set_ydata(self.battery_data)

        self.ke_data = np.roll(self.ke_data, -1)
        self.ke_data[-1] = self.ke_value
        self.ke_line.set_ydata(self.ke_data)

        # Redraw canvas
        self.canvas.draw()

        # Schedule next update
        self.root.after(500, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartWatchApp(root)
    root.mainloop()
