import tkinter as tk

from PIL import Image, ImageTk
from openstuder import SIStatus

from installation import PropertyCategory
from uielements import DashboardPage, Button


class BatteryDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Battery.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = Button(self, 'img/BackButton.png', callback=lambda: self._change_to_frame('overview'))
        self.__back_button.place(x=20, y=12, width=46, height=46)

        self.__power = tk.StringVar()
        self.__power.set('...')
        self.__power_label = tk.Label(self, textvariable=self.__power, font=self._default_font(size=32), bg='#DDEBF0', fg='black')
        self.__power_label.place(x=261, y=151, width=158, height=46)

        self.__voltage = tk.StringVar()
        self.__voltage.set('...')
        self.__voltage_label = tk.Label(self, textvariable=self.__voltage, font=self._default_font(size=32), bg='#DDEBF0', fg='black')
        self.__voltage_label.place(x=560, y=151, width=158, height=46)

        self.__current = tk.StringVar()
        self.__current.set('...')
        self.__current_label = tk.Label(self, textvariable=self.__current, font=self._default_font(size=32), bg='#DDEBF0', fg='black')
        self.__current_label.place(x=261, y=265, width=158, height=46)

        self.__charge = tk.StringVar()
        self.__charge.set('...')
        self.__charge_label = tk.Label(self, textvariable=self.__charge, font=self._default_font(size=32), bg='#DDEBF0', fg='black')
        self.__charge_label.place(x=560, y=265, width=158, height=46)

        self.__temperature = tk.StringVar()
        self.__temperature.set('...')
        self.__temperature_label = tk.Label(self, textvariable=self.__temperature, font=self._default_font(size=32), bg='#DDEBF0', fg='black')
        self.__temperature_label.place(x=261, y=377, width=158, height=46)

        self.__battery_level_indicator = tk.Canvas(self, bg='white', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__battery_level_indicator.place(x=71, y=161, width=98, height=246)
        self.__battery_indicator_bars = -1
        self.__update_battery_indicator(0)

    def _activate(self, installation):
        self.__installation = installation

        properties = installation.get_property_ids(
            PropertyCategory.BATTERY_POWER |
            PropertyCategory.BATTERY_CHARGE |
            PropertyCategory.BATTERY_CURRENT |
            PropertyCategory.BATTERY_TEMPERATURE |
            PropertyCategory.BATTERY_VOLTAGE
        )

        self.client.read_properties(properties)
        self.client.subscribe_to_properties(properties)

    def _deactivate(self):
        self.client.unsubscribe_from_properties(self.__installation.get_property_ids(
            PropertyCategory.BATTERY_POWER |
            PropertyCategory.BATTERY_CHARGE |
            PropertyCategory.BATTERY_CURRENT |
            PropertyCategory.BATTERY_TEMPERATURE |
            PropertyCategory.BATTERY_VOLTAGE
        ))

    def on_property_updated(self, property_id, value):
        self.__installation.set_property_value(property_id, value)
        self.__update_values()

    def on_properties_read(self, results):
        for result in results:
            if result.status == SIStatus.SUCCESS:
                self.__installation.set_property_value(result.id, result.value)
        self.__update_values()

    def __update_values(self):
        self.__power.set(DashboardPage.format_float_value(self.__installation.battery_get_power(), max_decimals=2))
        self.__voltage.set(DashboardPage.format_float_value(self.__installation.battery_get_voltage(), max_decimals=2))
        self.__current.set(DashboardPage.format_float_value(self.__installation.battery_get_current(), max_decimals=2))
        self.__temperature.set(DashboardPage.format_float_value(self.__installation.battery_get_temperature(), max_decimals=1))

        battery_charge = self.__installation.battery_get_charge()
        self.__charge.set(DashboardPage.format_float_value(battery_charge, max_decimals=0))
        self.__update_battery_indicator(battery_charge)

    def __update_battery_indicator(self, level):
        bars = int(level / 10)
        if self.__battery_indicator_bars != bars:
            self.__battery_indicator_bars = bars
            self.__battery_level_indicator.delete('all')
            for i in range(10):
                if (10 - i) <= bars:
                    color = '#4B8CA3'
                else:
                    color = '#C2DBE4'
                self.__battery_level_indicator.create_line(0, 14 + i * 24, 98, 14 + i * 24, width=12, fill=color)
