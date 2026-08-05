"""
BPhO Shared Theme Configuration
================================
All Task files import from this module to get the active colour theme.
The launcher (main.py) sets the BPHO_THEME environment variable before
spawning each task subprocess, so the plots always match the GUI.
"""

import os
import matplotlib.pyplot as plt


# ── Theme definitions ─────────────────────────────────────────────
# Each theme maps to: (mpl_style, accent, data, accent2, muted, bg)

THEMES = {
    "Grayscale Standard": {
        "mpl_style": "dark_background",
        "ACCENT":  "#ffffff",
        "DATA":    "#e0e0e0",
        "PINK":    "#cccccc",
        "ORANGE":  "#aaaaaa",
        "MUTED":   "#888888",
        "WARN":    "#aaaaaa",
    },
    "Terminal Green": {
        "mpl_style": "dark_background",
        "ACCENT":  "#00ff41",
        "DATA":    "#33ff33",
        "PINK":    "#ff6ec7",
        "ORANGE":  "#ff9100",
        "MUTED":   "#227722",
        "WARN":    "#674700",
    },
    "Deep Sea Blue": {
        "mpl_style": "dark_background",
        "ACCENT":  "#39cccc",
        "DATA":    "#7fdbff",
        "PINK":    "#01ff70",
        "ORANGE":  "#ff851b",
        "MUTED":   "#005b9f",
        "WARN":    "#ff851b",
    },
    "Neon Synthesis": {
        "mpl_style": "dark_background",
        "ACCENT":  "#ff00ff",
        "DATA":    "#00ffcc",
        "PINK":    "#ff00ff",
        "ORANGE":  "#ff0055",
        "MUTED":   "#a32cc4",
        "WARN":    "#ff0055",
    },
    "Solarized Dark": {
        "mpl_style": "dark_background",
        "ACCENT":  "#b58900",
        "DATA":    "#839496",
        "PINK":    "#2aa198",
        "ORANGE":  "#dc322f",
        "MUTED":   "#586e75",
        "WARN":    "#dc322f",
    },
    "Pastel Blossom": {
        "mpl_style": "default",
        "ACCENT":  "#ff69b4",
        "DATA":    "#5c405c",
        "PINK":    "#ffb6c1",
        "ORANGE":  "#ff1493",
        "MUTED":   "#b38cb3",
        "WARN":    "#ff1493",
    },
    "Arctic Frost": {
        "mpl_style": "default",
        "ACCENT":  "#00ced1",
        "DATA":    "#2f4f4f",
        "PINK":    "#4682b4",
        "ORANGE":  "#ff4500",
        "MUTED":   "#778899",
        "WARN":    "#ff4500",
    },
    "Crimson Velvet": {
        "mpl_style": "dark_background",
        "ACCENT":  "#ff4d4d",
        "DATA":    "#f5e6e6",
        "PINK":    "#ff9999",
        "ORANGE":  "#ffb300",
        "MUTED":   "#a36666",
        "WARN":    "#ffb300",
    },
    "Autumn Harvest": {
        "mpl_style": "dark_background",
        "ACCENT":  "#ff8c00",
        "DATA":    "#fae8d4",
        "PINK":    "#ffd700",
        "ORANGE":  "#ff4500",
        "MUTED":   "#a88965",
        "WARN":    "#ff4500",
    },
    "Midnight Obsidian": {
        "mpl_style": "dark_background",
        "ACCENT":  "#5e81ac",
        "DATA":    "#d4d4d4",
        "PINK":    "#81a1c1",
        "ORANGE":  "#bf616a",
        "MUTED":   "#666666",
        "WARN":    "#bf616a",
    },
    "Royal Amethyst": {
        "mpl_style": "dark_background",
        "ACCENT":  "#b366ff",
        "DATA":    "#e6d9f2",
        "PINK":    "#d9b3ff",
        "ORANGE":  "#ffb366",
        "MUTED":   "#8e73a6",
        "WARN":    "#ffb366",
    },
    "Forest Canopy": {
        "mpl_style": "dark_background",
        "ACCENT":  "#4dff88",
        "DATA":    "#d9f2e3",
        "PINK":    "#80ffaa",
        "ORANGE":  "#ffcc66",
        "MUTED":   "#68997a",
        "WARN":    "#ffcc66",
    },
    "Corporate Light": {
        "mpl_style": "default",
        "ACCENT":  "#0056b3",
        "DATA":    "#333333",
        "PINK":    "#007bff",
        "ORANGE":  "#dc3545",
        "MUTED":   "#777777",
        "WARN":    "#dc3545",
    },
    "Sunset Glow": {
        "mpl_style": "dark_background",
        "ACCENT":  "#ff758c",
        "DATA":    "#ffe6f2",
        "PINK":    "#ff7eb3",
        "ORANGE":  "#ffd700",
        "MUTED":   "#b3809e",
        "WARN":    "#ffd700",
    },
    "Desert Sand": {
        "mpl_style": "default",
        "ACCENT":  "#d4a373",
        "DATA":    "#4a4235",
        "PINK":    "#bc4749",
        "ORANGE":  "#bc4749",
        "MUTED":   "#8c816d",
        "WARN":    "#bc4749",
    },
}


def apply_theme(theme_name=None):
    """Apply the given theme to matplotlib. Reads BPHO_THEME env var if not given."""
    if theme_name is None:
        theme_name = os.environ.get("BPHO_THEME", "Grayscale Standard")

    t = THEMES.get(theme_name, THEMES["Grayscale Standard"])

    plt.style.use(t["mpl_style"])

    return {
        "ACCENT": t["ACCENT"],
        "DATA":   t["DATA"],
        "PINK":   t["PINK"],
        "ORANGE": t["ORANGE"],
        "MUTED":  t["MUTED"],
        "WARN":   t["WARN"],
    }