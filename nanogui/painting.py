import tkinter as tk
from tkinter import ttk
from random import random
import nanogui.nanolist as nl



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

        self.nanolist = nl.NanoList(self.canvas)
        self.after(0, self.nanolist.update)
        
        self.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click) 
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag) 
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release) 
        self.canvas.bind("<MouseWheel>", self.scroll_radius)

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
                print(f"No function defined for tool: {self.master.toolbar.selected_tool}")
        elif item[0] == self.background:
            if self.master.toolbar.selected_tool != "blend":
                self.nanolist[item] = self.master.toolbar.colour1
                self.nanolist.update()
                self.nanolist.update_undo()

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

    def on_canvas_release(self, event: tk.Event) -> None:
        """
        Handles mouse button release after dragging
        """
        self.current_tool_function = None
        self.nanolist.update_undo()

    def scroll_radius(self, event: tk.Event):
        current_r = self.master.toolbar.options['radius'].get()
        delta_r = int(1*(event.delta/120))
        new_r = current_r + delta_r
        self.master.toolbar.options['radius'].set(new_r)

    def set_cursor(self, tool):
        # https://stackoverflow.com/a/66205274
        path = f"@img/cursors/{tool}.cur"
        self['cursor'] = path

    def blend(self, item: int, **kwargs) -> None:
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        pts = self.nanolist.knn(item, radius=radius)
        for x in pts:
            i = self.nanolist._get_index(x)
            adj_col = []
            adj_pts = self.nanolist.knn(i, radius=1)
            adj_pts = [pt for pt in adj_pts if pt != x]
            for y in adj_pts:
                adj_col.append(self.nanolist[y])
            new_col = self.nanolist.colour_mixer(self.nanolist[x], strength, adj_col)
            self.nanolist[x] = new_col
            self.nanolist.update()
            

    def bucket(self, item: int, **kwargs) -> None:
        tolerance = kwargs["tolerance"]
        pts_abs = [self.nanolist._get_rowcol(item[0])]
        c1 = self.nanolist[pts_abs[0]]
        pts_abs = self.nanolist.similar_neighbour(pts_abs[0], tolerance, c1, pts_abs)
        for x in pts_abs:
            self.nanolist[x] = self.master.toolbar.colour1
            self.nanolist.update()


    def dropper(self, item: int, **kwargs) -> None:
        """
        changes colour to the colour of the one clicked
        """
        self.master.toolbar.colour1 = self.nanolist[item]
        self.master.toolbar.colour1_button.config(bg=self.nanolist[item])

    def marker(self, item: int, **kwargs) -> None:
        """
        Marker adds colour mixing with what is already on the canvas
        """
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        pts = self.nanolist.knn(item, radius=radius)
        for x in pts:
            new_colour = self.nanolist.colour_mixer(self.nanolist[x], strength, [self.master.toolbar.colour1])
            self.nanolist[x] = new_colour
            self.nanolist.update()

    def pencil(self, item: int, **kwargs) -> None:
        """
        Pencil directly changes colour
        """
        radius = kwargs["radius"]
        pts = self.nanolist.knn(item, radius=radius)
        for x in pts:
            self.nanolist[x] = self.master.toolbar.colour1
            self.nanolist.update()

    def spray(self, item: int, **kwargs) -> None:
        """
        Adds colour with randomness
        """
        radius = kwargs["radius"]
        strength = kwargs["strength"]
        pts = self.nanolist.knn(item, radius=radius)
        for x in pts:
            if 3*random() < ((strength+0.001)**((strength+1))):
                self.nanolist[x] = self.master.toolbar.colour1
                self.nanolist.update()