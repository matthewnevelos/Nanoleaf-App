import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# TODO 
# Type hints if feeling quirky
# Docstring
# Finish nanolist
# Add tools
# work on zooming
# custom sizes/shapes low priority
# Add styles

class App(tk.Tk):
    """
    Main window for UofC Nanoleaf Editor
    """
    def __init__(self) -> None:
        """
        Initialize the App, set up main window and its components
        """
        super().__init__()

        self.title("UofC Nanoleaf Editor")

        # Set window size and center it
        aw = 800
        ah = 600
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - aw) // 2
        y = (sh - ah) // 2
        self.geometry(f'{aw}x{ah}+{x}+{y}')

        self.toolbar = ToolSideBar(self)
        self.toolbar.pack(fill='y', side='left', expand=False)

        self.canvas_frame = Painting(self)
        self.canvas_frame.pack(fill="both", side="right", expand=True)

        self.update_idletasks()  # Update the geometry manager


class ToolSideBar(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, width=150)

        # Style
        # style = ttk.Style()
        # style.configure('TFrame', background='lightgray')

        # List of icons
        icons = [
            "blend", "bucket", "dropper", "eraser", "gradient",
            "line", "magnify", "pen", "pencil"
        ]

        # Store references to icons to prevent garbage collection
        self.icons = {}

        # Load images and create buttons
        for i, icon in enumerate(icons):
            try:
                image = Image.open(f"icons/{icon}.png").resize((50, 50))
                photo = ImageTk.PhotoImage(image)
                self.icons[icon] = photo  # Store reference

                button = ttk.Button(self, image=photo)
                row = i // 2
                column = i % 2
                button.grid(row=row, column=column)
            except FileNotFoundError:
                print(f"Icon {icon}.png not found in the 'icons/' directory.")


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
        Background is a rectangle
        Draw triangles row by row in the pattern used in UofC.
        (0,0) is top left

        vertices are numbered as following
            2       1 ______ 3
            /\        \    /
           /  \        \  /
        1 /____\ 3      \/2

        x-coordinates increment by half the length of the triangle
        y-coordinates flip 1,2 <-> 3

        The drawing will be offset such that there is equal whitespace above and below

        If growing, the first triangle will be upward
        The first and last triangle of a row will be the same orientation
        """
        # Draw background first
        self.background = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, outline="", fill="blue")

        prev_num_cols = 0
        self.triangle_length = triangle_size
        self.triangle_height = self.triangle_length * (3**0.5) / 2
        columns_per_row = [13, 15, 17, 19, 21, 23, 23, 21, 19, 17]

        for row, num_cols in enumerate(columns_per_row):
            growing = True
            num_rows = len(columns_per_row)

            if columns_per_row[row] <= prev_num_cols:
                growing = False
            x_margin = (self.canvas_width - num_cols * self.triangle_length / 2) / 2
            y_margin = (self.canvas_height - num_rows * self.triangle_height) / 2
            
            y_lower = y_margin + self.triangle_height * (row + 1)
            y_upper = y_margin + self.triangle_height * row

            X = [x_margin, x_margin + self.triangle_length / 2, x_margin + self.triangle_length]

            for col in range(num_cols):
                if (col + growing) % 2 == 1:
                    Y = [y_lower, y_upper, y_lower]  # Upwards
                else:
                    Y = [y_upper, y_lower, y_upper]  # Downwards
                
                triangle = self.canvas.create_polygon(list(zip(X, Y)), outline="white", fill="")
                self.triangles.append(triangle)  # Store reference to the triangle

                # Increment x-coords
                X = [i + self.triangle_length / 2 for i in X]

            prev_num_cols = columns_per_row[row]
        

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        Handles canvas click event
        """
        # Get the item (triangle) clicked on
        item = self.canvas.find_closest(event.x, event.y)
        
        # Check if the click was on the background
        if item[0]== self.background:
            print(item)
            # Change the color of the background
            self.canvas.itemconfig(self.background, fill="green") 
        else:
            # Change the color of the triangle
            self.canvas.itemconfig(item, fill="red")
        print(item)


def main() -> None:
    """
    Main function to start application
    """
    app = App()
    app.mainloop()
        

if __name__ == '__main__':
    main()
