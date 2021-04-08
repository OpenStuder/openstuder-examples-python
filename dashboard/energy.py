import tkinter as tk

from PIL import Image, ImageTk
from openstuder import SIStatus

from installation import Installation, PropertyCategory
from uielements import DashboardPage, Button


class EnergyDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Energy.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = Button(self, 'img/BackButton.png', callback=lambda: self._change_to_frame('overview'))
        self.__back_button.place(x=24, y=24, width=46, height=46)

        self.__solar_production_today = tk.StringVar()
        self.__solar_production_today.set('-')
        self.__solar_production_today_label = tk.Label(self, textvariable=self.__solar_production_today, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__solar_production_today_label.place(x=44, y=255, width=148, height=44)

        self.__solar_production_yesterday = tk.StringVar()
        self.__solar_production_yesterday.set('-')
        self.__solar_production_yesterday_label = tk.Label(self, textvariable=self.__solar_production_yesterday, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__solar_production_yesterday_label.place(x=44, y=428, width=148, height=44)

        self.__grid_today = tk.StringVar()
        self.__grid_today.set('...')
        self.__grid_today_label = tk.Label(self, textvariable=self.__grid_today, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__grid_today_label.place(x=292, y=255, width=148, height=44)

        self.__grid_yesterday = tk.StringVar()
        self.__grid_yesterday.set('...')
        self.__grid_yesterday_label = tk.Label(self, textvariable=self.__grid_yesterday, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__grid_yesterday_label.place(x=292, y=428, width=148, height=44)

        self.__consumption_today = tk.StringVar()
        self.__consumption_today.set('...')
        self.__consumption_today_label = tk.Label(self, textvariable=self.__consumption_today, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__consumption_today_label.place(x=786, y=255, width=148, height=44)

        self.__consumption_yesterday = tk.StringVar()
        self.__consumption_yesterday.set('...')
        self.__consumption_yesterday_label = tk.Label(self, textvariable=self.__consumption_yesterday, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__consumption_yesterday_label.place(x=786, y=428, width=148, height=44)

        self.__battery_charged_today = tk.StringVar()
        self.__battery_charged_today.set('...')
        self.__battery_charged_today_label = tk.Label(self, textvariable=self.__battery_charged_today, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__battery_charged_today_label.place(x=539, y=255, width=148, height=44)

        self.__battery_charged_yesterday = tk.StringVar()
        self.__battery_charged_yesterday.set('...')
        self.__battery_charged_yesterday_label = tk.Label(self, textvariable=self.__battery_charged_yesterday, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__battery_charged_yesterday_label.place(x=539, y=341, width=148, height=44)

        self.__battery_discharged_today = tk.StringVar()
        self.__battery_discharged_today.set('...')
        self.__battery_discharged_today_label = tk.Label(self, textvariable=self.__battery_discharged_today, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__battery_discharged_today_label.place(x=539, y=428, width=148, height=44)

        self.__battery_discharged_yesterday = tk.StringVar()
        self.__battery_discharged_yesterday.set('...')
        self.__battery_discharged_yesterday_label = tk.Label(self, textvariable=self.__battery_discharged_yesterday, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__battery_discharged_yesterday_label.place(x=539, y=514, width=148, height=44)

    def _activate(self, installation):
        self.__installation = installation

        properties = installation.get_property_ids(
            PropertyCategory.PV_ENERGY_STATS |
            PropertyCategory.GRID_ENERGY_STATS |
            PropertyCategory.OUTPUT_ENERGY_STATS |
            PropertyCategory.BATTERY_ENERGY_STATS
        )

        self.client.read_properties(properties)

    def _deactivate(self):
        pass

    def on_properties_read(self, results):
        for result in results:
            if result.status == SIStatus.SUCCESS:
                self.__installation.set_property_value(result.id, result.value)

        self.__solar_production_today.set(DashboardPage.format_float_value(self.__installation.pv_get_energy_today(), max_digits=6, max_decimals=2))
        self.__solar_production_yesterday.set(DashboardPage.format_float_value(self.__installation.pv_get_energy_yesterday(), max_digits=6, max_decimals=2))
        self.__grid_today.set(DashboardPage.format_float_value(self.__installation.grid_get_energy_today(), max_digits=6, max_decimals=2))
        self.__grid_yesterday.set(DashboardPage.format_float_value(self.__installation.grid_get_energy_yesterday(), max_digits=6, max_decimals=2))
        self.__consumption_today.set(DashboardPage.format_float_value(self.__installation.output_get_energy_today(), max_digits=6, max_decimals=2))
        self.__consumption_yesterday.set(DashboardPage.format_float_value(self.__installation.output_get_energy_yesterday(), max_digits=6, max_decimals=2))
        self.__battery_charged_today.set(DashboardPage.format_float_value(self.__installation.battery_get_charge_today(), max_decimals=2))
        self.__battery_charged_yesterday.set(DashboardPage.format_float_value(self.__installation.battery_get_charge_yesterday(), max_decimals=2))
        self.__battery_discharged_today.set(DashboardPage.format_float_value(self.__installation.battery_get_discharge_today(), max_decimals=2))
        self.__battery_discharged_yesterday.set(DashboardPage.format_float_value(self.__installation.battery_get_discharge_yesterday(), max_decimals=2))