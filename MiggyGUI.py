import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import math
import time
from datetime import datetime

# Robot and AI support are optional at import time so the GUI can still open
# on machines without the Unitree SDK or an API key configured.
try:
    from Miggy import Miggy
    MIGGY_IMPORT_ERROR = None
except Exception as _e:
    Miggy = None
    MIGGY_IMPORT_ERROR = _e

try:
    from AIMiggyController import AIMiggy, strip_code_fences
    AI_IMPORT_ERROR = None
except Exception as _e:
    AIMiggy = None
    strip_code_fences = None
    AI_IMPORT_ERROR = _e


class ConsoleRedirector:
    def __init__(self, queue):
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
        self.running_operation = False
        self.log_queue = queue.Queue()
        self.after_id = None

        # Build UI
        self.build_ui()
        self.setup_menu()
        self.setup_statusbar()

        # Redirect stdout/stderr to console
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = ConsoleRedirector(self.log_queue)
        sys.stderr = ConsoleRedirector(self.log_queue)

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
        self.status_label = ttk.Label(self.conn_frame, text="â— Disconnected", foreground="red")
        self.status_label.grid(row=0, column=4, padx=10)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: AI Control
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="ðŸ¤– AI Control")
        self.build_ai_tab()

        # Tab 2: Manual Control
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text="ðŸŽ® Manual Control")
        self.build_manual_tab()

        # Tab 3: Status
        self.status_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.status_tab, text="ðŸ“Š Status")
        self.build_status_tab()

        # Tab 4: Console
        self.console_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.console_tab, text="ðŸ’» Console")
        self.build_console_tab()

        # Emergency stop button
        self.emergency_frame = ttk.Frame(self.main_frame)
        self.emergency_frame.pack(fill=tk.X, pady=5)
        self.emergency_btn = ttk.Button(self.emergency_frame, text="ðŸ›‘ EMERGENCY STOP", command=self.emergency_stop,
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
        self.ai_entry.bind("<Return>", lambda event: self.on_ai_send())
        self.ai_send_btn = ttk.Button(frame_query, text="Generate Code", command=self.on_ai_send)
        self.ai_send_btn.pack(side=tk.LEFT)

        # Code preview
        ttk.Label(self.ai_tab, text="Generated Code:").pack(anchor=tk.W, pady=(10, 0))
        self.code_text = scrolledtext.ScrolledText(self.ai_tab, height=8, font=("Courier New", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Execute button
        self.execute_btn = ttk.Button(self.ai_tab, text="â–¶ Execute Code", command=self.on_execute_code, state=tk.DISABLED)
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

        btn_forward = ttk.Button(move_frame, text="â¬† Forward", command=lambda: self.on_move_clicked(1))
        btn_forward.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        btn_backward = ttk.Button(move_frame, text="â¬‡ Backward", command=lambda: self.on_move_clicked(-1))
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

        btn_left = ttk.Button(rot_frame, text="â†º Left", command=lambda: self.on_rotate_clicked(1))
        btn_left.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        btn_right = ttk.Button(rot_frame, text="â†» Right", command=lambda: self.on_rotate_clicked(-1))
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
        file_menu.add_command(label="Exit", command=self.on_close)
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
        if Miggy is None:
            messagebox.showerror("Error",
                                 "Robot support is unavailable (is unitree_sdk2py installed?):\n"
                                 f"{MIGGY_IMPORT_ERROR}")
            return
        self.connect_btn.config(state=tk.DISABLED)
        self.statusbar.config(text="Connecting...")

        # Connect in a background thread so DDS init doesn't freeze the GUI
        def worker():
            try:
                miggy = Miggy(interface)
            except Exception as e:
                self.root.after(0, self.on_connect_failed, str(e))
                return
            aimiggy = None
            ai_error = None
            if AIMiggy is not None:
                try:
                    aimiggy = AIMiggy()
                except Exception as e:
                    ai_error = str(e)
            else:
                ai_error = str(AI_IMPORT_ERROR)
            self.root.after(0, self.on_connect_success, miggy, aimiggy, ai_error, interface)

        threading.Thread(target=worker, daemon=True).start()

    def on_connect_success(self, miggy, aimiggy, ai_error, interface):
        self.miggy = miggy
        self.aimiggy = aimiggy
        self.is_connected = True
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.status_label.config(text="â— Connected", foreground="green")
        self.statusbar.config(text=f"Connected to {interface}")
        self.log_message(f"Connected to Miggy on {interface}")
        if ai_error:
            self.ai_send_btn.config(state=tk.DISABLED)
            self.log_message(f"AI control unavailable: {ai_error}")
        else:
            self.ai_send_btn.config(state=tk.NORMAL)

    def on_connect_failed(self, error):
        self.connect_btn.config(state=tk.NORMAL)
        self.statusbar.config(text="Connection failed")
        self.log_message(f"Connection failed: {error}")
        messagebox.showerror("Connection Error", f"Failed to connect: {error}")

    def on_disconnect(self):
        if not self.is_connected:
            return
        try:
            if self.miggy:
                self.miggy.stop()
        except Exception:
            pass
        self.is_connected = False
        self.miggy = None
        self.aimiggy = None
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.execute_btn.config(state=tk.DISABLED)
        self.ai_send_btn.config(state=tk.NORMAL)
        self.status_label.config(text="â— Disconnected", foreground="red")
        self.statusbar.config(text="Disconnected")
        self.log_message("Disconnected from Miggy")

    def on_ai_send(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to robot.")
            return
        if self.aimiggy is None:
            messagebox.showerror("Error",
                                 "AI control is unavailable. Check that the openai package is "
                                 "installed and NVIDIA_API_KEY is set.")
            return
        query = self.ai_entry.get().strip()
        if not query:
            messagebox.showinfo("Info", "Please enter a command.")
            return
        self.ai_send_btn.config(state=tk.DISABLED)
        self.statusbar.config(text="Generating code...")

        # Network call runs in a background thread so the GUI stays responsive
        def worker():
            try:
                response = self.aimiggy.askAIMiggy(query)
                code = strip_code_fences(response.output_text)
                self.root.after(0, self.on_ai_response, query, code)
            except Exception as e:
                self.root.after(0, self.on_ai_error, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def on_ai_response(self, query, code):
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, code)
        self.execute_btn.config(state=tk.NORMAL)
        self.ai_send_btn.config(state=tk.NORMAL)
        self.statusbar.config(text="Code generated. Review and execute.")
        self.log_message(f"AI generated code for: {query}")

    def on_ai_error(self, error):
        self.ai_send_btn.config(state=tk.NORMAL)
        self.statusbar.config(text="AI generation failed")
        self.log_message(f"AI error: {error}")
        messagebox.showerror("AI Error", f"Failed to generate code: {error}")

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

    def parse_float_entries(self, *fields):
        """Read (entry, name) pairs as floats; show an error and return None on bad input."""
        values = []
        for entry, name in fields:
            try:
                values.append(float(entry.get()))
            except ValueError:
                messagebox.showerror("Error", f"{name} must be a number.")
                return None
        return values

    def on_move_clicked(self, direction):
        values = self.parse_float_entries((self.dist_entry, "Distance"),
                                          (self.speed_entry, "Speed"))
        if values is None:
            return
        distance, speed = values
        self.manual_move(direction * abs(distance), abs(speed))

    def on_rotate_clicked(self, direction):
        values = self.parse_float_entries((self.angle_entry, "Angle"),
                                          (self.rot_speed_entry, "Rotation speed"))
        if values is None:
            return
        angle, speed = values
        self.manual_rotate(direction * math.radians(abs(angle)), abs(speed))

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
        if not self.is_connected or not self.miggy:
            return
        # Deliberately bypasses run_in_thread: the stop must fire even (especially)
        # while another operation is in progress.
        miggy = self.miggy

        def worker():
            try:
                miggy.stop()
            except Exception as e:
                self.log_message(f"Emergency stop error: {e}")

        threading.Thread(target=worker, daemon=True).start()
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
        """Poll the log queue and update console text widget."""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, msg)
                self.console_text.see(tk.END)
                self.console_text.config(state=tk.DISABLED)
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
                            "Â© 2026 All Rights Reserved")

    def on_close(self):
        self.on_disconnect()
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MiggyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()

