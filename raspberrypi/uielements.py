import datetime
import sys
import tkinter as tk
from tkinter import font as tkft
from tkinter import messagebox as tkmb

from PIL import ImageTk, Image
from openstuder import SIAsyncGatewayClientCallbacks, SIStatus


class Button(tk.Label):
    def __init__(self, parent, image, callback=None):
        self.__callback = callback
        self.__image_render = ImageTk.PhotoImage(Image.open(image))
        super(Button, self).__init__(parent, image=self.__image_render)
        self.bind('<Button-1>', self.__on_click)

    def __on_click(self, _):
        if callable(self.__callback):
            self.__callback()


class Switch(tk.Label):
    def __init__(self, parent, image_on, image_off, initial_state=True, callback=None):
        # Save properties.
        self.__state = initial_state
        self.__callback = callback

        # Load images.
        self.__image_on_render = ImageTk.PhotoImage(Image.open(image_on))
        self.__image_off_render = ImageTk.PhotoImage(Image.open(image_off))

        # Call superclass constructor.
        super(Switch, self).__init__(parent, image=(self.__image_on_render if initial_state else self.__image_off_render))

        # Register for mouse event.
        self.bind('<Button-1>', self.__on_click)

    def state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state
        self.config(image=(self.__image_on_render if self.__state else self.__image_off_render))

    def __on_click(self, _):
        if callable(self.__callback):
            self.__callback(self)


class DashboardPage(tk.Frame, SIAsyncGatewayClientCallbacks):
    def __init__(self, parent, client):
        super(DashboardPage, self).__init__(parent)

        available_fonts = tkft.families()
        if 'Arial' in available_fonts:
            self.__default_font = 'Arial'
        elif 'Liberation Sans' in available_fonts:
            self.__default_font = 'Liberation Sans'
        else:
            self.__default_font = 'Sans'

        if sys.platform == 'darwin':
            self.__size_factor = 1
        else:
            self.__size_factor = 0.75

        self.__main = parent.master
        self.client = client
        self._setup_ui()
        self.grid(row=0, column=0, sticky="nsew")

        self.__time = tk.StringVar()
        self.__update_time()
        self.__time_label = tk.Label(self, textvariable=self.__time, font=self._default_font(weight='normal'), bg='white', fg='black', anchor=tk.W)
        self.__time_label.place(x=25, y=600, width=400, height=20)

    def _default_font(self, size=16, weight='bold'):
        return tkft.Font(family=self.__default_font, size=int(size*self.__size_factor), weight=weight)

    def _setup_ui(self):
        raise NotImplementedError()

    def _activate(self, system_info):
        raise NotImplementedError()

    def _deactivate(self):
        raise NotImplementedError()

    def _change_to_frame(self, frame_name):
        self.__main.change_to_frame(frame_name)

    def on_property_read(self, status, property_id, value):
        if status == SIStatus.SUCCESS:
            self.on_property_updated(property_id, value)

    def on_properties_read(self, results):
        for result in results:
            self.on_property_read(result.status, result.id, result.value)

    def on_error(self, reason):
        tkmb.showerror("Client error", reason)

    @staticmethod
    def format_float_value(value, max_digits=5, max_decimals=None):
        string = str(value)
        digit_count = len(string)
        point_index = string.find(".")
        if point_index == -1:
            return string
        digit_count -= 1
        if digit_count <= max_digits:
            return string
        cut_at = max(max_digits + 1, point_index)
        if max_decimals is not None:
            if max_decimals == 0:
                cut_at = min(cut_at, point_index)
            else:
                cut_at = min(cut_at, point_index + max_decimals + 1)
        return string[0:cut_at]

    def __update_time(self):
        self.__time.set(datetime.datetime.now().strftime('%A, %d.%m.%Y %H:%M'))
        self.after(5000, self.__update_time)
