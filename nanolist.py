class NanoList:
    def __init__(self, shape=[1, 13, 15, 17, 19, 21, 23, 23, 21, 19, 17]):
        """
        Container which will be used for storing colours of the NanoLeaf.
        
        0th entry is background colour. Not used for anything other than displaying on tkinter.
        """
        self.shape = shape
        self.data = [[0] * i for i in self.shape]

    def __getitem__(self, index):
        if isinstance(index, tuple):
            outer_index, inner_index = index
            try:
                return self.data[outer_index][inner_index]
            except IndexError:
                raise IndexError(f"Index {inner_index} out of range for sublist {outer_index}")
        else:
            if index < 0:
                raise IndexError("Negative indexing is not supported")
            current_index = index
            for outer_index, sublist in enumerate(self.data):
                if current_index < len(sublist):
                    return sublist[current_index]
                current_index -= len(sublist)
            raise IndexError("Index out of range")

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            outer_index, inner_index = index
            try:
                self.data[outer_index][inner_index] = value
            except IndexError:
                raise IndexError(f"Index {inner_index} out of range for sublist {outer_index}")
        else:
            if index < 0:
                raise IndexError("Negative indexing is not supported")
            current_index = index
            for outer_index, sublist in enumerate(self.data):
                if current_index < len(sublist):
                    self.data[outer_index][current_index] = value
                    return
                current_index -= len(sublist)
            raise IndexError("Index out of range")

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
    
    def update(self, values: list):
        for i, val in enumerate(values):
            self.data[i]= val

# Example usage
nano_list = NanoList()

print(nano_list)
