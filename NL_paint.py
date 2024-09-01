import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from nanolist import NanoList
from random import random
from math import sin

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
        self.colour1 = "hot pink"

        # Create tools and colour buttons
        self.create_tool_options()
        self.create_tools()

        # Initially select pen
        self.select_tool("pencil")

    def create_tools(self) -> None:
        icons = ["blend", "bucket", "dropper", "marker", "pencil", "spray"]
        for i, icon in enumerate(icons):
            try:
                image = Image.open(f"icons/{icon}.png").resize((50, 50))
                photo = ImageTk.PhotoImage(image)
                button = tk.Button(self, image=photo, command=lambda icon=icon: self.select_tool(icon), relief="groove", borderwidth=2)
                button.grid(row=i // 2 + 2, column=i % 2, padx=5, pady=5)  # Adjust row to start below colour buttons
                self.icons[icon] = photo  # Store reference
                self.buttons[icon] = button
            except FileNotFoundError:
                print(f"Icon {icon}.png not found in the 'icons/' directory.")

    def create_tool_options(self) -> None:
        """
        Create button to select colours, and scale to change radius of brush
        """

        def choose_colour1() -> None:
            colour = colorchooser.askcolor(title="Choose Colour 1")[1]
            if colour:
                self.colour1 = colour
                self.colour1_button.config(bg=self.colour1)

        # Colour picker
        self.colour1_frame = tk.Frame(self, bg="black", borderwidth=1, relief="flat")
        self.colour1_frame.grid(row=0, column=0, pady=5, columnspan=2)
        self.colour1_button = tk.Button(self.colour1_frame, bg=self.colour1, width=15, height=2, command=choose_colour1, borderwidth=5, border=5, relief="flat")
        self.colour1_button.pack()

        # Radius, tolerance, strnegth
        # {tool: [max val, resolution], ...}
        op_param = {"radius":[4, 1], "tolerance":[100, 5], "strength":[1, 0.01]}
        for i, option in enumerate(op_param):
            frame = tk.Frame(self, bg="black", borderwidth=1, relief="flat")
            frame.grid(row=5+i, column=0, columnspan=2, pady=5)
            slider = tk.Scale(frame, from_=0, to=op_param[option][0], orient=tk.HORIZONTAL, label=option, resolution=op_param[option][1])
            slider.pack()
            self.options[option] = slider

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool

        enabled_options = {"blend":["radius", "strength"],
                           "bucket":["tolerance"],
                           "dropper":[],
                           "marker":["radius", "strength"],
                           "pencil":["radius"],
                           "spray":["radius", "strength"]}
        
        for option in self.options:
            self.options[option].set(0)
            if option in enabled_options[tool]:
                self.options[option].config(state=tk.NORMAL, bg="SystemButtonFace")
            else:
                self.options[option].config(state=tk.DISABLED, bg="gray50")


        for t, button in self.buttons.items():
            if t == tool:
                button.config(bg="green")
            else:
                button.config(bg="SystemButtonFace")


class Painting(ttk.Frame):
    """
    Canvas for drawing
    """
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        
        self.canvas_width = 600
        self.canvas_height = 600
        
        self.canvas = tk.Canvas(self, bg="red", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nanolist = NanoList(self.canvas)
        self.after(0, self.nanolist.update)
        
        self.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Bind left-click event
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)  # Bind dragging event
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)  # Bind release event

        self.triangles = []  # Store references to the triangle items
        
        self.columns_per_row = [13, 15, 17, 19, 21, 23, 23, 21, 19, 17]  # Grid layout
        self.draw_grid()

        self.tool_functions = {
            "blend": self.blend,
            "bucket": self.bucket,
            "dropper": self.dropper,
            "marker": self.marker,
            "pencil": self.pencil,
            "spray": self.spray
        }

        self.current_tool_function = None

    def on_resize(self, event: tk.Event) -> None:
        """
        Resize the canvas to fit drawing in new window size and update the grid to fit the window
        """
        toolbar_width = self.master.toolbar.winfo_width()
        self.canvas_width = self.master.winfo_width() - toolbar_width
        self.canvas_height = self.master.winfo_height()
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.coords(self.background, 0, 0, self.canvas_width, self.canvas_height)
        
        # Recalculate the triangle size and update the grid
        self.update_grid()

    def calculate_max_triangle_size(self) -> int:
        """
        Calculate the maximum triangle size that allows the grid to fit within the canvas.
        """
        max_width = self.canvas_width / (max(self.columns_per_row)+4) * 2
        max_height = self.canvas_height / (len(self.columns_per_row)+2) * (2 / (3**0.5))
        return min(max_width, max_height)

    def draw_grid(self) -> None:
        """
        Draw triangles row by row in the pattern used in UofC, ensuring they fit within the canvas.
        """
        self.background = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, outline="", fill="blue")

        prev_num_cols = 0
        self.triangle_length = self.calculate_max_triangle_size()
        self.triangle_height = self.triangle_length * (3**0.5) / 2

        for row, num_cols in enumerate(self.columns_per_row):
            growing = num_cols > prev_num_cols
            x_margin = (self.canvas_width - num_cols * self.triangle_length / 2) / 2
            y_margin = (self.canvas_height - len(self.columns_per_row) * self.triangle_height) / 2
            
            y_lower = y_margin + self.triangle_height * (row + 1)
            y_upper = y_margin + self.triangle_height * row

            X = [x_margin, x_margin + self.triangle_length / 2, x_margin + self.triangle_length]

            for col in range(num_cols):
                Y = [y_lower, y_upper, y_lower] if (col + growing) % 2 == 1 else [y_upper, y_lower, y_upper]
                triangle = self.canvas.create_polygon(list(zip(X, Y)), outline="white", fill="")
                self.triangles.append(triangle)
                X = [i + self.triangle_length / 2 for i in X]

            prev_num_cols = num_cols

    def update_grid(self) -> None:
        """
        Update the positions and sizes of the existing triangles to fit within the resized canvas.
        """
        prev_num_cols = 0
        self.triangle_length = self.calculate_max_triangle_size()
        self.triangle_height = self.triangle_length * (3**0.5) / 2
        triangle_index = 0

        for row, num_cols in enumerate(self.columns_per_row):
            growing = num_cols > prev_num_cols
            x_margin = (self.canvas_width - num_cols * self.triangle_length / 2) / 2
            y_margin = (self.canvas_height - len(self.columns_per_row) * self.triangle_height) / 2
            
            y_lower = y_margin + self.triangle_height * (row + 1)
            y_upper = y_margin + self.triangle_height * row

            X = [x_margin, x_margin + self.triangle_length / 2, x_margin + self.triangle_length]

            for col in range(num_cols):
                Y = [y_lower, y_upper, y_lower] if (col + growing) % 2 == 1 else [y_upper, y_lower, y_upper]
                coords = list(zip(X, Y))
                self.canvas.coords(self.triangles[triangle_index], *sum(coords, ()))
                triangle_index += 1
                X = [i + self.triangle_length / 2 for i in X]

            prev_num_cols = num_cols

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        Handles canvas click event
        """
        item = self.canvas.find_closest(event.x, event.y)
        
        # op_params of the form {"radius":2, ...}
        op_params = {x:self.master.toolbar.options[x].get() for x in self.master.toolbar.options}
        op_params["colour1"] = self.master.toolbar.colour1

        if item[0] != self.background or self.master.toolbar.selected_tool=="dropper":
            self.current_tool_function = self.tool_functions.get(self.master.toolbar.selected_tool)
            if self.current_tool_function:
                self.current_tool_function(item, **op_params)
            else:
                print(f"No function defined for tool {self.master.toolbar.selected_tool}")
        elif item[0] == self.background:
            self.nanolist[item] = self.master.toolbar.colour1
            self.nanolist.update()

    def on_canvas_drag(self, event: tk.Event) -> None:
        """
        Handles dragging motion over the canvas
        """
        self.after(20) # still 50fps
        if self.current_tool_function:
            item = self.canvas.find_closest(event.x, event.y)
            op_params = {x:self.master.toolbar.options[x].get() for x in self.master.toolbar.options}
            op_params["colour1"] = self.master.toolbar.colour1
            if item[0] != self.background or self.master.toolbar.selected_tool=="dropper":
                self.current_tool_function(item, **op_params)
            elif item[0] == self.background:
                self.nanolist[item] = self.master.toolbar.colour1
                self.nanolist.update()

    def on_canvas_release(self, event: tk.Event) -> None:
        """
        Handles mouse button release after dragging
        """
        self.current_tool_function = None


    def blend(self, item: int, **kwargs) -> None:
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        pass

    def bucket(self, item: int, **kwargs) -> None:
        tolerance = kwargs["tolerance"]
        pass

    def dropper(self, item: int, **kwargs) -> None:
        self.master.toolbar.colour1 = self.nanolist[item]
        self.master.toolbar.colour1_button.config(bg=self.nanolist[item])

    def marker(self, item: int, **kwargs) -> None:
        """
        TODO**
        Eraser tool functionality: Reset the colour of the triangle
        """
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        self.nanolist[item] = "#ffffff"
        self.nanolist.update()

    def pencil(self, item: int, **kwargs) -> None:
        """
        Pencil tool functionality: Change the colour of the triangle to the selected colour
        """
        radius = kwargs["radius"]
        self.nanolist[item] = self.master.toolbar.colour1
        self.nanolist.update()

    def spray(self, item: int, **kwargs) -> None:
        """
        Spraypaint tool functionality
        """
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        pts = self.nanolist.knn(item, radius=radius)
        for x in pts:
            if 3*random() < ((strength+0.001)**((strength+1))):
                self.nanolist[x] = self.master.toolbar.colour1
                self.nanolist.update()


def main() -> None:
    """
    Main function to start application
    """
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
