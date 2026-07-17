import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import time
from datetime import datetime
import math

# Import existing modules
# from Miggy import Miggy
# from AIMiggyController import AIMiggy

class ConsoleRedirector:
    def __init__(self, text_widget, queue):
        self.text_widget = text_widget
        self.queue = queue

    def write(self, msg):
        self.queue.put(msg)

    def flush(self):
        pass


class MiggyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MiggyOS Control Center")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # State
        self.miggy = None
        self.aimiggy = None
        self.is_connected = False
        self.worker_thread = None
        self.running_operation = False
        self.log_queue = queue.Queue()
        self.after_id = None

        # Build UI
        self.build_ui()
        self.setup_menu()
        self.setup_statusbar()

        # Redirect stdout/stderr to console
        sys.stdout = ConsoleRedirector(self.console_text, self.log_queue)
        sys.stderr = ConsoleRedirector(self.console_text, self.log_queue)

        # Start log polling
        self.poll_log_queue()

    def build_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Connection frame
        self.conn_frame = ttk.LabelFrame(self.main_frame, text="Connection", padding="5")
        self.conn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.conn_frame, text="Interface:").grid(row=0, column=0, sticky=tk.W)
        self.interface_var = tk.StringVar(value="eth0")
        ttk.Entry(self.conn_frame, textvariable=self.interface_var, width=15).grid(row=0, column=1, padx=5)
        self.connect_btn = ttk.Button(self.conn_frame, text="Connect", command=self.on_connect)
        self.connect_btn.grid(row=0, column=2, padx=5)
        self.disconnect_btn = ttk.Button(self.conn_frame, text="Disconnect", command=self.on_disconnect, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=3, padx=5)
        self.status_label = ttk.Label(self.conn_frame, text="● Disconnected", foreground="red")
        self.status_label.grid(row=0, column=4, padx=10)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: AI Control
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="🤖 AI Control")
        self.build_ai_tab()

        # Tab 2: Manual Control
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text="🎮 Manual Control")
        self.build_manual_tab()

        # Tab 3: Status
        self.status_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.status_tab, text="📊 Status")
        self.build_status_tab()

        # Tab 4: Console
        self.console_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.console_tab, text="💻 Console")
        self.build_console_tab()

        # Emergency stop button
        self.emergency_frame = ttk.Frame(self.main_frame)
        self.emergency_frame.pack(fill=tk.X, pady=5)
        self.emergency_btn = ttk.Button(self.emergency_frame, text="🛑 EMERGENCY STOP", command=self.emergency_stop,
                                        style="Emergency.TButton")
        self.emergency_btn.pack(side=tk.RIGHT)

        # Configure style for emergency button
        style = ttk.Style()
        style.configure("Emergency.TButton", foreground="white", background="red", font=('Arial', 12, 'bold'))

    def build_ai_tab(self):
        # Query input
        frame_query = ttk.Frame(self.ai_tab)
        frame_query.pack(fill=tk.X, pady=5)
        ttk.Label(frame_query, text="Command:").pack(side=tk.LEFT)
        self.ai_entry = ttk.Entry(frame_query)
        self.ai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.ai_send_btn = ttk.Button(frame_query, text="Generate Code", command=self.on_ai_send)
        self.ai_send_btn.pack(side=tk.LEFT)

        # Code preview
        ttk.Label(self.ai_tab, text="Generated Code:").pack(anchor=tk.W, pady=(10, 0))
        self.code_text = scrolledtext.ScrolledText(self.ai_tab, height=8, font=("Courier New", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Execute button
        self.execute_btn = ttk.Button(self.ai_tab, text="▶ Execute Code", command=self.on_execute_code, state=tk.DISABLED)
        self.execute_btn.pack(pady=5)

    def build_manual_tab(self):
        # Movement controls
        move_frame = ttk.LabelFrame(self.manual_tab, text="Movement", padding="5")
        move_frame.pack(fill=tk.X, pady=5)

        ttk.Label(move_frame, text="Distance (m):").grid(row=0, column=0, sticky=tk.W)
        self.dist_entry = ttk.Entry(move_frame, width=10)
        self.dist_entry.grid(row=0, column=1, padx=5)
        self.dist_entry.insert(0, "1.0")

        ttk.Label(move_frame, text="Speed (m/s):").grid(row=0, column=2, sticky=tk.W)
        self.speed_entry = ttk.Entry(move_frame, width=10)
        self.speed_entry.grid(row=0, column=3, padx=5)
        self.speed_entry.insert(0, "0.5")

        btn_forward = ttk.Button(move_frame, text="⬆ Forward", command=lambda: self.manual_move(float(self.dist_entry.get()), float(self.speed_entry.get())))
        btn_forward.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        btn_backward = ttk.Button(move_frame, text="⬇ Backward", command=lambda: self.manual_move(-float(self.dist_entry.get()), float(self.speed_entry.get())))
        btn_backward.grid(row=1, column=2, columnspan=2, pady=5, sticky=tk.W)

        # Rotation controls
        rot_frame = ttk.LabelFrame(self.manual_tab, text="Rotation", padding="5")
        rot_frame.pack(fill=tk.X, pady=5)

        ttk.Label(rot_frame, text="Angle (deg):").grid(row=0, column=0, sticky=tk.W)
        self.angle_entry = ttk.Entry(rot_frame, width=10)
        self.angle_entry.grid(row=0, column=1, padx=5)
        self.angle_entry.insert(0, "90")

        ttk.Label(rot_frame, text="Speed (rad/s):").grid(row=0, column=2, sticky=tk.W)
        self.rot_speed_entry = ttk.Entry(rot_frame, width=10)
        self.rot_speed_entry.grid(row=0, column=3, padx=5)
        self.rot_speed_entry.insert(0, "1.0")

        btn_left = ttk.Button(rot_frame, text="↺ Left", command=lambda: self.manual_rotate(math.radians(float(self.angle_entry.get())), float(self.rot_speed_entry.get())))
        btn_left.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        btn_right = ttk.Button(rot_frame, text="↻ Right", command=lambda: self.manual_rotate(-math.radians(float(self.angle_entry.get())), -float(self.rot_speed_entry.get())))
        btn_right.grid(row=1, column=2, columnspan=2, pady=5, sticky=tk.W)

        # Posture controls
        posture_frame = ttk.LabelFrame(self.manual_tab, text="Posture", padding="5")
        posture_frame.pack(fill=tk.X, pady=5)

        ttk.Button(posture_frame, text="Stand", command=self.manual_stand).pack(side=tk.LEFT, padx=5)
        ttk.Button(posture_frame, text="Sit", command=self.manual_sit).pack(side=tk.LEFT, padx=5)

        # Arm special actions
        arm_frame = ttk.LabelFrame(self.manual_tab, text="Arm Actions", padding="5")
        arm_frame.pack(fill=tk.X, pady=5)

        self.arm_action_var = tk.StringVar()
        actions = ["shake hand", "high five", "hug", "high wave", "clap", "face wave",
                   "left kiss", "heart", "right heart", "hands up", "x-ray", "right hand up",
                   "reject", "right kiss", "two-hand kiss"]
        self.arm_combo = ttk.Combobox(arm_frame, textvariable=self.arm_action_var, values=actions, state="readonly")
        self.arm_combo.pack(side=tk.LEFT, padx=5)
        self.arm_combo.current(0)
        ttk.Button(arm_frame, text="Execute Arm Action", command=self.manual_arm_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(arm_frame, text="Release Arm", command=self.manual_release_arm).pack(side=tk.LEFT, padx=5)

        # Speech
        speech_frame = ttk.LabelFrame(self.manual_tab, text="Speech", padding="5")
        speech_frame.pack(fill=tk.X, pady=5)

        self.speech_entry = ttk.Entry(speech_frame)
        self.speech_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.speech_lang_var = tk.StringVar(value="english")
        lang_combo = ttk.Combobox(speech_frame, textvariable=self.speech_lang_var, values=["english", "chinese"], state="readonly", width=10)
        lang_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(speech_frame, text="Say", command=self.manual_say).pack(side=tk.LEFT, padx=5)

    def build_status_tab(self):
        self.status_text = scrolledtext.ScrolledText(self.status_tab, font=("Courier New", 10))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "Robot status will be displayed here when connected.\n")
        self.status_text.config(state=tk.DISABLED)

        # Refresh button
        ttk.Button(self.status_tab, text="Refresh Status", command=self.refresh_status).pack(pady=5)

    def build_console_tab(self):
        self.console_text = scrolledtext.ScrolledText(self.console_tab, font=("Courier New", 10), bg="black", fg="white")
        self.console_text.pack(fill=tk.BOTH, expand=True)
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, "MiggyOS Console ready.\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

        # Clear button
        ttk.Button(self.console_tab, text="Clear Console", command=self.clear_console).pack(pady=5)

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Connect...", command=self.on_connect)
        file_menu.add_command(label="Disconnect", command=self.on_disconnect)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def setup_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_connect(self):
        if self.is_connected:
            messagebox.showinfo("Info", "Already connected.")
            return
        interface = self.interface_var.get().strip()
        if not interface:
            messagebox.showerror("Error", "Interface cannot be empty.")
            return
        try:
            self.statusbar.config(text="Connecting...")
            #self.miggy = Miggy(interface)
            #self.aimiggy = AIMiggy()
            self.is_connected = True
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.status_label.config(text="● Connected", foreground="green")
            self.statusbar.config(text=f"Connected to {interface}")
            self.log_message(f"Connected to Miggy on {interface}")
            # Enable controls (already enabled by default)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.log_message(f"Connection failed: {str(e)}")
            self.statusbar.config(text="Connection failed")

    def on_disconnect(self):
        if not self.is_connected:
            return
        try:
            if self.miggy:
                self.miggy.stop()
        except:
            pass
        self.is_connected = False
        self.miggy = None
        self.aimiggy = None
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Disconnected", foreground="red")
        self.statusbar.config(text="Disconnected")
        self.log_message("Disconnected from Miggy")

    def on_exit(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.running_operation = False
            self.worker_thread.join(timeout=1)
        self.on_disconnect()
        self.root.quit()

    def on_ai_send(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to robot.")
            return
        query = self.ai_entry.get().strip()
        if not query:
            messagebox.showinfo("Info", "Please enter a command.")
            return
        self.ai_send_btn.config(state=tk.DISABLED)
        self.statusbar.config(text="Generating code...")
        try:
            # Ask AI for code
            #response = self.aimiggy.askAIMiggy(query)
            code = response.output_text.strip()
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(tk.END, code)
            self.execute_btn.config(state=tk.NORMAL)
            self.statusbar.config(text="Code generated. Review and execute.")
            self.log_message(f"AI generated code for: {query}")
        except Exception as e:
            messagebox.showerror("AI Error", f"Failed to generate code: {str(e)}")
            self.statusbar.config(text="AI generation failed")
            self.log_message(f"AI error: {str(e)}")
        self.ai_send_btn.config(state=tk.NORMAL)

    def on_execute_code(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        code = self.code_text.get(1.0, tk.END).strip()
        if not code:
            return
        self.execute_btn.config(state=tk.DISABLED)
        self.statusbar.config(text="Executing code...")
        # Run in thread
        self.run_in_thread(self.execute_code_thread, code)

    def execute_code_thread(self, code):
        try:
            # Use the existing miggy instance
            exec_globals = {"miggy": self.miggy, "math": math, "time": time}
            exec(code, exec_globals)
            self.root.after(0, self.on_execute_done, "Execution completed successfully.")
            self.log_message("Code executed successfully.")
        except Exception as e:
            self.root.after(0, self.on_execute_done, f"Execution error: {str(e)}")
            self.log_message(f"Code execution error: {str(e)}")

    def on_execute_done(self, msg):
        self.statusbar.config(text=msg)
        self.execute_btn.config(state=tk.NORMAL)
        # Optionally show message

    def manual_move(self, distance, speed):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.run_in_thread(self.miggy.move_dist, distance, speed)
        self.log_message(f"Move dist={distance}, speed={speed}")

    def manual_rotate(self, angle, speed):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.run_in_thread(self.miggy.rotate_angle, angle, speed)
        self.log_message(f"Rotate angle={angle}, speed={speed}")

    def manual_stand(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.run_in_thread(self.miggy.stand)
        self.log_message("Stand command issued")

    def manual_sit(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.run_in_thread(self.miggy.sit)
        self.log_message("Sit command issued")

    def manual_arm_action(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        action = self.arm_action_var.get()
        self.run_in_thread(self.miggy.run_special, action)
        self.log_message(f"Arm action: {action}")

    def manual_release_arm(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.run_in_thread(self.miggy.release_arm)
        self.log_message("Release arm")

    def manual_say(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        text = self.speech_entry.get().strip()
        if not text:
            messagebox.showinfo("Info", "Enter text to say.")
            return
        lang = self.speech_lang_var.get()
        self.run_in_thread(self.miggy.say, text, lang)
        self.log_message(f"Say: '{text}' in {lang}")

    def emergency_stop(self):
        if not self.is_connected:
            return
        self.run_in_thread(self.miggy.stop)
        self.log_message("EMERGENCY STOP issued.")
        self.statusbar.config(text="Emergency Stop")

    def refresh_status(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"\n--- Status at {datetime.now().strftime('%H:%M:%S')} ---\n")
        # For now, just a placeholder. Later we can read from StateDriver.
        self.status_text.insert(tk.END, "StateDriver not fully integrated yet.\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {msg}\n")

    def poll_log_queue(self):
        """Poll the log queue and update console text widget.
        Trim the console to a maximum number of lines and ensure each
        X request stays within a safe size. This prevents "PolyRequestTooLarge"
        errors when large log messages are inserted rapidly.
        """
        MAX_LINES = 2000
        MAX_CHUNK = 4096  # split large messages into manageable chunks
        try:
            while True:
                msg = self.log_queue.get_nowait()
                # Insert the message in chunks to avoid overly large X requests
                start = 0
                while start < len(msg):
                    chunk = msg[start:start + MAX_CHUNK]
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, chunk)
                    # Trim excess lines if over limit
                    line_count = int(self.console_text.index('end-1c').split('.')[0])
                    if line_count > MAX_LINES:
                        excess = line_count - MAX_LINES
                        self.console_text.delete('1.0', f"{excess + 1}.0")
                    self.console_text.see(tk.END)
                    self.console_text.config(state=tk.DISABLED)
                    start += MAX_CHUNK
        except queue.Empty:
            pass
        self.after_id = self.root.after(100, self.poll_log_queue)

    def clear_console(self):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state=tk.DISABLED)

    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread to avoid blocking GUI."""
        if self.running_operation:
            messagebox.showinfo("Info", "Another operation is already running. Please wait.")
            return
        self.running_operation = True
        self.statusbar.config(text="Operation in progress...")
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.root.after(0, self.on_operation_error, str(e))
            finally:
                self.running_operation = False
                self.root.after(0, self.on_operation_done)
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    def on_operation_error(self, err):
        messagebox.showerror("Operation Error", str(err))
        self.log_message(f"Operation error: {err}")

    def on_operation_done(self):
        self.statusbar.config(text="Ready")

    def show_about(self):
        messagebox.showinfo("About MiggyOS Control Center",
                            "MiggyOS Control Center\n"
                            "Version 1.0\n\n"
                            "Innovators: pickle69420 and roostr365\n"
                            "© 2026 All Rights Reserved")
    def on_close(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.on_exit()

def main():
    root = tk.Tk()
    app = MiggyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
