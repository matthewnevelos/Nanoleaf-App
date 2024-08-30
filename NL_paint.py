import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from nanolist import NanoList

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
        self.icons = {}
        self.buttons = {}
        self.colour1 = "#fff"
        self.colour2 = "#000"
        self.selected_tool = None
        self.radius = tk.IntVar()

        # Define styles for selected and unselected buttons
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.map("TButton", background=[("active", "#ececec")])
        style.configure("Selected.TButton", background="#d3d3d3")

        # Create tools and color buttons
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
                button = ttk.Button(self, image=photo, command=lambda icon=icon: self.select_tool(icon))
                button.grid(row=i // 2 + 3, column=i % 2, padx=5, pady=5)  # Adjust row to start below color buttons
                self.icons[icon] = photo  # Store reference
                self.buttons[icon] = button
            except FileNotFoundError:
                print(f"Icon {icon}.png not found in the 'icons/' directory.")

    def create_tool_options(self) -> None:
        """
        Create button to select colours, and scale to change radius of brush
        """

        def choose_color1() -> None:
            color = colorchooser.askcolor(title="Choose Color 1")[1]
            if color:
                self.colour1 = color
                self.color1_button.config(bg=self.colour1)

        def choose_color2() -> None:
            color = colorchooser.askcolor(title="Choose Color 2")[1]
            if color:
                self.colour2 = color
                self.color2_button.config(bg=self.colour2)

        self.color1_button = tk.Button(self, bg=self.colour1, width=10, height=2, command=choose_color1)
        self.color1_button.grid(row=0, column=0, pady=5)

        self.color2_button = tk.Button(self, bg=self.colour2, width=10, height=2, command=choose_color2)
        self.color2_button.grid(row=0, column=1, pady=5)

        self.radius_slider = tk.Scale(self, from_=0, to=5, orient=tk.HORIZONTAL, variable=self.radius, label="Radius:")
        self.radius_slider.grid(row=1, columnspan=2)

    def select_tool(self, tool: str) -> None:
        # Set the selected tool
        self.selected_tool = tool
        
        # Update the button styles
        for t, button in self.buttons.items():
            button.configure(style="Selected.TButton" if t == tool else "TButton")



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

        self.triangles = []  # Store references to the triangle items
        
        self.columns_per_row = [13, 15, 17, 19, 21, 23, 23, 21, 19, 17]  # Grid layout
        self.draw_grid()

        # Mapping of tools to their respective functions
        self.tool_functions = {
            "blend": self.blend,
            "bucket": self.bucket,
            "dropper": self.dropper,
            "marker": self.marker,
            "pencil": self.pencil,
            "spray": self.spray
            # Add other tools and their functions here
        }

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
        colour1 = self.master.toolbar.colour1
        colour2 = self.master.toolbar.colour2
        radius = self.master.toolbar.radius
        if item[0] != self.background:
            tool_function = self.tool_functions.get(self.master.toolbar.selected_tool)
            if tool_function:
                tool_function(item, colour1=colour1, colour2=colour2, radius=radius)
            else:
                print(f"No function defined for tool {self.master.toolbar.selected_tool}")
        elif item[0] == self.background:
            # Set background
            pass

    def blend(self, item: int, **kwargs) -> None:
        pass

    def bucket(self, item: int, **kwargs) -> None:
        pass

    def dropper(self, item: int, **kwargs) -> None:
        pass

    def marker(self, item: int, **kwargs) -> None:
        """
        TODO**
        Eraser tool functionality: Reset the color of the triangle
        """
        radius = kwargs["radius"]
        self.nanolist[item] = "#fff"
        self.nanolist.update()

    def pencil(self, item: int, **kwargs) -> None:
        """
        Pencil tool functionality: Change the color of the triangle to the selected color
        """
        self.nanolist[item] = self.master.toolbar.colour1
        self.nanolist.update()
        

    def spray(self, item: int, **kwargs) -> None:
        """
        Spraypaint tool functionality
        """
        radius = kwargs['radius']
        k = NanoList()
        pts = k.kn
        (item, radius)
        for x in pts:
            self.nanolist[x] = self.master.toolbar.colour1
            self.canvas.itemconfig(x, fill="#0FF")

        




def main() -> None:
    """
    Main function to start application
    """
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
