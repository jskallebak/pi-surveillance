import tkinter as tk
from tkinter import simpledialog, filedialog
import sys
import json

class Rectangle:
    def __init__(self, name, x, y, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.canvas_item = None
        self.text_item = None
        self.p1_item = None  # Input point (left)
        self.p2_item = None  # Output point (right)
        self.points_swapped = False
        self.update_connection_points()

        self.red_box = None
        self.blue_box = None
        self.yellow_box = None

        self.red_signal = False
        self.blue_signal = False
        self.yellow_signal = False

    def update_connection_points(self):
        if not self.points_swapped:
            self.p1 = (self.x, self.y + (self.height / 2))
            self.p2 = (self.x + self.width, self.y + (self.height / 2))
        else:
            self.p2 = (self.x, self.y + (self.height / 2))
            self.p1 = (self.x + self.width, self.y + (self.height / 2))

    def update_connection_points(self):
        if not self.points_swapped:
            self.p1 = (self.x, self.y + (self.height / 2))
            self.p2 = (self.x + self.width, self.y + (self.height / 2))
        else:
            self.p2 = (self.x, self.y + (self.height / 2))
            self.p1 = (self.x + self.width, self.y + (self.height / 2))

    def draw(self, canvas):
        if self.canvas_item:
            canvas.delete(self.canvas_item)
        if self.text_item:
            canvas.delete(self.text_item)
        if self.p1_item:
            canvas.delete(self.p1_item)
        if self.p2_item:
            canvas.delete(self.p2_item)
        if self.red_box:
            canvas.delete(self.red_box)
        if self.blue_box:
            canvas.delete(self.blue_box)
        if self.yellow_box:
            canvas.delete(self.yellow_box)

        self.canvas_item = canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            outline="black", fill="lightblue"
        )
        self.text_item = canvas.create_text(
            self.x + 5, self.y + 5,
            text=self.name,
            anchor="nw",
            font=("Arial", 10),
            fill="black"
        )
        
        point_radius = 3
        self.p1_item = canvas.create_oval(
            self.p1[0] - point_radius, self.p1[1] - point_radius,
            self.p1[0] + point_radius, self.p1[1] + point_radius,
            fill="blue"
        )
        self.p2_item = canvas.create_oval(
            self.p2[0] - point_radius, self.p2[1] - point_radius,
            self.p2[0] + point_radius, self.p2[1] + point_radius,
            fill="red"
        )

        # Draw wider colored boxes with padding
        box_width = 30
        box_height = (self.height - 20) / 3
        box_x = self.x + self.width - box_width - 5
        box_y = self.y + 10

        self.red_box = canvas.create_rectangle(
            box_x, box_y, 
            box_x + box_width, box_y + box_height,
            fill="red" if self.red_signal else "gray", outline=""
        )
        self.blue_box = canvas.create_rectangle(
            box_x, box_y + box_height, 
            box_x + box_width, box_y + 2*box_height,
            fill="blue" if self.blue_signal else "gray", outline=""
        )
        self.yellow_box = canvas.create_rectangle(
            box_x, box_y + 2*box_height, 
            box_x + box_width, box_y + 3*box_height,
            fill="yellow" if self.yellow_signal else "gray", outline=""
        )

    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.update_connection_points()

    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.update_connection_points()

    def switch_points(self):
        self.points_swapped = not self.points_swapped
        self.update_connection_points()

    def set_signal(self, color, signal):
        if color == "red":
            self.red_signal = signal
        elif color == "blue":
            self.blue_signal = signal
        elif color == "yellow":
            self.yellow_signal = signal
        else:
            raise ValueError("Invalid color. Use 'red', 'blue', or 'yellow'.")

    def get_signal(self, color):
        if color == "red":
            return self.red_signal
        elif color == "blue":
            return self.blue_signal
        elif color == "yellow":
            return self.yellow_signal
        else:
            raise ValueError("Invalid color. Use 'red', 'blue', or 'yellow'.")

class Line:
    def __init__(self, name, start_rect, end_rect, start_is_output=True):
        self.name = name
        self.start_rect = start_rect
        self.end_rect = end_rect
        self.start_is_output = start_is_output
        self.canvas_item = None
        self.update_coordinates()

    def update_coordinates(self):
        if self.start_is_output:
            self.x1, self.y1 = self.start_rect.p2
            self.x2, self.y2 = self.end_rect.p1
        else:
            self.x1, self.y1 = self.start_rect.p1
            self.x2, self.y2 = self.end_rect.p2

    def draw(self, canvas):
        if self.canvas_item:
            canvas.delete(self.canvas_item)
        self.update_coordinates()
        self.canvas_item = canvas.create_line(
            self.x1, self.y1, self.x2, self.y2,
            fill="red", width=2
        )

