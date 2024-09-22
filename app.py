import platform
import sys
import random

is_raspberry_pi = platform.machine().startswith('aarch64')
print(f"Running on a Raspberry Pi: {is_raspberry_pi}")
print(platform.machine())

if is_raspberry_pi:
    import RPi.GPIO as RealGPIO

    class GPIOWrapper:
        def __init__(self):
            self.simulating = True
            # Add these attributes
            self.BCM = RealGPIO.BCM
            self.IN = RealGPIO.IN
            self.OUT = RealGPIO.OUT
            self.PUD_DOWN = RealGPIO.PUD_DOWN
            self.PUD_UP = RealGPIO.PUD_UP
            self.HIGH = RealGPIO.HIGH
            self.LOW = RealGPIO.LOW

        def set_simulating(self, simulating):
            self.simulating = simulating

        def input(self, pin):
            value = RealGPIO.input(pin)
            if self.simulating:
                print(f"GPIO: Reading pin {pin}: {'HIGH' if value else 'LOW'}")
            return value

        # Implement other necessary methods, forwarding them to RealGPIO
        def setmode(self, mode):
            RealGPIO.setmode(mode)

        def setup(self, pin, mode, pull_up_down=None):
            if pull_up_down:
                RealGPIO.setup(pin, mode, pull_up_down=pull_up_down)
            else:
                RealGPIO.setup(pin, mode)

        def cleanup(self):
            RealGPIO.cleanup()

    GPIO = GPIOWrapper()
else:
    print("Not running on a Raspberry Pi. GPIO functionality will be simulated.")

    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        HIGH = 1
        LOW = 0
        PUD_DOWN = "PUD_DOWN"
        PUD_UP = "PUD_UP"
        
        def __init__(self):
            self.pin_values = {}
            self.simulating = True

        def setmode(self, mode):
            print(f"Mock: Setting GPIO mode to {mode}")

        def set_simulating(self, simulating):
            self.simulating = simulating

        def setwarnings(self, flag):
            print(f"Mock: Setting warnings to {flag}")

        def setup(self, pin, mode, pull_up_down=None):
            pull_up_down_str = f" with pull_up_down={pull_up_down}" if pull_up_down else ""
            print(f"Mock: Setting up GPIO pin {pin} as {'input' if mode == self.IN else 'output'}{pull_up_down_str}")
            if pin not in self.pin_values:
                self.pin_values[pin] = self.LOW  # Initialize to LOW

        def input(self, pin):
            if pin not in self.pin_values:
                self.pin_values[pin] = self.LOW
            if self.simulating:
                value = "HIGH" if self.pin_values[pin] == self.HIGH else "LOW"
                print(f"Mock: Reading GPIO pin {pin}: {value}")
            return self.pin_values[pin]
        
        def set_mock_value(self, pin, value):
            self.pin_values[pin] = value


        def cleanup(self, pin=None):
            if pin is None:
                print("Mock: Cleaning up all GPIO pins")
            else:
                print(f"Mock: Cleaning up GPIO pin {pin}")

    GPIO = MockGPIO()


import tkinter as tk
from tkinter import simpledialog, filedialog
import json
from time import sleep
from threading import Thread

