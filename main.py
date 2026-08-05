"""
BPhO Computational Physics 2026 — GUI Task Launcher
====================================================
A tkinter-based graphical interface to select and run simulation tasks.
Improved with non-blocking subprocesses and background threading.
"""

import subprocess
import sys
import os
import ctypes
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json

# Enable high-DPI awareness on Windows to prevent blurry text
if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except AttributeError:
        pass # Fallback for older Windows versions

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "bpho_config.json")

TASKS = [
    ("Task 1",  "Random Walk Model",                             "Task1.py",
     "SUMMARY: Simulation of a 2D random walk.\n\nDETAIL: Create a model of a random walk consisting of N steps of a fixed size s. At each step, the particle moves in a completely random direction chosen from a uniform distribution between 0 and 2π radians. This serves as a foundational model for stochastic processes."),
    ("Task 2",  "Brownian Motion Simulation",                    "Task2.py",
     "SUMMARY: 2D kinematic simulation of Brownian motion.\n\nDETAIL: Model N small particles undergoing random walks that collide with a much larger particle. The simulation uses conservation of momentum to compute collisions between the small particles and the large one, culminating in an animated visualization of the system's subsequent motion."),
    ("Task 3",  "Planck & Einstein Thermal Models",              "Task3.py",
     "SUMMARY: Visualise Black Body radiation and Einstein's heat capacity.\n\nDETAIL: Plot the Planck 'Black Body radiation' spectrum B(λ, T) for multiple temperatures (e.g., 4000K, 5000K, 6000K). Additionally, plot Einstein's model of molar heat capacity of solids against temperature for various atomic crystals (such as gold, copper, iron)."),
    ("Task 4",  "Photoelectric Effect Simulator",                "Task4.py",
     "SUMMARY: Interactive photoelectric effect and stopping voltage analysis.\n\nDETAIL: Plot photoelectron stopping voltage against the frequency (or in-vacuum wavelength) of incident photons for various metals. Extended as an interactive animated app allowing users to adjust variables like work function and applied voltage to observe the emissions."),
    ("Task 5",  "Bohr Model & Hydrogen Emissions",               "Task5.py",
     "SUMMARY: Spectral lines of a hydrogenic atom.\n\nDETAIL: Generate a graph mapping photon energy against wavelength for photon emissions from hydrogen atoms. This models the transitions between electron energy levels according to the Bohr model, highlighting specific emission series such as Lyman, Balmer, Paschen, Brackett, and Pfund."),
    ("Task 6",  "Electron Diffraction Analysis",                 "Task6.py",
     "SUMMARY: Model of 'electron wave' rings on a phosphor screen.\n\nDETAIL: Build a computer model showing electron diffraction rings, with accelerating voltage V (1kV to 5kV) as a variable. Assuming graphite atomic layer spacings, the app plots the rings and verifies the relationship by generating a 1/√V vs sin(½φ) straight-line graph."),
    ("Task 7",  "Particle-in-a-Box & Uncertainty",               "Task7.py",
     "SUMMARY: Schrödinger equation solutions for a 1D potential well.\n\nDETAIL: Plot the energy levels versus quantum number, and the probability densities (|ψ|²) versus displacement x for a particle trapped in a box. As an extension, the model computationally verifies that the particle obeys the Heisenberg Uncertainty Principle (Δx·Δp ≥ ½ħ)."),
    ("Task 8",  "Quantum Cryptography Calculator",               "Task8.py",
     "SUMMARY: Visual calculator for entangled photon detection.\n\nDETAIL: Create an interactive visual tool to compare classical and quantum mismatch probabilities. It models the detection of polarized entangled photons across two detectors, allowing users to adjust polarization axes to see how quantum mechanics predicts different probabilities."),
    ("Task 9",  "Compton Scattering Kinematics",                 "Task9.py",
     "SUMMARY: Analysis of X-ray photon scattering off free electrons.\n\nDETAIL: Model the kinematics of Compton scattering. The application plots the fractional wavelength shift (Δλ/λ), the electron recoil speed (v/c), and the electron recoil angle (φ) as functions of the photon scattering angle (θ) for an incident X-ray."),
    ("Task 10", "Hydrogenic Orbitals 2D & 3D",                   "Task10.py",
     "SUMMARY: Volumetric and slice visualizations of atomic orbitals.\n\nDETAIL: Plot detailed 2D slices (e.g., z=0 plane) and 3D volumetric scatter plots of the probability density (|ψ|²) for an electron in a hydrogenic atom. The visualization is generated using provided solutions to the Schrödinger Equation based on quantum numbers (n, l, m)."),
]