class DrawingApp:
    def __init__(self, master, live_mode=False, load_file=None):
        self.master = master
        self.master.title("Enhanced Drawing App")
        self.live_mode = live_mode
        
        self.canvas = tk.Canvas(self.master, width=800, height=600, bg="white")
        self.canvas.pack()
        
        if not live_mode:
            # Create a frame for the buttons
            self.button_frame = tk.Frame(self.master)
            self.button_frame.pack(pady=5)

            # First row of buttons
            self.add_edit_rectangle_button = tk.Button(self.button_frame, text="Add/Edit Rectangle", command=self.prompt_add_edit_rectangle)
            self.add_edit_rectangle_button.grid(row=0, column=0, padx=5, pady=5)
            
            # Second row of buttons
            self.connect_rectangles_button = tk.Button(self.button_frame, text="Connect Rectangles", command=self.prompt_connect_rectangles)
            self.connect_rectangles_button.grid(row=1, column=0, padx=5, pady=5)
            
            self.disconnect_rectangles_button = tk.Button(self.button_frame, text="Disconnect Rectangles", command=self.prompt_disconnect_rectangles)
            self.disconnect_rectangles_button.grid(row=1, column=1, padx=5, pady=5)
            
            self.switch_points_button = tk.Button(self.button_frame, text="Switch Rectangle Points", command=self.prompt_switch_points)
            self.switch_points_button.grid(row=1, column=2, padx=5, pady=5)

            # Third row of buttons
            self.save_button = tk.Button(self.button_frame, text="Save Canvas", command=self.save_canvas)
            self.save_button.grid(row=2, column=0, padx=5, pady=5)

            self.load_button = tk.Button(self.button_frame, text="Load Canvas", command=self.load_canvas_dialog)
            self.load_button.grid(row=2, column=1, padx=5, pady=5)

            # Create a frame for the control panel
            self.control_panel = tk.Frame(self.master)
            self.control_panel.pack(pady=10)

            # Create an input field for the rectangle name
            self.rect_name_var = tk.StringVar()
            self.rect_name_entry = tk.Entry(self.control_panel, textvariable=self.rect_name_var)
            self.rect_name_entry.grid(row=0, column=0, padx=5)

            # Create buttons for toggling each color
            self.red_button = tk.Button(self.control_panel, text="Toggle Red", command=lambda: self.toggle_signal_ui("red"))
            self.red_button.grid(row=0, column=1, padx=5)

            self.blue_button = tk.Button(self.control_panel, text="Toggle Blue", command=lambda: self.toggle_signal_ui("blue"))
            self.blue_button.grid(row=0, column=2, padx=5)

            self.yellow_button = tk.Button(self.control_panel, text="Toggle Yellow", command=lambda: self.toggle_signal_ui("yellow"))
            self.yellow_button.grid(row=0, column=3, padx=5)

        self.rectangles = {}
        self.lines = {}

        self.dragged_rect = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.temp_connections = []

        # Only bind mouse events if not in live mode
        if not live_mode:
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Load canvas if specified, otherwise create initial setup
        if load_file:
            self.load_canvas(load_file)
        else:
            self.create_initial_setup()


    def load_canvas_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.load_canvas(file_path)

    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        canvas_state = {
            "rectangles": [],
            "lines": []
        }

        for rect in self.rectangles.values():
            canvas_state["rectangles"].append({
                "name": rect.name,
                "x": rect.x,
                "y": rect.y,
                "width": rect.width,
                "height": rect.height,
                "points_swapped": rect.points_swapped,
                "red_signal": rect.red_signal,
                "blue_signal": rect.blue_signal,
                "yellow_signal": rect.yellow_signal
            })

        for line in self.lines.values():
            canvas_state["lines"].append({
                "name": line.name,
                "start_rect": line.start_rect.name,
                "end_rect": line.end_rect.name,
                "start_is_output": line.start_is_output
            })

        with open(file_path, 'w') as f:
            json.dump(canvas_state, f, indent=2)

        print(f"Canvas state saved to {file_path}")

    def load_canvas(self, file_path):
        try:
            with open(file_path, 'r') as f:
                canvas_state = json.load(f)

            self.clear_canvas()

            for rect_data in canvas_state["rectangles"]:
                rect = Rectangle(rect_data["name"], rect_data["x"], rect_data["y"], rect_data["width"], rect_data["height"])
                rect.points_swapped = rect_data["points_swapped"]
                rect.red_signal = rect_data.get("red_signal", False)
                rect.blue_signal = rect_data.get("blue_signal", False)
                rect.yellow_signal = rect_data.get("yellow_signal", False)
                rect.update_connection_points()
                self.rectangles[rect.name] = rect
                rect.draw(self.canvas)

            for line_data in canvas_state["lines"]:
                start_rect = self.rectangles[line_data["start_rect"]]
                end_rect = self.rectangles[line_data["end_rect"]]
                line = Line(line_data["name"], start_rect, end_rect, line_data["start_is_output"])
                self.lines[line.name] = line
                line.draw(self.canvas)

            print(f"Canvas state loaded from {file_path}")
        except Exception as e:
            print(f"Error loading canvas from {file_path}: {str(e)}")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.rectangles.clear()
        self.lines.clear()

    def create_initial_setup(self):
        # Try to load the initial state from a file
        initial_state_file = "initial_state.json"
        try:
            with open(initial_state_file, 'r') as f:
                canvas_state = json.load(f)

            for rect_data in canvas_state["rectangles"]:
                rect = Rectangle(rect_data["name"], rect_data["x"], rect_data["y"], rect_data["width"], rect_data["height"])
                rect.points_swapped = rect_data["points_swapped"]
                rect.update_connection_points()
                self.rectangles[rect.name] = rect
                rect.draw(self.canvas)

            for line_data in canvas_state["lines"]:
                start_rect = self.rectangles[line_data["start_rect"]]
                end_rect = self.rectangles[line_data["end_rect"]]
                line = Line(line_data["name"], start_rect, end_rect, line_data["start_is_output"])
                self.lines[line.name] = line
                line.draw(self.canvas)

            print(f"Initial state loaded from {initial_state_file}")

        except FileNotFoundError:
            # If the file doesn't exist, create the default setup with renamed rectangles
            r1 = Rectangle("r1", 100, 100, 150, 80)
            r2 = Rectangle("r2", 350, 300, 200, 100)
            r3 = Rectangle("r3", 600, 500, 150, 80)

            for rect in [r1, r2, r3]:
                rect.draw(self.canvas)
                self.rectangles[rect.name] = rect

            self.connect_rectangles("r1", "r2")
            self.connect_rectangles("r2", "r3")

            print("Default initial setup created with rectangles r1, r2, and r3")
    def prompt_add_edit_rectangle(self):
        name = simpledialog.askstring("Input", "Enter the name of the rectangle (new or existing):", parent=self.master)
        if name is None or name.strip() == "":
            print("Operation cancelled or invalid name.")
            return
        
        rectangle = self.rectangles.get(name)
        
        x = simpledialog.askinteger("Input", f"Enter x coordinate for {name}:", parent=self.master, initialvalue=rectangle.x if rectangle else 0)
        y = simpledialog.askinteger("Input", f"Enter y coordinate for {name}:", parent=self.master, initialvalue=rectangle.y if rectangle else 0)
        width = simpledialog.askinteger("Input", f"Enter width for {name}:", parent=self.master, initialvalue=rectangle.width if rectangle else 50)
        height = simpledialog.askinteger("Input", f"Enter height for {name}:", parent=self.master, initialvalue=rectangle.height if rectangle else 50)
        
        if all(value is not None for value in (x, y, width, height)):
            if rectangle:
                rectangle.x, rectangle.y, rectangle.width, rectangle.height = x, y, width, height
                rectangle.update_connection_points()
            else:
                rectangle = Rectangle(name, x, y, width, height)
                self.rectangles[name] = rectangle
            
            rectangle.draw(self.canvas)
            self.update_connected_lines(rectangle)
            print(f"Rectangle '{name}' {'updated' if name in self.rectangles else 'created'}.")
        else:
            print("Operation cancelled or invalid input.")

    def prompt_move_shape(self):
        if not self.rectangles and not self.lines:
            print("No shapes to move. Create a shape first.")
            return
        
        name = simpledialog.askstring("Input", "Enter the name of the shape to move:", parent=self.master)
        shape = self.rectangles.get(name) or self.lines.get(name)
        
        if not shape:
            print(f"No shape named '{name}' found.")
            return
        
        if isinstance(shape, Rectangle):
            new_x = simpledialog.askinteger("Input", f"Enter new x coordinate for {name}:", parent=self.master)
            new_y = simpledialog.askinteger("Input", f"Enter new y coordinate for {name}:", parent=self.master)
            
            if new_x is not None and new_y is not None:
                shape.move_to(new_x, new_y)
                shape.draw(self.canvas)
                self.update_connected_lines(shape)
                print(f"Rectangle '{name}' moved to ({new_x}, {new_y}).")
            else:
                print("Move operation cancelled or invalid input.")
        
        elif isinstance(shape, Line):
            new_x1 = simpledialog.askinteger("Input", f"Enter new x1 coordinate for {name}:", parent=self.master)
            new_y1 = simpledialog.askinteger("Input", f"Enter new y1 coordinate for {name}:", parent=self.master)
            new_x2 = simpledialog.askinteger("Input", f"Enter new x2 coordinate for {name}:", parent=self.master)
            new_y2 = simpledialog.askinteger("Input", f"Enter new y2 coordinate for {name}:", parent=self.master)
            
            if all(coord is not None for coord in (new_x1, new_y1, new_x2, new_y2)):
                shape.update_coordinates()
                shape.draw(self.canvas)
                print(f"Line '{name}' moved.")
            else:
                print("Move operation cancelled or invalid input.")

    def prompt_resize_shape(self):
        if not self.rectangles:
            print("No rectangles to resize. Create a rectangle first.")
            return
        
        name = simpledialog.askstring("Input", "Enter the name of the rectangle to resize:", parent=self.master)
        shape = self.rectangles.get(name)
        
        if not shape:
            print(f"No rectangle named '{name}' found.")
            return
        
        width = simpledialog.askinteger("Input", f"Enter new width for {name}:", parent=self.master)
        height = simpledialog.askinteger("Input", f"Enter new height for {name}:", parent=self.master)
        
        if width is not None and height is not None:
            shape.resize(width, height)
            shape.draw(self.canvas)
            self.update_connected_lines(shape)
            print(f"Rectangle '{name}' resized.")
        else:
            print("Resize operation cancelled or invalid input.")

    def prompt_connect_rectangles(self):
        if len(self.rectangles) < 2:
            print("You need at least two rectangles to connect. Please create more rectangles.")
            return

        rect1_name = simpledialog.askstring("Input", "Enter the name of the first rectangle:", parent=self.master)
        rect2_name = simpledialog.askstring("Input", "Enter the name of the second rectangle:", parent=self.master)

        self.connect_rectangles(rect1_name, rect2_name)

    def connect_rectangles(self, rect1_name, rect2_name):
        if rect1_name not in self.rectangles or rect2_name not in self.rectangles:
            return

        rect1 = self.rectangles[rect1_name]
        rect2 = self.rectangles[rect2_name]

        line_name = f"Line_{rect1_name}_to_{rect2_name}"
        new_line = Line(line_name, rect1, rect2, True)
        self.lines[line_name] = new_line
        self.update_canvas()

    def prompt_disconnect_rectangles(self):
        if not self.lines:
            print("No connections to remove. Please connect some rectangles first.")
            return

        rect1_name = simpledialog.askstring("Input", "Enter the name of the first rectangle:", parent=self.master)
        rect2_name = simpledialog.askstring("Input", "Enter the name of the second rectangle:", parent=self.master)

        line_name = f"Line_{rect1_name}_to_{rect2_name}"
        reverse_line_name = f"Line_{rect2_name}_to_{rect1_name}"

        if line_name in self.lines:
            self.canvas.delete(self.lines[line_name].canvas_item)
            del self.lines[line_name]
            print(f"Disconnected {rect1_name} from {rect2_name}")
        elif reverse_line_name in self.lines:
            self.canvas.delete(self.lines[reverse_line_name].canvas_item)
            del self.lines[reverse_line_name]
            print(f"Disconnected {rect2_name} from {rect1_name}")
        else:
            print(f"No connection found between {rect1_name} and {rect2_name}")

    def prompt_switch_points(self):
        if not self.rectangles:
            print("No rectangles to switch points. Create a rectangle first.")
            return
        
        name = simpledialog.askstring("Input", "Enter the name of the rectangle to switch points:", parent=self.master)
        
        if name not in self.rectangles:
            print(f"No rectangle named '{name}' found.")
            return
        
        rectangle = self.rectangles[name]
        
        # Disconnect all lines connected to this rectangle
        self.remove_connections(name)
        
        # Switch the points
        rectangle.switch_points()
        rectangle.draw(self.canvas)
        
        print(f"Switched input and output points for rectangle '{name}' and disconnected all connected lines.")

    def prompt_get_connected(self):
        if not self.rectangles:
            print("No rectangles to check. Create some rectangles first.")
            return

        rect_name = simpledialog.askstring("Input", "Enter the name of the rectangle:", parent=self.master)
        if not rect_name:
            print("Operation cancelled.")
            return

        connected = self.get_connected_with_info(rect_name)
        if connected:
            print(f"Rectangles connected to '{rect_name}':")
            print(connected[0])
            for is_output in connected:
                connection_type = "output to" if is_output else "input from"
                #print(f"- {connection_type} {rect.name}")
        else:
            print(f"No rectangles are connected to '{rect_name}'.")

    def on_press(self, event):
        if self.live_mode:
            return
        for rect in self.rectangles.values():
            if rect.x <= event.x <= rect.x + rect.width and rect.y <= event.y <= rect.y + rect.height:
                self.dragged_rect = rect
                self.drag_start_x = event.x - rect.x
                self.drag_start_y = event.y - rect.y
                # Store connections with direction information
                self.temp_connections = self.get_connected_with_info(rect.name)

                self.remove_connections(rect.name)
                break

    def on_drag(self, event):
        if self.live_mode or not self.dragged_rect:
            return
        new_x = event.x - self.drag_start_x
        new_y = event.y - self.drag_start_y
        self.dragged_rect.move_to(new_x, new_y)
        self.dragged_rect.draw(self.canvas)

    def on_release(self, event):
        if self.live_mode:
            return
        if self.dragged_rect:
            # Reconnect stored connections
            self.reconnect(self.dragged_rect.name, self.temp_connections)
            self.dragged_rect = None
            self.temp_connections = []
            self.update_canvas()

    def remove_connections(self, rect_name):
        rect = self.rectangles[rect_name]
        lines_to_remove = []
        for line_name, line in self.lines.items():
            if line.start_rect == rect or line.end_rect == rect:
                self.canvas.delete(line.canvas_item)
                lines_to_remove.append(line_name)
        for line_name in lines_to_remove:
            del self.lines[line_name]

    def reconnect(self, rect_name, connected_info):
        for connected_rect, is_output, line_name in connected_info:
            print('Reconnecting:', connected_rect.name, is_output, line_name)
            if is_output:
                start_rect = self.rectangles[rect_name]
                end_rect = connected_rect
                self.connect_rectangles(start_rect.name, end_rect.name)
            else:
                start_rect = connected_rect
                end_rect = self.rectangles[rect_name]
                self.connect_rectangles(start_rect.name, end_rect.name)


    def get_connected_with_info(self, rect_name):
        if rect_name not in self.rectangles:
            print(f"No rectangle named '{rect_name}' found.")
            return []

        rect = self.rectangles[rect_name]
        connected = []

        for line in self.lines.values():
            if line.start_rect == rect:
                connected.append((line.end_rect, True, line.name))  # True indicates rect is the output
            elif line.end_rect == rect:
                connected.append((line.start_rect, False, line.name))  # False indicates rect is the input

        return connected

    def update_connected_lines(self, rect):
        for line in self.lines.values():
            if line.start_rect == rect or line.end_rect == rect:
                line.draw(self.canvas)
        self.redraw_all_rectangles()

    def update_canvas(self):
        self.draw_all_lines()
        self.redraw_all_rectangles()

    def redraw_all_rectangles(self):
        for rect in self.rectangles.values():
            rect.draw(self.canvas)

    def draw_all_lines(self):
        for line in self.lines.values():
            line.draw(self.canvas)

    def toggle_signal(self, rect_name, color):
        if rect_name in self.rectangles:
            rect = self.rectangles[rect_name]
            current_signal = rect.get_signal(color)
            rect.set_signal(color, not current_signal)
            rect.draw(self.canvas)
        else:
            print(f"Rectangle '{rect_name}' not found.")

    def set_all_signals(self, rect_name, signal):
        if rect_name in self.rectangles:
            rect = self.rectangles[rect_name]
            for color in ["red", "blue", "yellow"]:
                rect.set_signal(color, signal)
            rect.draw(self.canvas)
        else:
            print(f"Rectangle '{rect_name}' not found.")

    def toggle_signal_ui(self, color):
        rect_name = self.rect_name_var.get()
        if rect_name in self.rectangles:
            self.toggle_signal(rect_name, color)
        else:
            print(f"Rectangle '{rect_name}' not found.")

    def toggle_signal(self, rect_name, color):
        if rect_name in self.rectangles:
            rect = self.rectangles[rect_name]
            current_signal = rect.get_signal(color)
            rect.set_signal(color, not current_signal)
            rect.draw(self.canvas)
        else:
            print(f"Rectangle '{rect_name}' not found.")


if __name__ == "__main__":
    live_mode = "--live" in sys.argv
    load_file = None

    for arg in sys.argv:
        if arg.startswith("--load="):
            load_file = arg.split("=")[1]
            break

    root = tk.Tk()
    app = DrawingApp(root, live_mode=live_mode, load_file=load_file)
    root.mainloop()