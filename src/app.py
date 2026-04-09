from __future__ import annotations
import sys
import tkinter as tk
from gui.gui import DownloaderGUI

def main() -> None:
    root = tk.Tk()
    try:
        if sys.platform == "win32":
            root.tk.call("source", "sun-valley.tcl")
            root.tk.call("set_theme", "light")
    except Exception:
        pass
    app = DownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()