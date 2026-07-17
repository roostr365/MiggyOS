import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import time
import json
from datetime import datetime

from Miggy import Miggy
from AIMiggyController import AIMiggy


class ConsoleRedirector:
    """Redirects stdout/stderr to the GUI console."""
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
        self.root.title("MiggyOS – Autonomous Control")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # State
        self.miggy = None
        self.aimiggy = AIMiggy()
        self.is_connected = False
        self.audio_listening = False
        self.audio_thread = None
        self.running_operation = False
        self.log_queue = queue.Queue()
        self.after_id = None

        self.build_ui()
        self.setup_statusbar()

        # Redirect stdout/stderr to console
        sys.stdout = ConsoleRedirector(self.console_text, self.log_queue)
        sys.stderr = ConsoleRedirector(self.console_text, self.log_queue)

        self.poll_log_queue()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def build_ui(self):
        # Main paned window: left = log, right = controls
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Log area
        self.log_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.log_frame, weight=3)

        # Right: Controls
        self.ctrl_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.ctrl_frame, weight=1)

        # --- Log area ---
        ttk.Label(self.log_frame, text="Event Log", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.console_text = scrolledtext.ScrolledText(
            self.log_frame, font=("Courier New", 10), bg="black", fg="white"
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, "MiggyOS Control Center ready.\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

        # Clear log button
        ttk.Button(self.log_frame, text="Clear Log", command=self.clear_console).pack(pady=5)

        # --- Controls ---
        # Connection
        conn_frame = ttk.LabelFrame(self.ctrl_frame, text="Connection", padding="5")
        conn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(conn_frame, text="Interface:").grid(row=0, column=0, sticky=tk.W)
        self.interface_var = tk.StringVar(value="eth0")
        ttk.Entry(conn_frame, textvariable=self.interface_var, width=12).grid(row=0, column=1, padx=5)
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.on_connect)
        self.connect_btn.grid(row=0, column=2, padx=2)
        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.on_disconnect, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=3, padx=2)
        self.status_label = ttk.Label(conn_frame, text="● Offline", foreground="red")
        self.status_label.grid(row=0, column=4, padx=5)

        # Audio
        audio_frame = ttk.LabelFrame(self.ctrl_frame, text="Audio Control", padding="5")
        audio_frame.pack(fill=tk.X, pady=5)

        self.listen_btn = ttk.Button(audio_frame, text="🎤 Start Listening", command=self.toggle_audio)
        self.listen_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(audio_frame, text="Clear Buffer", command=self.clear_audio_buffer).pack(side=tk.LEFT, padx=5)
        self.audio_status = ttk.Label(audio_frame, text="Idle", foreground="gray")
        self.audio_status.pack(side=tk.LEFT, padx=10)

        # Manual fallback: text command
        manual_frame = ttk.LabelFrame(self.ctrl_frame, text="Manual Command", padding="5")
        manual_frame.pack(fill=tk.X, pady=5)

        self.manual_entry = ttk.Entry(manual_frame)
        self.manual_entry.pack(fill=tk.X, pady=2)
        ttk.Button(manual_frame, text="Send to AI", command=self.on_manual_send).pack(pady=2)

        # Fallback: move/rotate/special (compact)
        quick_frame = ttk.LabelFrame(self.ctrl_frame, text="Quick Actions", padding="5")
        quick_frame.pack(fill=tk.X, pady=5)

        # Move
        move_sub = ttk.Frame(quick_frame)
        move_sub.pack(fill=tk.X, pady=2)
        ttk.Label(move_sub, text="Dist:").pack(side=tk.LEFT)
        self.dist_entry = ttk.Entry(move_sub, width=6)
        self.dist_entry.insert(0, "1.0")
        self.dist_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(move_sub, text="Speed:").pack(side=tk.LEFT)
        self.speed_entry = ttk.Entry(move_sub, width=6)
        self.speed_entry.insert(0, "0.5")
        self.speed_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(move_sub, text="Fwd", command=lambda: self.manual_move(float(self.dist_entry.get()), float(self.speed_entry.get()))).pack(side=tk.LEFT, padx=2)
        ttk.Button(move_sub, text="Bwd", command=lambda: self.manual_move(-float(self.dist_entry.get()), float(self.speed_entry.get()))).pack(side=tk.LEFT, padx=2)

        # Rotate
        rot_sub = ttk.Frame(quick_frame)
        rot_sub.pack(fill=tk.X, pady=2)
        ttk.Label(rot_sub, text="Angle°:").pack(side=tk.LEFT)
        self.angle_entry = ttk.Entry(rot_sub, width=6)
        self.angle_entry.insert(0, "90")
        self.angle_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(rot_sub, text="Speed:").pack(side=tk.LEFT)
        self.rot_speed_entry = ttk.Entry(rot_sub, width=6)
        self.rot_speed_entry.insert(0, "1.0")
        self.rot_speed_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(rot_sub, text="Left", command=lambda: self.manual_rotate(math.radians(float(self.angle_entry.get())), float(self.rot_speed_entry.get()))).pack(side=tk.LEFT, padx=2)
        ttk.Button(rot_sub, text="Right", command=lambda: self.manual_rotate(-math.radians(float(self.angle_entry.get())), -float(self.rot_speed_entry.get()))).pack(side=tk.LEFT, padx=2)

        # Special action
        sp_sub = ttk.Frame(quick_frame)
        sp_sub.pack(fill=tk.X, pady=2)
        self.arm_action_var = tk.StringVar()
        actions = ["shake hand", "high five", "hug", "high wave", "clap", "face wave",
                   "left kiss", "heart", "right heart", "hands up", "x-ray", "right hand up",
                   "reject", "right kiss", "two-hand kiss"]
        self.arm_combo = ttk.Combobox(sp_sub, textvariable=self.arm_action_var, values=actions, state="readonly", width=12)
        self.arm_combo.current(0)
        self.arm_combo.pack(side=tk.LEFT, padx=2)
        ttk.Button(sp_sub, text="Execute Arm", command=self.manual_arm_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(sp_sub, text="Release", command=self.manual_release_arm).pack(side=tk.LEFT, padx=2)

        # Speech
        speech_frame = ttk.LabelFrame(self.ctrl_frame, text="Speech", padding="5")
        speech_frame.pack(fill=tk.X, pady=5)
        self.speech_entry = ttk.Entry(speech_frame)
        self.speech_entry.pack(fill=tk.X, pady=2)
        lang_frame = ttk.Frame(speech_frame)
        lang_frame.pack(fill=tk.X)
        self.speech_lang_var = tk.StringVar(value="english")
        ttk.Radiobutton(lang_frame, text="English", variable=self.speech_lang_var, value="english").pack(side=tk.LEFT)
        ttk.Radiobutton(lang_frame, text="Chinese", variable=self.speech_lang_var, value="chinese").pack(side=tk.LEFT)
        ttk.Button(speech_frame, text="Say", command=self.manual_say).pack(pady=2)

        # Emergency stop – always visible at bottom
        self.emergency_btn = ttk.Button(
            self.ctrl_frame, text="🛑 EMERGENCY STOP",
            command=self.emergency_stop,
            style="Emergency.TButton"
        )
        self.emergency_btn.pack(fill=tk.X, pady=10)

        style = ttk.Style()
        style.configure("Emergency.TButton", foreground="white", background="red", font=('Arial', 12, 'bold'))
        style.configure("Listening.TButton", foreground="white", background="green", font=('Arial', 10, 'bold'))

    def setup_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {msg}\n")

    def poll_log_queue(self):
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

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def on_connect(self):
        if self.is_connected:
            return
        interface = self.interface_var.get().strip()
        if not interface:
            messagebox.showerror("Error", "Interface required.")
            return
        try:
            self.statusbar.config(text="Connecting...")
            self.miggy = Miggy(interface)
            self.is_connected = True
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.status_label.config(text="● Online", foreground="green")
            self.statusbar.config(text=f"Connected to {interface}")
            self.log(f"Connected to {interface}")
            self.listen_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.log(f"Connection failed: {e}")

    def on_disconnect(self):
        if self.audio_listening:
            self.stop_audio()
        if self.is_connected and self.miggy:
            try:
                self.miggy.stop()
            except:
                pass
        self.is_connected = False
        self.miggy = None
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Offline", foreground="red")
        self.statusbar.config(text="Disconnected")
        self.log("Disconnected")
        self.listen_btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------
    def toggle_audio(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Connect first.")
            return
        if not self.audio_listening:
            self.start_audio()
        else:
            self.stop_audio()

    def start_audio(self):
        self.audio_listening = True
        self.listen_btn.config(text="⏹ Stop Listening", style="Listening.TButton")
        self.audio_status.config(text="Listening...", foreground="green")
        self.log("Audio listening started")
        self.miggy.clear_audio()
        self.audio_thread = threading.Thread(target=self.audio_loop, daemon=True)
        self.audio_thread.start()

    def stop_audio(self):
        self.audio_listening = False
        self.listen_btn.config(text="🎤 Start Listening", style="TButton")
        self.audio_status.config(text="Idle", foreground="gray")
        self.log("Audio listening stopped")
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=0.5)

    def audio_loop(self):
        while self.audio_listening:
            try:
                cmd = self.miggy.check_audio()
                if cmd is not None:
                    self.root.after(0, self.process_audio_command, cmd)
                time.sleep(0.3)
            except Exception as e:
                self.log(f"Audio loop error: {e}")
                break

    def process_audio_command(self, cmd):
        self.log(f"🎤 Audio: {cmd}")
        # Let AI generate code
        try:
            response = self.aimiggy.askAIMiggy(cmd)
            code = response.output_text.strip()
            self.log(f"🤖 AI generated code:\n{code}")
            # Execute automatically (or ask for confirmation? We'll auto-run for now)
            self.run_ai_code(code)
        except Exception as e:
            self.log(f"AI error: {e}")

    def clear_audio_buffer(self):
        if self.is_connected:
            self.miggy.clear_audio()
            self.log("Audio buffer cleared")

    # ------------------------------------------------------------------
    # AI execution
    # ------------------------------------------------------------------
    def run_ai_code(self, code):
        if not self.is_connected:
            self.log("Not connected, cannot execute.")
            return
        if not code:
            return
        self.run_in_thread(self.execute_code_thread, code)

    def execute_code_thread(self, code):
        try:
            exec_globals = {"miggy": self.miggy, "math": math, "time": time}
            exec(code, exec_globals)
            self.root.after(0, lambda: self.log("✅ Code executed successfully."))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Execution error: {e}"))

    # ------------------------------------------------------------------
    # Manual fallback
    # ------------------------------------------------------------------
    def on_manual_send(self):
        query = self.manual_entry.get().strip()
        if not query:
            return
        self.log(f"Manual command: {query}")
        try:
            response = self.aimiggy.askAIMiggy(query)
            code = response.output_text.strip()
            self.log(f"AI generated code:\n{code}")
            self.run_ai_code(code)
        except Exception as e:
            self.log(f"AI error: {e}")

    def manual_move(self, dist, speed):
        if not self.is_connected:
            return
        self.log(f"Manual move: dist={dist}, speed={speed}")
        self.run_in_thread(self.miggy.move_dist, dist, speed)

    def manual_rotate(self, angle, speed):
        if not self.is_connected:
            return
        self.log(f"Manual rotate: angle={angle}, speed={speed}")
        self.run_in_thread(self.miggy.rotate_angle, angle, speed)

    def manual_arm_action(self):
        if not self.is_connected:
            return
        action = self.arm_action_var.get()
        self.log(f"Manual arm: {action}")
        self.run_in_thread(self.miggy.run_special, action)

    def manual_release_arm(self):
        if not self.is_connected:
            return
        self.log("Manual release arm")
        self.run_in_thread(self.miggy.release_arm)

    def manual_say(self):
        if not self.is_connected:
            return
        text = self.speech_entry.get().strip()
        if not text:
            return
        lang = self.speech_lang_var.get()
        self.log(f"Manual speech: '{text}' ({lang})")
        self.run_in_thread(self.miggy.say, text, lang)

    def emergency_stop(self):
        if not self.is_connected:
            return
        self.log("🚨 EMERGENCY STOP ACTIVATED")
        self.run_in_thread(self.miggy.stop)

    # ------------------------------------------------------------------
    # Threading helper
    # ------------------------------------------------------------------
    def run_in_thread(self, func, *args, **kwargs):
        if self.running_operation:
            self.log("Operation already running, skipping.")
            return
        self.running_operation = True
        self.statusbar.config(text="Busy...")
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Operation error: {e}"))
            finally:
                self.running_operation = False
                self.root.after(0, lambda: self.statusbar.config(text="Ready"))
        threading.Thread(target=wrapper, daemon=True).start()

    # ------------------------------------------------------------------
    # Launch
    # ------------------------------------------------------------------
    @staticmethod
    def launch():
        root = tk.Tk()
        app = MiggyGUI(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()

    def on_close(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.on_disconnect()
        self.root.quit()


if __name__ == "__main__":
    MiggyGUI.launch()
