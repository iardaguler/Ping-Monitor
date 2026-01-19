import subprocess
import platform
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time

# ---------------- Globals ----------------
stop_ping_flag = False

# ---------------- Functions ----------------

def ping_target(ip):
    """Ping a single IP once and return latency (ms) or None if unreachable."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    ping_cmd = ["ping", param, "1", ip]

    try:
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None
        # Extract latency from output
        output = result.stdout
        latency = None
        for line in output.splitlines():
            if "time=" in line.lower():
                # Windows: time=12ms, Linux: time=0.012 ms
                parts = line.split("time=")[1]
                latency = parts.split()[0].replace("ms","")
                latency = float(latency)
                break
        return latency
    except Exception:
        return None

def get_mac(ip):
    """Get MAC address from ARP table."""
    try:
        arp_cmd = ["arp", "-a", ip]
        result = subprocess.run(arp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        mac = "Not found"
        for line in result.stdout.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if "-" in part or ":" in part:
                        mac = part
                        break
        return mac
    except Exception:
        return "Error"

def start_ping_monitor():
    global stop_ping_flag
    stop_ping_flag = False
    ips = ip_entry.get().strip()
    if not ips:
        messagebox.showerror("Error", "Please enter at least one target IP address.")
        return
    ips_list = [ip.strip() for ip in ips.split(",")]
    threading.Thread(target=ping_loop, args=(ips_list,), daemon=True).start()

def ping_loop(ips_list):
    global stop_ping_flag
    output_text.configure(state="normal")
    while not stop_ping_flag:
        for ip in ips_list:
            latency = ping_target(ip)
            timestamp = time.strftime("%H:%M:%S")
            if latency is None:
                output_text.insert(tk.END, f"[{timestamp}] {ip} - Unreachable\n", "fail")
            else:
                # Color based on latency
                if latency < 50:
                    tag = "fast"
                elif latency < 150:
                    tag = "medium"
                else:
                    tag = "slow"
                output_text.insert(tk.END, f"[{timestamp}] {ip} - {latency}ms\n", tag)
            mac = get_mac(ip)
            output_text.insert(tk.END, f"MAC: {mac}\n", "mac")
            output_text.see(tk.END)
        output_text.insert(tk.END, "-"*50 + "\n")
        output_text.see(tk.END)
        time.sleep(2)  # wait before next round
    output_text.configure(state="disabled")

def stop_ping():
    global stop_ping_flag
    stop_ping_flag = True

def clear_output():
    output_text.configure(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.configure(state="disabled")

# ---------------- GUI ----------------

root = tk.Tk()
root.title("Advanced Ping & MAC Monitor")

# Fixed window size
window_width = 700
window_height = 500
root.resizable(False, False)  # disable resizing

# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

# Background color
root.configure(bg="#2e3f4f")

FONT_LABEL = ("Arial", 12, "bold")
FONT_BUTTON = ("Arial", 11)
FONT_TEXT = ("Consolas", 10)

# Top frame
top_frame = tk.Frame(root, pady=10, bg="#2e3f4f")
top_frame.pack(fill="x")

tk.Label(top_frame, text="Target IP:", font=FONT_LABEL, bg="#2e3f4f", fg="white").pack(side="left", padx=5)
ip_entry = tk.Entry(top_frame, font=FONT_TEXT, width=35)
ip_entry.pack(side="left", padx=5)

tk.Button(top_frame, text="Start Ping Monitor", font=FONT_BUTTON, command=start_ping_monitor, bg="#4CAF50", fg="white").pack(side="left", padx=5)
tk.Button(top_frame, text="Stop", font=FONT_BUTTON, command=stop_ping, bg="#f39c12", fg="white").pack(side="left", padx=5)
tk.Button(top_frame, text="Clear Output", font=FONT_BUTTON, command=clear_output, bg="#f44336", fg="white").pack(side="left", padx=5)

# Output frame
output_frame = tk.Frame(root, padx=10, pady=10, bg="#2e3f4f")
output_frame.pack(fill="both", expand=True)

output_text = scrolledtext.ScrolledText(
    output_frame,
    height=25,
    font=FONT_TEXT,
    state="disabled",
    bg="#1e2a33",
    fg="white",
    insertbackground="white"
)
output_text.pack(fill="both", expand=True)

# Tags for colors
output_text.tag_config("fast", foreground="#00ff00")    # Green <50ms
output_text.tag_config("medium", foreground="#ffff00")  # Yellow 50-150ms
output_text.tag_config("slow", foreground="#ff5555")    # Red >150ms
output_text.tag_config("fail", foreground="#ff3333")    # Ping failed
output_text.tag_config("mac", foreground="#ffa500")     # MAC address

root.mainloop()
