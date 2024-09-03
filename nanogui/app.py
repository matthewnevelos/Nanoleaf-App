import tkinter as tk
from nanogui.toolbar import ToolSideBar
from nanogui.painting import Painting

class App(tk.Tk):
    """
    Main window for UofC Nanoleaf Editor
    """
    def __init__(self) -> None:
        super().__init__()
        self.title("UofC Nanoleaf Editor")

        # Set window size and center it
        self.geometry(self.center_window(800, 600))

        self.toolbar = ToolSideBar(self)
        self.toolbar.pack(fill='y', side='left', expand=False)

        self.canvas_frame = Painting(self)
        self.canvas_frame.pack(fill="both", side="right", expand=True)

    def center_window(self, width: int, height: int) -> str:
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - width) // 2, (sh - height) // 2
        return f'{width}x{height}+{x}+{y}'