THEMES = {
    "Grayscale Standard": {
        "BG": "#1e1e1e", "FG": "#e0e0e0", "DIM_FG": "#888888",
        "ACCENT": "#ffffff", "ACCENT2": "#cccccc", "BUTTON_BG": "#2d2d2d",
        "HOVER_BG": "#444444", "CARD_BG": "#252525", "WARN_FG": "#aaaaaa", "TEXT_ON_ACCENT": "#000000"
    },
    "Terminal Green": {
        "BG": "#0a0a0a", "FG": "#33ff33", "DIM_FG": "#227722",
        "ACCENT": "#00ff41", "ACCENT2": "#39ff14", "BUTTON_BG": "#1a1a1a",
        "HOVER_BG": "#0d330d", "CARD_BG": "#111111", "WARN_FG": "#674700", "TEXT_ON_ACCENT": "#000000"
    },
    "Deep Sea Blue": {
        "BG": "#001f3f", "FG": "#7fdbff", "DIM_FG": "#005b9f",
        "ACCENT": "#39cccc", "ACCENT2": "#01ff70", "BUTTON_BG": "#00172d",
        "HOVER_BG": "#003366", "CARD_BG": "#002b5e", "WARN_FG": "#ff851b", "TEXT_ON_ACCENT": "#000000"
    },
    "Neon Synthesis": {
        "BG": "#0d0221", "FG": "#00ffcc", "DIM_FG": "#a32cc4",
        "ACCENT": "#ff00ff", "ACCENT2": "#00ffcc", "BUTTON_BG": "#1c0b43",
        "HOVER_BG": "#2d1b54", "CARD_BG": "#160539", "WARN_FG": "#ff0055", "TEXT_ON_ACCENT": "#ffffff"
    },
    "Solarized Dark": {
        "BG": "#002b36", "FG": "#839496", "DIM_FG": "#586e75",
        "ACCENT": "#b58900", "ACCENT2": "#2aa198", "BUTTON_BG": "#073642",
        "HOVER_BG": "#586e75", "CARD_BG": "#073642", "WARN_FG": "#dc322f", "TEXT_ON_ACCENT": "#002b36"
    },
    "Pastel Blossom": {
        "BG": "#fff0f5", "FG": "#5c405c", "DIM_FG": "#b38cb3",
        "ACCENT": "#ff69b4", "ACCENT2": "#ffb6c1", "BUTTON_BG": "#ffe4e1",
        "HOVER_BG": "#ffc0cb", "CARD_BG": "#ffffff", "WARN_FG": "#ff1493", "TEXT_ON_ACCENT": "#ffffff"
    },
    "Arctic Frost": {
        "BG": "#f0f8ff", "FG": "#2f4f4f", "DIM_FG": "#778899",
        "ACCENT": "#00ced1", "ACCENT2": "#4682b4", "BUTTON_BG": "#e0ffff",
        "HOVER_BG": "#afeeee", "CARD_BG": "#ffffff", "WARN_FG": "#ff4500", "TEXT_ON_ACCENT": "#ffffff"
    },
    "Crimson Velvet": {
        "BG": "#2b0a0a", "FG": "#f5e6e6", "DIM_FG": "#a36666",
        "ACCENT": "#ff4d4d", "ACCENT2": "#ff9999", "BUTTON_BG": "#4d1a1a",
        "HOVER_BG": "#802b2b", "CARD_BG": "#3d0f0f", "WARN_FG": "#ffb300", "TEXT_ON_ACCENT": "#2b0a0a"
    },
    "Autumn Harvest": {
        "BG": "#2e2013", "FG": "#fae8d4", "DIM_FG": "#a88965",
        "ACCENT": "#ff8c00", "ACCENT2": "#ffd700", "BUTTON_BG": "#4a3520",
        "HOVER_BG": "#73512e", "CARD_BG": "#3d2a17", "WARN_FG": "#ff4500", "TEXT_ON_ACCENT": "#2e2013"
    },
    "Midnight Obsidian": {
        "BG": "#050505", "FG": "#d4d4d4", "DIM_FG": "#666666",
        "ACCENT": "#5e81ac", "ACCENT2": "#81a1c1", "BUTTON_BG": "#1a1a1a",
        "HOVER_BG": "#2b2b2b", "CARD_BG": "#0f0f0f", "WARN_FG": "#bf616a", "TEXT_ON_ACCENT": "#050505"
    },
    "Royal Amethyst": {
        "BG": "#1f0f29", "FG": "#e6d9f2", "DIM_FG": "#8e73a6",
        "ACCENT": "#b366ff", "ACCENT2": "#d9b3ff", "BUTTON_BG": "#331a40",
        "HOVER_BG": "#4d2666", "CARD_BG": "#29143d", "WARN_FG": "#ffb366", "TEXT_ON_ACCENT": "#1f0f29"
    },
    "Forest Canopy": {
        "BG": "#0f2115", "FG": "#d9f2e3", "DIM_FG": "#68997a",
        "ACCENT": "#4dff88", "ACCENT2": "#80ffaa", "BUTTON_BG": "#1a3322",
        "HOVER_BG": "#264d33", "CARD_BG": "#142b1c", "WARN_FG": "#ffcc66", "TEXT_ON_ACCENT": "#0f2115"
    },
    "Corporate Light": {
        "BG": "#f4f7f6", "FG": "#333333", "DIM_FG": "#777777",
        "ACCENT": "#0056b3", "ACCENT2": "#007bff", "BUTTON_BG": "#e9ecef",
        "HOVER_BG": "#ced4da", "CARD_BG": "#ffffff", "WARN_FG": "#dc3545", "TEXT_ON_ACCENT": "#ffffff"
    },
    "Sunset Glow": {
        "BG": "#2b182e", "FG": "#ffe6f2", "DIM_FG": "#b3809e",
        "ACCENT": "#ff758c", "ACCENT2": "#ff7eb3", "BUTTON_BG": "#402345",
        "HOVER_BG": "#593361", "CARD_BG": "#361e3a", "WARN_FG": "#ffd700", "TEXT_ON_ACCENT": "#2b182e"
    },
    "Desert Sand": {
        "BG": "#f5f0e6", "FG": "#4a4235", "DIM_FG": "#8c816d",
        "ACCENT": "#d4a373", "ACCENT2": "#bc4749", "BUTTON_BG": "#faedcd",
        "HOVER_BG": "#e3d5b8", "CARD_BG": "#ffffff", "WARN_FG": "#bc4749", "TEXT_ON_ACCENT": "#ffffff"
    }
}

