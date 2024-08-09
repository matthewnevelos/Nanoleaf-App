import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk

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
        self.icons = {}
        self.buttons = {}
        self.colour1 = "#fff"
        self.colour2 = "#000"
        self.selected_tool = None

        # Define styles for selected and unselected buttons
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.map("TButton", background=[("active", "#ececec")])
        style.configure("Selected.TButton", background="#d3d3d3")

        # Create tools and color buttons
        self.create_color_buttons()
        self.create_tools()

        # Initially select pen
        self.select_tool("pen")

    def create_tools(self) -> None:
        icons = ["blend", "bucket", "dropper", "eraser", "gradient", "line", "magnify", "pen", "pencil"]
        for i, icon in enumerate(icons):
            try:
                image = Image.open(f"icons/{icon}.png").resize((50, 50))
                photo = ImageTk.PhotoImage(image)
                button = ttk.Button(self, image=photo, command=lambda icon=icon: self.select_tool(icon))
                button.grid(row=i // 2 + 2, column=i % 2, padx=5, pady=5)  # Adjust row to start below color buttons
                self.icons[icon] = photo  # Store reference
                self.buttons[icon] = button
            except FileNotFoundError:
                print(f"Icon {icon}.png not found in the 'icons/' directory.")

    def create_color_buttons(self) -> None:
        self.color1_button = tk.Button(self, bg=self.colour1, width=10, height=2, command=self.choose_color1)
        self.color1_button.grid(row=0, column=0, pady=5)

        self.color2_button = tk.Button(self, bg=self.colour2, width=10, height=2, command=self.choose_color2)
        self.color2_button.grid(row=0, column=1, pady=5)

    def choose_color1(self) -> None:
        color = colorchooser.askcolor(title="Choose Color 1")[1]
        if color:
            self.colour1 = color
            self.color1_button.config(bg=self.colour1)

    def choose_color2(self) -> None:
        color = colorchooser.askcolor(title="Choose Color 2")[1]
        if color:
            self.colour2 = color
            self.color2_button.config(bg=self.colour2)

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool
        self.update_button_style(tool)

    def update_button_style(self, selected_tool: str) -> None:
        for tool, button in self.buttons.items():
            button.configure(style="Selected.TButton" if tool == selected_tool else "TButton")


class Painting(ttk.Frame):
    """
    Canvas for drawing
    """
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        
        self.canvas_width = 600
        self.canvas_height = 600
        self.brush_color = "black"
        
        self.canvas = tk.Canvas(self, bg="blue", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Bind left-click event

        self.triangles = []  # Store references to the triangle items
        
        self.draw_grid(50)

        # Mapping of tools to their respective functions
        self.tool_functions = {
            "pen": self.pen,
            "eraser": self.eraser,
            # Add other tools and their functions here
        }

    def on_resize(self, event: tk.Event) -> None:
        """
        Resize the canvas to fit drawing in new window size
        """
        toolbar_width = self.master.toolbar.winfo_width()
        self.canvas_width = self.master.winfo_width() - toolbar_width
        self.canvas_height = self.master.winfo_height()
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

    def draw_grid(self, triangle_size: int) -> None:
        """
        Draw a grid of triangles on the canvas.
        """
        self.canvas.delete("all")
        self.background = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, outline="", fill="blue")

        prev_num_cols = 0
        self.triangle_length = triangle_size
        self.triangle_height = self.triangle_length * (3**0.5) / 2
        columns_per_row = [13, 15, 17, 19, 21, 23, 23, 21, 19, 17]

        for row, num_cols in enumerate(columns_per_row):
            growing = num_cols > prev_num_cols
            x_margin = (self.canvas_width - num_cols * self.triangle_length / 2) / 2
            y_margin = (self.canvas_height - len(columns_per_row) * self.triangle_height) / 2
            
            y_lower = y_margin + self.triangle_height * (row + 1)
            y_upper = y_margin + self.triangle_height * row

            X = [x_margin, x_margin + self.triangle_length / 2, x_margin + self.triangle_length]

            for col in range(num_cols):
                Y = [y_lower, y_upper, y_lower] if (col + growing) % 2 == 1 else [y_upper, y_lower, y_upper]
                triangle = self.canvas.create_polygon(list(zip(X, Y)), outline="white", fill="")
                self.triangles.append(triangle)
                X = [i + self.triangle_length / 2 for i in X]

            prev_num_cols = num_cols

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        Handles canvas click event
        """
        item = self.canvas.find_closest(event.x, event.y)
        if item[0] != self.background:
            tool_function = self.tool_functions.get(self.master.toolbar.selected_tool)
            if tool_function:
                tool_function(item)
            else:
                print(f"No function defined for tool {self.master.toolbar.selected_tool}")

    def pen(self, item: int) -> None:
        """
        Pen tool functionality: Change the color of the triangle to the selected color
        """
        self.canvas.itemconfig(item, fill=self.master.toolbar.colour1)

    def eraser(self, item: int) -> None:
        """
        Eraser tool functionality: Reset the color of the triangle
        """
        self.canvas.itemconfig(item, fill="#000")

    # def _knn(self, item: int) -> [int]:




def main() -> None:
    """
    Main function to start application
    """
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
