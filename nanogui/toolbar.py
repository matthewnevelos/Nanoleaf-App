import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk


class ToolSideBar(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, width=150)

        # Initlize variables
        # Tools
        self.icons = {}
        self.buttons = {}
        self.selected_tool = None
        # Options
        self.options = {}
        self.colour1 = "#FF69B4"
        self.colour_hist = {}

        # Create tools and colour buttons
        self.create_tool_options()
        self.create_tools()

        # Initially select pen
        self.select_tool(None)

    def create_tools(self) -> None:
        icons = ["blend", "bucket", "dropper", "marker", "pencil", "spray"]
        for i, icon in enumerate(icons):
            try:
                image = Image.open(f"img/icons/{icon}.png").resize((50, 50))
                photo = ImageTk.PhotoImage(image)
                button = tk.Button(self, image=photo, command=lambda icon=icon: self.select_tool(icon), relief="groove", borderwidth=2)
                button.grid(row=i // 2 + 2, column=i % 2, padx=5, pady=5)  # Adjust row to start below colour buttons
                self.icons[icon] = photo  # Store reference
                self.buttons[icon] = button
            except FileNotFoundError:
                print(f"Icon {icon}.png not found in the 'img/icons/' directory.")

    def create_tool_options(self) -> None:
        """
        Create button to select colours, and scale to change radius of brush
        """

        def choose_colour1() -> None:
            newcolour = colorchooser.askcolor(title="Choose Colour 1")[1]
            if newcolour:
                self.colour1 = newcolour
                self.colour1_button.config(bg=self.colour1)

            dict_copy = self.colour_hist.copy()
            for x in range(len(self.colour_hist)-1, 0, -1):
                self.colour_hist[x][1] = dict_copy[x-1][1] 

            self.colour_hist[0][1] = newcolour
            self.update_colours()

        def make_col_hist_butts() -> None:
            colour_hist = ["#FF1493", "#FFD700", "#7CFC00", "#00BFFF", "#0000EE", "#A020F0"]
            col_hist_frame = tk.Frame(self, bg="black", borderwidth=1, relief="flat")
            col_hist_frame.grid(row=1, column=0, pady=5, padx=3, columnspan=2)
            for i, colour in enumerate(colour_hist):
                button = tk.Button(col_hist_frame, bg=colour_hist[i], width=2, height=1,command=lambda index=i: self.choose_colour(index), relief="flat" )
                button.grid(row=0, column=i)
                self.colour_hist[i] = [button, colour]

        # Colour picker
        col_frame = tk.Frame(self, bg="black", borderwidth=1, relief="flat")
        col_frame.grid(row=0, column=0, pady=5, columnspan=2)
        self.colour1_button = tk.Button(col_frame, bg=self.colour1, width=15, height=2, command=choose_colour1, borderwidth=5, border=5, relief="flat")
        self.colour1_button.pack()

        # Historic colour buttons
        make_col_hist_butts()

        # Undo/redo buttons
        image = Image.open("img/icons/undo.png").resize((40, 40))
        self.undo_img = ImageTk.PhotoImage(image)
        self.redo_img = ImageTk.PhotoImage(image.transpose(Image.FLIP_LEFT_RIGHT))
        self.undo_butt = tk.Button(self, image=self.undo_img, command=self.undo, relief="groove", borderwidth=2)
        self.redo_butt = tk.Button(self, image=self.redo_img, command=self.redo, relief="groove", borderwidth=2)
        self.undo_butt.grid(row=9, column=0, padx=5, pady=5)
        self.redo_butt.grid(row=9, column=1, padx=5, pady=5)

        # Radius, tolerance, strnegth
        # {tool: [max val, resolution], ...}
        op_param = {"radius":[4, 1], "tolerance":[100, 5], "strength":[1, 0.01]}
        for i, option in enumerate(op_param):
            frame = tk.Frame(self, bg="black", borderwidth=1, relief="flat")
            frame.grid(row=5+i, column=0, columnspan=2, pady=(19, 0))
            slider = tk.Scale(frame, from_=0, to=op_param[option][0], orient=tk.HORIZONTAL, label=option, resolution=op_param[option][1])
            slider.pack()
            self.options[option] = slider

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool

        enabled_options = {"blend": ["radius", "strength"],
                           "bucket": ["tolerance"],
                           "dropper": [],
                           "marker": ["radius", "strength"],
                           "pencil": ["radius"],
                           "spray": ["radius", "strength"],
                           None: []}
        
        for option in self.options:
            if option in enabled_options[tool]:
                self.options[option].config(state=tk.NORMAL, bg="SystemButtonFace")
            else:
                self.options[option].config(state=tk.DISABLED, bg="gray50")

        # Correct access to canvas_frame
        if hasattr(self.master, 'canvas_frame'):
            self.master.canvas_frame.set_cursor(tool)

        for t, button in self.buttons.items():
            if t == tool:
                button.config(bg="green")
            else:
                button.config(bg="SystemButtonFace")
    
    def choose_colour(self, index: int):
        """
        change active colour from one in history
        """
        colour = self.colour_hist[index][1]
        self.colour1_button.config(bg=colour)
        self.colour1=colour
    
    def update_colours(self):
        for x in self.colour_hist:
            self.colour_hist[x][0].config(bg=self.colour_hist[x][1])

    def undo(self):
        self.master.canvas_frame.nanolist.undo()

    def redo(self):
        self.master.canvas_frame.nanolist.redo()