class BPhOLauncher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BPhO Computational Physics 2026")
        self.geometry("780x620")
        self.resizable(True, True)

        # Handle clean exit and save theme
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load saved theme or default to Grayscale Standard
        initial_theme = "Grayscale Standard"
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    config_data = json.load(f)
                    saved = config_data.get("theme")
                    if saved in THEMES:
                        initial_theme = saved
            except Exception:
                pass

        # Lists to keep track of widgets for theme switching
        self._bg_widgets = []
        self._card_widgets = []
        self._dim_labels = []
        self._accent_labels = []
        self._accent2_labels = []
        self._std_buttons = []

        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        self._bg_widgets.extend([self, header])

        title = tk.Label(header, text="BPhO  Computational  Physics  2026", font=("Consolas", 16, "bold"))
        title.pack(anchor="w")
        self._accent_labels.append(title)

        subtitle = tk.Label(header, text="Select a simulation task to run  •  Made by Wiktor Jarawski & Nirbhay Saxena", font=("Consolas", 9))
        subtitle.pack(anchor="w", pady=(4, 0))
        self._dim_labels.append(subtitle)

        # Theme selector
        theme_frame = tk.Frame(header)
        theme_frame.place(relx=1.0, rely=0.0, anchor="ne")
        self._bg_widgets.append(theme_frame)

        theme_lbl = tk.Label(theme_frame, text="Theme:", font=("Consolas", 9))
        theme_lbl.pack(side=tk.LEFT, padx=(0, 5))
        self._dim_labels.append(theme_lbl)

        self.theme_var = tk.StringVar(value=initial_theme)
        self.theme_menu = tk.OptionMenu(theme_frame, self.theme_var, *THEMES.keys(), command=self._on_theme_change)
        self.theme_menu.config(highlightthickness=0, relief=tk.FLAT, font=("Consolas", 9), cursor="hand2")
        self.theme_menu.pack(side=tk.LEFT)

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        self._bg_widgets.append(main_frame)

        # left panel — task list
        left = tk.Frame(main_frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bg_widgets.append(left)

        tasks_lbl = tk.Label(left, text="Tasks", font=("Consolas", 10, "bold"))
        tasks_lbl.pack(anchor="w", pady=(0, 4))
        self._accent_labels.append(tasks_lbl)

        list_frame = tk.Frame(left, highlightthickness=0)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._card_widgets.append(list_frame)

        self.listbox = tk.Listbox(list_frame, font=("Consolas", 10), activestyle="none", borderwidth=0, highlightthickness=0, height=12)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        for short, name, _, _ in TASKS:
            self.listbox.insert(tk.END, f"  {short}  —  {name}")

        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self._run_selected())
        self.listbox.selection_set(0)

        # right panel — description (using tk.Text for dynamic resizing/wrapping)
        right = tk.Frame(main_frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(16, 0))
        self._bg_widgets.append(right)

        desc_title_lbl = tk.Label(right, text="Description", font=("Consolas", 10, "bold"))
        desc_title_lbl.pack(anchor="w", pady=(0, 4))
        self._accent2_labels.append(desc_title_lbl)

        # Dynamic Text widget that expands and wraps text automatically on window resize
        self.desc_text = tk.Text(right, font=("Consolas", 10), wrap=tk.WORD, relief=tk.FLAT, borderwidth=0, highlightthickness=0, padx=14, pady=14)
        self.desc_text.pack(fill=tk.BOTH, expand=True)
        self.desc_text.config(state=tk.DISABLED)
        self._card_widgets.append(self.desc_text)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        self._bg_widgets.append(btn_frame)

        self.run_btn = tk.Button(btn_frame, text="▶  Run Selected Task", font=("Consolas", 11, "bold"), relief=tk.FLAT, padx=24, pady=6, cursor="hand2", command=self._run_selected)
        self.run_btn.pack(side=tk.LEFT)

        self.run_all_btn = tk.Button(btn_frame, text="Run All", font=("Consolas", 9), relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=self._run_all)
        self.run_all_btn.pack(side=tk.LEFT, padx=(10, 0))
        self._std_buttons.append(self.run_all_btn)

        self.quit_btn = tk.Button(btn_frame, text="Quit", font=("Consolas", 9), relief=tk.FLAT, padx=12, pady=6, cursor="hand2", command=self.destroy)
        self.quit_btn.pack(side=tk.RIGHT)
        self._std_buttons.append(self.quit_btn)

        # ── status bar ───────────────────────────────────────
        self.status = tk.Label(self, text="Ready.", font=("Consolas", 9), anchor="w")
        self.status.pack(fill=tk.X, padx=24, pady=(0, 8))

        # Apply initial theme
        self._apply_theme(initial_theme)

        # load first description
        self.listbox.event_generate("<<ListboxSelect>>")

    def _on_theme_change(self, selected_theme):
        self._apply_theme(selected_theme)
        self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"theme": self.theme_var.get()}, f)
        except Exception as e:
            print(f"Failed to save configuration: {e}")

    def on_close(self):
        self.save_config()
        self.destroy()

    def _apply_theme(self, theme_name):
        t = THEMES[theme_name]

        for w in self._bg_widgets:
            w.configure(bg=t["BG"])

        for w in self._card_widgets:
            w.configure(bg=t["CARD_BG"])

        for lbl in self._accent_labels:
            lbl.configure(bg=t["BG"], fg=t["ACCENT"])

        for lbl in self._accent2_labels:
            lbl.configure(bg=t["BG"], fg=t["ACCENT2"])

        for lbl in self._dim_labels:
            lbl.configure(bg=t["BG"], fg=t["DIM_FG"])

        self.listbox.configure(bg=t["CARD_BG"], fg=t["FG"], selectbackground=t["ACCENT"], selectforeground=t["TEXT_ON_ACCENT"])
        self.desc_text.configure(bg=t["CARD_BG"], fg=t["FG"])

        self.run_btn.configure(bg=t["ACCENT"], fg=t["TEXT_ON_ACCENT"], activebackground=t["ACCENT2"], activeforeground=t["TEXT_ON_ACCENT"])

        for btn in self._std_buttons:
            fg_col = t["WARN_FG"] if btn == self.quit_btn else t["FG"]
            btn.configure(bg=t["BUTTON_BG"], fg=fg_col, activebackground=t["HOVER_BG"], activeforeground=t["FG"])

        self.theme_menu.config(bg=t["BUTTON_BG"], fg=t["FG"], activebackground=t["HOVER_BG"], activeforeground=t["FG"])
        self.theme_menu["menu"].config(bg=t["CARD_BG"], fg=t["FG"], activebackground=t["HOVER_BG"], activeforeground=t["FG"])

        self.status.configure(bg=t["BG"], fg=t["WARN_FG"])

    # ── events ───────────────────────────────────────────────

    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        desc_str = TASKS[idx][3]

        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", desc_str)
        self.desc_text.config(state=tk.DISABLED)

    def _run_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a task first.")
            return
        idx = sel[0]
        name, _, filename, _ = TASKS[idx]

        filepath = os.path.join(SCRIPT_DIR, filename)
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"File not found:\n{filepath}")
            return

        self.status.config(text=f"Launched: {name} (Running in background)")
        try:
            env = os.environ.copy()
            env["BPHO_THEME"] = self.theme_var.get()
            subprocess.Popen([sys.executable, filepath], cwd=SCRIPT_DIR, env=env)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run {filename}:\n{e}")
            self.status.config(text="Error.")

    def _run_all(self):
        if not messagebox.askokcancel("Run All",
                                      "This will sequentially open 8 Matplotlib windows.\n"
                                      "Close each one to proceed to the next task.\n\nContinue?"):
            return

        self.run_all_btn.config(state=tk.DISABLED)
        # Use a background thread so the sequential blocking doesn't freeze the GUI
        threading.Thread(target=self._run_all_thread, daemon=True).start()

    def _run_all_thread(self):
        for short, name, filename, _ in TASKS:
            filepath = os.path.join(SCRIPT_DIR, filename)
            if not os.path.exists(filepath):
                print(f"Skipping {filename} (Not found)")
                continue

            # Safely update GUI from the background thread using .after()
            self.after(0, lambda n=name: self.status.config(
                text=f"Running: {n} ... close the Matplotlib window to proceed."
            ))

            try:
                env = os.environ.copy()
                env["BPHO_THEME"] = self.theme_var.get()
                subprocess.run([sys.executable, filepath], cwd=SCRIPT_DIR, env=env)
            except Exception as e:
                print(f"Failed to run {filename}: {e}")

        self.after(0, lambda: self.status.config(text="Finished running all tasks."))
        self.after(0, lambda: self.run_all_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    app = BPhOLauncher()
    app.mainloop()