class Rectangle:
    def __init__(self, name, x, y, width, height, gpio=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gpio = gpio
        if self.gpio is not None:
            self.setup_gpio()
        self.canvas_item = None
        self.text_item = None
        self.gpio_text_item = None
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

    def simulate_gpio(self):
        return random.choice([GPIO.HIGH, GPIO.LOW])

    def get_gpio_state(self, simulating):
        if self.gpio is None:
            return None
        if simulating:
            return self.simulate_gpio()
        else:
            return GPIO.input(self.gpio)

    def setup_gpio(self):
        if self.gpio is not None:
            GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update_gpio(self, new_gpio):
        if self.gpio is not None:
            GPIO.cleanup(self.gpio)
        self.gpio = new_gpio
        if self.gpio is not None:
            self.setup_gpio()

    def read_gpio(self):
        if self.gpio is not None:
            return GPIO.input(self.gpio)
        return None

    def update_connection_points(self):
        if not self.points_swapped:
            self.p1 = (self.x, self.y + (self.height / 2))
            self.p2 = (self.x + self.width, self.y + (self.height / 2))
        else:
            self.p2 = (self.x, self.y + (self.height / 2))
            self.p1 = (self.x + self.width, self.y + (self.height / 2))

    def set_mock_gpio(self, value):
        if self.gpio is not None:
            GPIO.set_mock_value(self.gpio, value)


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
        if self.gpio_text_item:
            canvas.delete(self.gpio_text_item)
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
        
        if self.gpio is not None:
            self.gpio_text_item = canvas.create_text(
                self.x + 5, self.y + 20,  # Adjust the y-coordinate as needed
                text=f"gpio: {self.gpio}",
                anchor="nw",
                font=("Arial", 8),
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
            if self.gpio is not None:
                GPIO.set_mock_value(self.gpio, GPIO.HIGH if signal else GPIO.LOW)
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
        
        def get_gpio_state(self, simulating):
            if self.gpio is None:
                return None
            return GPIO.input(self.gpio)
    

class Line:
    def __init__(self, name, start_shape, end_shape, start_is_output=True):
        self.name = name
        self.start_shape = start_shape
        self.end_shape = end_shape
        self.start_is_output = start_is_output
        self.canvas_item = None
        self.update_coordinates()

    def update_coordinates(self):
        if isinstance(self.start_shape, Rectangle):
            self.x1, self.y1 = self.start_shape.p2 if self.start_is_output else self.start_shape.p1
        else:  # Point
            self.x1, self.y1 = self.start_shape.x, self.start_shape.y

        if isinstance(self.end_shape, Rectangle):
            self.x2, self.y2 = self.end_shape.p1 if self.start_is_output else self.end_shape.p2
        else:  # Point
            self.x2, self.y2 = self.end_shape.x, self.end_shape.y

    def draw(self, canvas):
        if self.canvas_item:
            canvas.delete(self.canvas_item)
        self.canvas_item = canvas.create_line(
            self.x1, self.y1, self.x2, self.y2,
            fill="red", width=2
        )

class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.canvas_item = None
        self.text_item = None
        self.is_visible = True

    def draw(self, canvas):
        if self.canvas_item:
            canvas.delete(self.canvas_item)
        if self.text_item:
            canvas.delete(self.text_item)

        if self.is_visible:
            point_radius = 3
            self.canvas_item = canvas.create_oval(
                self.x - point_radius, self.y - point_radius,
                self.x + point_radius, self.y + point_radius,
                fill="black"
            )
            self.text_item = canvas.create_text(
                self.x, self.y - 15,
                text=self.name,
                anchor="center",
                font=("Arial", 8),
                fill="black"
            )

    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    # Add these methods to make Points compatible with the existing Rectangle interface
    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    @property
    def p1(self):
        return (self.x, self.y)

    @property
    def p2(self):
        return (self.x, self.y)

class DrawingApp:
    def __init__(self, master, live_mode=False, load_file=True):
        self.master = master
        self.live_mode = live_mode
        self.default_canvas_file = "qq.json"

        self.simulating = True
        
        self.canvas = tk.Canvas(self.master, width=800, height=600, bg="white")
        self.canvas.pack()
        
        self.rectangles = {}
        self.lines = {}
        self.points = {}

        self.dragged_shape = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.temp_connections = []

        self.polling = False
        self.poll_thread = None

        if load_file:
            self.load_canvas(self.default_canvas_file)
        else:
            self.create_initial_setup()

        if not live_mode:

            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)

            self.setup_ui()
            self.start_gpio_polling()
            self.simulate_button.config(text=f"Simulation: {'ON' if self.simulating else 'OFF'}")

    def setup_ui(self):
            # Create a frame for the buttons
            self.button_frame = tk.Frame(self.master)
            self.button_frame.pack(pady=5)

            # First row of buttons
            self.add_edit_rectangle_button = tk.Button(self.button_frame, text="Add/Edit Rectangle", command=self.prompt_add_edit_rectangle)
            self.add_edit_rectangle_button.grid(row=0, column=0, padx=5, pady=5)

            # Add new button for adding points
            self.add_point_button = tk.Button(self.button_frame, text="Add Point", command=self.prompt_add_point)
            self.add_point_button.grid(row=0, column=1, padx=5, pady=5)

            # Move shape button
            self.move_shape_button = tk.Button(self.button_frame, text="Move Shape", command=self.prompt_move_shape)
            self.move_shape_button.grid(row=0, column=2, padx=5, pady=5)  # Adjust row and column as needed
            
            # Second row of buttons
            self.connect_shapes_button = tk.Button(self.button_frame, text="Connect Shapes", command=self.prompt_connect_shapes)
            self.connect_shapes_button.grid(row=1, column=0, padx=5, pady=5)
            
            self.disconnect_shapes_button = tk.Button(self.button_frame, text="Disconnect Shapes", command=self.prompt_disconnect_shapes)
            self.disconnect_shapes_button.grid(row=1, column=1, padx=5, pady=5)
            
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

            self.toggle_all_points_visibility_button = tk.Button(self.button_frame, text="Toggle All Points Visibility", command=self.toggle_all_points_visibility)
            self.toggle_all_points_visibility_button.grid(row=2, column=2, padx=5, pady=5) 

            # Add the simulation toggle button
            self.simulate_button = tk.Button(self.button_frame, text="Simulation: ON", command=self.toggle_simulation)
            self.simulate_button.grid(row=3, column=0, padx=5, pady=5)



    def toggle_simulation(self):
        self.simulating = not self.simulating
        GPIO.set_simulating(self.simulating) 
        status = "ON" if self.simulating else "OFF"
        print(f"Simulation mode is now {status}")
        self.simulate_button.config(text=f"Simulation: {status}")
        
        if not self.simulating:
            # Set consistent mock values when turning simulation off
            for rect in self.rectangles.values():
                if rect.gpio is not None:
                    rect.set_mock_gpio(GPIO.LOW) 
        
        self.update_all_rectangles()

    def update_all_rectangles(self):
            for rect in self.rectangles.values():
                if rect.gpio is not None:
                    value = rect.get_gpio_state(self.simulating)
                    if value is not None:
                        rect.set_signal("red", value == GPIO.HIGH)
                        rect.draw(self.canvas)


    def load_default_canvas(self):
        try:
            self.load_canvas(self.default_canvas_file)
            print(f"Default canvas loaded from {self.default_canvas_file}")
        except Exception as e:
            print(f"Error loading default canvas: {str(e)}")
            print("Creating initial setup instead.")
            self.create_initial_setup()

    def create_initial_setup(self):
        # Create default shapes
        r1 = Rectangle("r1", 100, 100, 150, 80)
        r2 = Rectangle("r2", 350, 300, 200, 100)
        r3 = Rectangle("r3", 600, 500, 150, 80)
        p1 = Point("p1", 200, 200)
        p2 = Point("p2", 500, 400)

        for rect in [r1, r2, r3]:
            self.rectangles[rect.name] = rect
            rect.draw(self.canvas)

        for point in [p1, p2]:
            self.points[point.name] = point
            point.draw(self.canvas)

        self.connect_shapes("r1", "r2")
        self.connect_shapes("r2", "r3")
        self.connect_shapes("p1", "r2")
        self.connect_shapes("p2", "r3")

        print("Default initial setup created")


    def load_canvas_dialog(self):
        print('HERE')
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.load_canvas(file_path)

    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        canvas_state = {
            "rectangles": [],
            "points": [],
            "lines": []
        }

        for rect in self.rectangles.values():
            canvas_state["rectangles"].append({
                "name": rect.name,
                "x": rect.x,
                "y": rect.y,
                "width": rect.width,
                "height": rect.height,
                "gpio": rect.gpio,  # Add this line to save the GPIO value
                "points_swapped": rect.points_swapped,
                "red_signal": rect.red_signal,
                "blue_signal": rect.blue_signal,
                "yellow_signal": rect.yellow_signal
            })

        for point in self.points.values():
            canvas_state["points"].append({
                "name": point.name,
                "x": point.x,
                "y": point.y,
                "is_visible": point.is_visible
            })

        for line in self.lines.values():
            canvas_state["lines"].append({
                "name": line.name,
                "start_shape": line.start_shape.name,
                "end_shape": line.end_shape.name,
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
                gpio = rect_data.get("gpio")
                if gpio == 0:
                    gpio = None
                rect = Rectangle(
                    rect_data["name"],
                    rect_data["x"],
                    rect_data["y"],
                    rect_data["width"],
                    rect_data["height"],
                    gpio
                )
                rect.points_swapped = rect_data["points_swapped"]
                rect.red_signal = rect_data.get("red_signal", False)
                rect.blue_signal = rect_data.get("blue_signal", False)
                rect.yellow_signal = rect_data.get("yellow_signal", False)
                rect.update_connection_points()
                self.rectangles[rect.name] = rect
                rect.draw(self.canvas)

            for point_data in canvas_state.get("points", []):
                point = Point(point_data["name"], point_data["x"], point_data["y"])
                point.is_visible = point_data.get("is_visible", True)
                self.points[point.name] = point
                if point.is_visible:
                    point.draw(self.canvas)

            for line_data in canvas_state["lines"]:
                start_shape = self.rectangles.get(line_data["start_shape"]) or self.points.get(line_data["start_shape"])
                end_shape = self.rectangles.get(line_data["end_shape"]) or self.points.get(line_data["end_shape"])
                if start_shape and end_shape:
                    line = Line(line_data["name"], start_shape, end_shape, line_data["start_is_output"])
                    self.lines[line.name] = line
                    line.draw(self.canvas)

            print(f"Canvas state loaded from {file_path}")
        except Exception as e:
            print(f"Error loading canvas from {file_path}: {str(e)}")


    def clear_canvas(self):
        self.canvas.delete("all")
        self.rectangles.clear()
        self.lines.clear()

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
        gpio = simpledialog.askinteger("Input", f"Enter GPIO pin for {name} (or 0 for none):", parent=self.master, initialvalue=rectangle.gpio if rectangle else 0)
        
        if gpio == 0:
            gpio = None

        if all(value is not None for value in (x, y, width, height)):
            if rectangle:
                rectangle.x, rectangle.y, rectangle.width, rectangle.height = x, y, width, height
                rectangle.update_gpio(gpio)
                rectangle.update_connection_points()
            else:
                rectangle = Rectangle(name, x, y, width, height, gpio)
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

    def prompt_disconnect_shapes(self):
        if not self.lines:
            print("No connections to remove. Please connect some shapes first.")
            return

        shape1_name = simpledialog.askstring("Input", "Enter the name of the first shape:", parent=self.master)
        shape2_name = simpledialog.askstring("Input", "Enter the name of the second shape:", parent=self.master)

        line_name = f"Line_{shape1_name}_to_{shape2_name}"
        reverse_line_name = f"Line_{shape2_name}_to_{shape1_name}"

        if line_name in self.lines:
            self.canvas.delete(self.lines[line_name].canvas_item)
            del self.lines[line_name]
            print(f"Disconnected {shape1_name} from {shape2_name}")
        elif reverse_line_name in self.lines:
            self.canvas.delete(self.lines[reverse_line_name].canvas_item)
            del self.lines[reverse_line_name]
            print(f"Disconnected {shape2_name} from {shape1_name}")
        else:
            print(f"No connection found between {shape1_name} and {shape2_name}")

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
        
        for shape in list(self.rectangles.values()) + list(self.points.values()):
            if isinstance(shape, Rectangle):
                if shape.x <= event.x <= shape.x + shape.width and shape.y <= event.y <= shape.y + shape.height:
                    self.dragged_shape = shape
                    self.drag_start_x = event.x - shape.x
                    self.drag_start_y = event.y - shape.y
                    break
            elif isinstance(shape, Point):
                if shape.x - 5 <= event.x <= shape.x + 5 and shape.y - 5 <= event.y <= shape.y + 5:
                    self.dragged_shape = shape
                    self.drag_start_x = event.x - shape.x
                    self.drag_start_y = event.y - shape.y
                    break

    def on_drag(self, event):
        if self.live_mode or not self.dragged_shape:
            return
        
        new_x = event.x - self.drag_start_x
        new_y = event.y - self.drag_start_y
        
        self.dragged_shape.move_to(new_x, new_y)
        self.dragged_shape.draw(self.canvas)
        
        # Update connected lines
        self.update_connected_lines(self.dragged_shape)

    def on_release(self, event):
        if self.live_mode:
            return
        self.dragged_shape = None

    def remove_connections(self, shape_name):
        shape = self.rectangles.get(shape_name) or self.points.get(shape_name)
        lines_to_remove = []
        for line_name, line in self.lines.items():
            if line.start_shape == shape or line.end_shape == shape:
                self.canvas.delete(line.canvas_item)
                lines_to_remove.append(line_name)
        for line_name in lines_to_remove:
            del self.lines[line_name]

    def reconnect(self, shape_name, connected_info):
        shape = self.get_shape_by_name(shape_name)
        if not shape:
            print(f"Error reconnecting: shape '{shape_name}' not found")
            return

        for connected_shape, is_output, line_name in connected_info:
            if is_output:
                self.connect_shapes(shape.name, connected_shape.name)
            else:
                self.connect_shapes(connected_shape.name, shape.name)


    def get_connected_with_info(self, shape_name):
        shape = self.get_shape_by_name(shape_name)
        if not shape:
            print(f"No shape named '{shape_name}' found.")
            return []

        connected = []

        for line in self.lines.values():
            if line.start_shape == shape:
                connected.append((line.end_shape, True, line.name))
            elif line.end_shape == shape:
                connected.append((line.start_shape, False, line.name))

        return connected
    
    def get_shape_by_name(self, name):
        return self.rectangles.get(name) or self.points.get(name)

    def update_connected_lines(self, shape):
        for line in self.lines.values():
            if line.start_shape == shape or line.end_shape == shape:
                line.update_coordinates()
                line.draw(self.canvas)

    def update_canvas(self):
        self.canvas.delete("all")  # Clear the canvas
        self.draw_all_lines()
        self.redraw_all_rectangles()
        self.redraw_all_points()

    def redraw_all_points(self):
        for point in self.points.values():
            if point.is_visible:
                point.draw(self.canvas)

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
            new_signal = not current_signal
            rect.set_signal(color, new_signal)
            
            # Update the GPIO state (real or simulated)
            if rect.gpio is not None:
                if self.simulating:
                    # Update the simulated GPIO state
                    rect.set_mock_gpio(GPIO.HIGH if new_signal else GPIO.LOW)
                else:
                    rect.set_mock_gpio(GPIO.HIGH if new_signal else GPIO.LOW)
            
            rect.draw(self.canvas)
            print(f"Toggled {color} signal for {rect_name} to {new_signal}")
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

    def prompt_add_point(self):
        name = simpledialog.askstring("Input", "Enter the name of the point:", parent=self.master)
        if name is None or name.strip() == "":
            print("Operation cancelled or invalid name.")
            return
        
        x = simpledialog.askinteger("Input", f"Enter x coordinate for {name}:", parent=self.master)
        y = simpledialog.askinteger("Input", f"Enter y coordinate for {name}:", parent=self.master)
        
        if x is not None and y is not None:
            point = Point(name, x, y)
            self.points[name] = point
            point.draw(self.canvas)
            print(f"Point '{name}' created at ({x}, {y}).")
        else:
            print("Operation cancelled or invalid input.")

    def prompt_connect_shapes(self):
        if len(self.rectangles) + len(self.points) < 2:
            print("You need at least two shapes to connect. Please create more shapes.")
            return

        shape1_name = simpledialog.askstring("Input", "Enter the name of the first shape:", parent=self.master)
        shape2_name = simpledialog.askstring("Input", "Enter the name of the second shape:", parent=self.master)

        self.connect_shapes(shape1_name, shape2_name)

    def connect_shapes(self, shape1_name, shape2_name):
        shape1 = self.get_shape_by_name(shape1_name)
        shape2 = self.get_shape_by_name(shape2_name)

        if not shape1 or not shape2:
            print(f"Cannot connect: one or both shapes not found.")
            return

        line_name = f"Line_{shape1_name}_to_{shape2_name}"
        new_line = Line(line_name, shape1, shape2, True)
        self.lines[line_name] = new_line
        new_line.draw(self.canvas)
        print(f"Connected {shape1_name} to {shape2_name}")

    def toggle_all_points_visibility(self):
        if not self.points:
            print("No points to toggle visibility.")
            return

        # Determine the new visibility state based on the first point
        new_visibility = not next(iter(self.points.values())).is_visible

        for point in self.points.values():
            point.is_visible = new_visibility

        self.update_canvas()
        visibility = "visible" if new_visibility else "hidden"
        print(f"All points are now {visibility}.")


    def start_gpio_polling(self):
        if not self.polling:
            self.polling = True
            self.poll_thread = Thread(target=self.poll_gpio)
            self.poll_thread.daemon = True
            self.poll_thread.start()

    def stop_gpio_polling(self):
        self.polling = False
        if self.poll_thread and self.poll_thread.is_alive():
            self.poll_thread.join(timeout=1)

    def poll_gpio(self):
        while self.polling:
            for rect in self.rectangles.values():
                if rect.gpio is not None:
                    value = rect.get_gpio_state(self.simulating)
                    if value is not None:
                        rect.set_signal("red", value == GPIO.HIGH)
                        self.master.after(0, rect.draw, self.canvas)
            sleep(1)


    def cleanup(self):
        print("Starting cleanup...")
        self.stop_gpio_polling()
        print("GPIO polling stopped.")
        
        print("Cleaning up GPIO...")
        GPIO.cleanup()
        
        print("Destroying Tkinter window...")
        self.master.quit()
        self.master.destroy()
        
        print("Exiting application...")
        sys.exit(0)



if __name__ == "__main__":
    live_mode = "--live" in sys.argv
    load_file = True

    for arg in sys.argv:
        if arg.startswith("--load="):
            load_file = arg.split("=")[1]
            break

    root = tk.Tk()
    app = None

    try:
        app = DrawingApp(root, live_mode=live_mode, load_file=load_file)
        
        def on_closing():
            if app:
                try:
                    app.cleanup()
                except Exception as e:
                    print(f"Error during cleanup: {e}")
                    import traceback
                    traceback.print_exc()
            root.destroy()
            sys.exit(0)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error during application execution: {e}")
        import traceback
        traceback.print_exc()
        if app:
            app.cleanup()
        else:
            root.destroy()
        sys.exit(1)