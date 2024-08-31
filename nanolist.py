from typing import Tuple, Union, List

# TODO Add colours to __str__

class NanoList:
    def __init__(self, canvas, shape=[1, 13, 15, 17, 19, 21, 23, 23, 21, 19, 17]):
        """
        Container which will be used for storing colours of the NanoLeaf.
        
        0th entry is background colour. Not used for anything other than displaying on tkinter.
        """
        self.canvas = canvas
        self.shape: List[int] = shape
        self.data = [["#000000"] * i for i in self.shape]
        self.data[0][0] = "#555555"
        self.history = [] # Previous edits, Last entry is most recent
        self.future = [] # Previous undos, Last entry is most recent
        self.forward = True 

    def __getitem__(self, index):
        """
        Get entry based on either index or [row][col]
            Although each row is staggered, each row starts at 0 index
        """
        if isinstance(index, tuple) and len(index)==1: index = index[0]
        if isinstance(index, tuple):
            outer_index, inner_index = index
            try:
                return self.data[outer_index][inner_index]
            except IndexError:
                raise IndexError(f"Index {inner_index} out of range for sublist {outer_index}")
        else:
            index -=1
            if index < 0:
                raise IndexError("Negative indexing is not supported")
            current_index = index
            for outer_index, sublist in enumerate(self.data):
                if current_index < len(sublist):
                    return sublist[current_index]
                current_index -= len(sublist)
            raise IndexError("Index out of range")

    def __setitem__(self, index, value):
        """
        Set value with either index or [row][col]
        """
        if isinstance(index, tuple) and len(index)==1: index = index[0]
        if isinstance(index, tuple):
            outer_index, inner_index = index
            try:
                self.data[outer_index][inner_index] = value
            except IndexError:
                raise IndexError(f"Index {inner_index} out of range for sublist {outer_index}")
        else:
            index -=1
            if index < 0:
                raise IndexError("Negative indexing is not supported")
            current_index = index
            for outer_index, sublist in enumerate(self.data):
                if current_index < len(sublist):
                    self.data[outer_index][current_index] = value
                    return
                current_index -= len(sublist)
            raise IndexError("Index out of range")
        
    def _get_rowcol(self, index) -> Tuple[int, int]:
        """
        return (row, col) for given index
        """
        if index < 0:
            raise IndexError("Negative indexing is not supported")
        current_index = index
        for outer_index, sublist in enumerate(self.data):
            if current_index < len(sublist):
                return (outer_index, current_index)
            current_index -= len(sublist)
        raise IndexError("Index out of range")
    
    def _get_index(self, coord: Tuple[int, int]) -> int:
        (row, col) = coord
        index = 1
        for i in range(row):
            index += self.shape[i]
        index += col
        return index
    
    def knn(self, index, radius) -> Tuple[int]:
        """
        Return nearest neighbours of a point based on set radius
        radius = 0: [0,0]
        radius = 1: [0,0, ]
        """
        index = index[0]
        relative_points = self._generate_points(radius, flip=self._is_rightsideup(index))
        center_pos = self._get_rowcol(index)
        print("relative_points")
        print(relative_points)
        relative_points = [()]
        abs_pos = self._get_abs_pts(center_pos, relative_points)
        return abs_pos

    def _get_abs_pts(self, center, rel_pts):
        """
        Calculates the absolute coordinate of a list of points.
        Given center, and list of the coordinates relative to center
        """
        abs_pts = []
        (row_center, col_center) = center
        num_cols_in_center = self.shape[row_center]
        for pt in rel_pts:
            (row_rel, col_rel) = pt
            num_cols_in_rel = self.shape[row_center+row_rel]
            col_diff = num_cols_in_rel - num_cols_in_center
            row = row_center + row_rel
            col = col_center + col_diff + col_rel
            abs_pts.append((row+col))

        return abs_pts


    def _generate_points(self, r, flip=False):
        """
        generate the relative coordinates. 
        returns a list of the form [(0,0), (1,0), (1,1), (-1,-1)]
        """
        if r == 0:
            return[0]
        if r == 1:
            pattern = [1, 3]

        pattern = [2*r+1]*(2*r-1)

        for i, _ in enumerate(pattern):
            if i < (r-1): 
                pattern[i] += 2*i
            if i == (r-1):
                pattern[i] = pattern[i-1]
            elif i > (r-1):
                pattern[i] = pattern[i-1] - 2
        
        if flip:
            pattern.reverse()

        return pattern


    def _is_rightsideup(self, index: Union[int, Tuple[int, int]]) -> bool:
        """
        Checks if a triangle is rightside up
        """
        # Its only being called once, should I keep check for (row, col)?
        if isinstance(index, int):
            row, col = self._get_rowcol(index)
        else: (row, col) = index # <- should never be used

        if row < 6: growing = True
        else: growing = False

        if (col + growing) % 2: return True
        else: return False

    def _is_exist(self, pos: Tuple[int, int]) -> bool:
        """
        Checks if triangle exists from a given (row, col) coordinate
        """
        (row, col) = pos

        if row < 0 or col < 0:
            return False

        if row > len(self.shape)():
            return False

        if col >= self.shape[row]:
            return False
        
        return True



    def __str__(self):
        """
        for multiline centering must center, then newline character
        """
        max_row_length = max(self.shape)+1
        center_length = max_row_length * 3 + (max_row_length - 1) - 2 # 3 digit numbers + a space between them
        middle = ""

        for row in self.data:
            row_str = " ".join(f"{num:3}" for num in row)
            middle += row_str.center(center_length) + "\n"

        return middle
    
    def update(self, forward=True):
        if not self.forward and forward: # If previous update was undo/redo and current is novel update, clear self.future
            self.future.clear()

        self.forward = forward
        if forward:
            self.history.append(self.data)
            self.history = self.history[-10:] # Only keep 10 most recent

        for row_i, row in enumerate(self.data):
            for col_i, colour in enumerate(row):
                index = self._get_index((row_i, col_i))
                self.canvas.itemconfig(index, fill=colour)

    def undo(self):
        try:
            self.future.append(self.history.pop())
            self.update(forward=False)
        except IndexError:
            print("Nothing to undo")

    def redo(self):
        if not self.forward: # executes only if last update was an undo
            try:
                self.history.append(self.future.pop())
            except IndexError:
                print("Nothing to redo")

    def colour_mixer(self, c1, c2, s2=0.5):
        """
        c1 is the colour already on the screen
        c2 is the colour that will be applied
        s2 is the strength of the applied colour (0-1)
        """
        if not (0<=s2<=1):
            raise ValueError("s2 must be between 0 and 1")
        s1=1-s2

        

