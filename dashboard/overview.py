import tkinter as tk

from PIL import Image, ImageTk
from openstuder import SIConnectionState, SIAccessLevel, SIStatus

from installation import PropertyCategory
from uielements import DashboardPage, Switch, Button


class OverviewDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Dashboard.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__on_off_button = Switch(self, 'img/PowerButtonOn.png', 'img/PowerButtonOff.png', callback=self.__on_power_button_clicked)
        self.__on_off_button.place(x=24, y=24, width=46, height=46)

        self.__energy_button = Button(self, 'img/EnergyButton.png', callback=lambda: self._change_to_frame('energy'))
        self.__energy_button.place(x=783, y=24, width=46, height=46)

        self.__battery_button = Button(self, 'img/BatteryButton.png', callback=lambda: self._change_to_frame('battery'))
        self.__battery_button.place(x=840, y=24, width=46, height=46)

        self.__messages_button = Button(self, 'img/MessagesButton.png', callback=self.__on_messages_button_clicked)
        self.__messages_button.place(x=897, y=24, width=46, height=46)

        self.__connect_button = Switch(self, 'img/ConnectedButton.png', 'img/NotConnectedButton.png', callback=lambda _: self._change_to_frame('connection'))
        self.__connect_button.place(x=954, y=24, width=46, height=46)

        self.__ac_charge_power = tk.StringVar()
        self.__ac_charge_power.set('-')
        self.__ac_charge_power_label = tk.Label(self, textvariable=self.__ac_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black', anchor=tk.E)
        self.__ac_charge_power_label.place(x=243, y=317, width=80, height=28)

        self.__pv_charge_power = tk.StringVar()
        self.__pv_charge_power.set('-')
        self.__pv_charge_power_label = tk.Label(self, textvariable=self.__pv_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black', anchor=tk.E)
        self.__pv_charge_power_label.place(x=454, y=137, width=80, height=28)

        self.__consumed_power = tk.StringVar()
        self.__consumed_power.set('-')
        self.__consumed_power_label = tk.Label(self, textvariable=self.__consumed_power, font='Arial 20 bold', bg='#DDEBF0', fg='black', anchor=tk.E)
        self.__consumed_power_label.place(x=664, y=317, width=80, height=28)

        self.__battery_charge_power = tk.StringVar()
        self.__battery_charge_power.set('-')
        self.__battery_charge_power_label = tk.Label(self, textvariable=self.__battery_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black', anchor=tk.E)
        self.__battery_charge_power_label.place(x=454, y=488, width=82, height=28)

        self.__battery_level = tk.StringVar()
        self.__battery_level.set('-')
        self.__battery_level_label = tk.Label(self, textvariable=self.__battery_level, font='Arial 20 bold', bg='#DDEBF0', fg='black', anchor=tk.E)
        self.__battery_level_label.place(x=454, y=512, width=82, height=28)

        self.__battery_level_indicator = tk.Canvas(self, bg='#DDEBF0', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__battery_level_indicator.place(x=501, y=549, width=16, height=40)
        self.__update_battery_indicator(0)

        self.__xtender_count = tk.StringVar()
        self.__xtender_count.set('0')
        self.__xtender_count_label = tk.Label(self, textvariable=self.__xtender_count, font='Arial 13 bold', bg='#DDEBF0', fg='black')
        self.__xtender_count_label.place(x=537, y=407, width=11, height=15)

        self.__new_messages_count = tk.IntVar()
        self.__new_messages_count.set(0)
        self.__new_messages_count_label = tk.Label(self, textvariable=self.__new_messages_count, font='Arial 11 bold', bg='white', fg='#4B8CA3')
        self.__new_messages_count_label.place(x=927, y=55, width=13, height=12)

    def _activate(self, installation):
        self.__installation = installation

        if self.client.state() == SIConnectionState.CONNECTED:
            self.on_connected(SIAccessLevel.NONE, '')
        else:
            self.on_disconnected()

        self.__xtender_count.set(installation.inverter_count)

        properties = installation.get_property_ids(
            PropertyCategory.INVERTER_STATE |
            PropertyCategory.PV_POWER |
            PropertyCategory.GRID_POWER |
            PropertyCategory.OUTPUT_POWER |
            PropertyCategory.BATTERY_POWER |
            PropertyCategory.BATTERY_CHARGE
        )

        self.client.read_properties(properties)
        self.client.subscribe_to_properties(properties)

    def _deactivate(self):
        self.client.unsubscribe_from_properties(self.__installation.get_property_ids(
            PropertyCategory.INVERTER_STATE |
            PropertyCategory.PV_POWER |
            PropertyCategory.GRID_POWER |
            PropertyCategory.OUTPUT_POWER |
            PropertyCategory.BATTERY_POWER |
            PropertyCategory.BATTERY_CHARGE
        ))

    def on_connected(self, access_level, gateway_version):
        self.__connect_button.set_state(True)

    def on_disconnected(self):
        self.__connect_button.set_state(False)

    def on_property_updated(self, property_id, value):
        self.__installation.set_property_value(property_id, value)
        self.__update_values()

    def on_properties_read(self, results):
        for result in results:
            if result.status == SIStatus.SUCCESS:
                self.__installation.set_property_value(result.id, result.value)
        self.__update_values()

    def on_device_message(self, message):
        count = self.__new_messages_count.get()
        if count < 99:
            count += 1
            self.__new_messages_count.set(count)

    def __update_values(self):
        self.__on_off_button.set_state(self.__installation.inverter_get_state())

        self.__pv_charge_power.set(DashboardPage.format_float_value(self.__installation.pv_get_power(), max_decimals=3))
        self.__ac_charge_power.set(DashboardPage.format_float_value(self.__installation.grid_get_power(), max_decimals=3))
        self.__consumed_power.set(DashboardPage.format_float_value(self.__installation.output_get_power(), max_decimals=3))
        self.__battery_charge_power.set(DashboardPage.format_float_value(self.__installation.battery_get_power(), max_decimals=3))

        battery_charge = self.__installation.battery_get_charge()
        self.__battery_level.set(DashboardPage.format_float_value(battery_charge, max_digits=3, max_decimals=0))
        self.__update_battery_indicator(battery_charge)

    def __update_battery_indicator(self, level):
        self.__battery_level_indicator.delete('all')
        for i in range(10):
            if (100 - i * 10) <= level:
                color = '#4B8CA3'
            else:
                color = '#C2DBE4'
            self.__battery_level_indicator.create_line(0, 2 + i * 4, 16, 2 + i * 4, width=2, fill=color)

    def __on_power_button_clicked(self, button):
        state = not button.state()
        if state:
            self.__installation.inverter_turn_on(self.client)
        else:
            self.__installation.inverter_turn_off(self.client)
        button.set_state(state)

    def __on_messages_button_clicked(self):
        self.__new_messages_count.set(0)
        self._change_to_frame('messages')
