import datetime
import tkinter as tk
from tkinter import messagebox as tkmb
from openstuder import SIAsyncGatewayClientCallbacks, SIAsyncGatewayClient, SIStatus, SIConnectionState, SIAccessLevel
from PIL import Image, ImageTk


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


class DashboardButton(tk.Label):
    def __init__(self, parent, image, callback=None):
        self.__callback = callback
        self.__image_render = ImageTk.PhotoImage(Image.open(image))
        super(DashboardButton, self).__init__(parent, image=self.__image_render)
        self.bind('<Button-1>', self.__on_click)

    def __on_click(self, _):
        if callable(self.__callback):
            self.__callback()


class DashboardSwitch(tk.Label):
    def __init__(self, parent, image_on, image_off, initial_state=True, callback=None):
        # Save properties.
        self.__state = initial_state
        self.__callback = callback

        # Load images.
        self.__image_on_render = ImageTk.PhotoImage(Image.open(image_on))
        self.__image_off_render = ImageTk.PhotoImage(Image.open(image_off))

        # Call superclass constructor.
        super(DashboardSwitch, self).__init__(parent, image=(self.__image_on_render if initial_state else self.__image_off_render))

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


class DashboardFrame(tk.Frame, SIAsyncGatewayClientCallbacks):
    def __init__(self, parent, client):
        super(DashboardFrame, self).__init__(parent)
        self.__main = parent.master
        self.client = client
        self.setup_ui()
        self.grid(row=0, column=0, sticky="nsew")

        self.__time = tk.StringVar()
        self.__update_time()
        self.__time_label = tk.Label(self, textvariable=self.__time, font='Arial 16', bg='white', fg='black', anchor=tk.W)
        self.__time_label.place(x=25, y=600, width=400, height=20)

    def setup_ui(self):
        raise NotImplementedError()

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def change_to_frame(self, frame_name):
        self.__main.change_to_frame(frame_name)

    def on_property_read(self, status, property_id, value):
        if status == SIStatus.SUCCESS:
            self.on_property_updated(property_id, value)

    def on_properties_read(self, results):
        for result in results:
            self.on_property_read(result.status, result.id, result.value)

    def on_error(self, reason):
        tkmb.showerror("Client error", reason)

    def __update_time(self):
        self.__time.set(datetime.datetime.now().strftime('%A, %d.%m.%Y %H:%M'))
        self.after(5000, self.__update_time)


class OverviewDashboardFrame(DashboardFrame):
    def setup_ui(self):
        dashboard_image = Image.open('img/Dashboard.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        solar_image = Image.open('img/DashboardSolar.png')
        self.__solar_background_render = ImageTk.PhotoImage(solar_image)
        self.__solar_label = tk.Label(self, image=self.__solar_background_render)
        self.__solar_label.place(x=451, y=123, width=122, height=180)

        self._on_off_button = DashboardSwitch(self, 'img/PowerButtonOn.png', 'img/PowerButtonOff.png', callback=self.__on_power_button_clicked)
        self._on_off_button.place(x=24, y=24, width=46, height=46)

        self.__energy_button = DashboardButton(self, 'img/EnergyButton.png', callback=lambda: self.change_to_frame('energy'))
        self.__energy_button.place(x=783, y=24, width=46, height=46)

        self.__battery_button = DashboardButton(self, 'img/BatteryButton.png', callback=lambda: self.change_to_frame('battery'))
        self.__battery_button.place(x=840, y=24, width=46, height=46)

        self.__messages_button = DashboardButton(self, 'img/MessagesButton.png', callback=self.__on_messages_button_clicked)
        self.__messages_button.place(x=897, y=24, width=46, height=46)

        self.__settings_button = DashboardSwitch(self, 'img/ConnectedButton.png', 'img/NotConnectedButton.png', callback=lambda _: self.change_to_frame('connection'))
        self.__settings_button.place(x=954, y=24, width=46, height=46)

        self.__ac_charge_power = tk.StringVar()
        self.__ac_charge_power.set('...')
        self.__ac_charge_power_label = tk.Label(self, textvariable=self.__ac_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black')
        self.__ac_charge_power_label.place(x=243, y=317, width=82, height=28)

        self.__pv_charge_power = tk.StringVar()
        self.__pv_charge_power.set('...')
        self.__pv_charge_power_label = tk.Label(self, textvariable=self.__pv_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black')
        self.__pv_charge_power_label.place(x=454, y=137, width=82, height=28)

        self.__consumed_power = tk.StringVar()
        self.__consumed_power.set('...')
        self.__consumed_power_label = tk.Label(self, textvariable=self.__consumed_power, font='Arial 20 bold', bg='#DDEBF0', fg='black')
        self.__consumed_power_label.place(x=664, y=317, width=82, height=28)

        self.__battery_charge_power = tk.StringVar()
        self.__battery_charge_power.set('...')
        self.__battery_charge_power_label = tk.Label(self, textvariable=self.__battery_charge_power, font='Arial 20 bold', bg='#DDEBF0', fg='black')
        self.__battery_charge_power_label.place(x=454, y=488, width=82, height=28)

        self.__battery_level = tk.StringVar()
        self.__battery_level.set('...')
        self.__battery_level_label = tk.Label(self, textvariable=self.__battery_level, font='Arial 20 bold', bg='#DDEBF0', fg='black')
        self.__battery_level_label.place(x=454, y=512, width=82, height=28)

        self.__battery_level_indicator = tk.Canvas(self, bg='#DDEBF0', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__battery_level_indicator.place(x=501, y=549, width=16, height=40)
        self.__update_battery_indicator(0)

        self.__xtender_count = tk.StringVar()
        self.__xtender_count.set('?')
        self.__xtender_count_label = tk.Label(self, textvariable=self.__xtender_count, font='Arial 13 bold', bg='#DDEBF0', fg='black')
        self.__xtender_count_label.place(x=537, y=407, width=11, height=15)

        self.__new_messages_count = tk.IntVar()
        self.__new_messages_count.set(0)
        self.__new_messages_count_label = tk.Label(self, textvariable=self.__new_messages_count, font='Arial 11 bold', bg='white', fg='#4B8CA3')
        self.__new_messages_count_label.place(x=927, y=55, width=13, height=12)

    def activate(self):
        if self.client.state() == SIConnectionState.CONNECTED:
            self.on_connected(SIAccessLevel.NONE, '')
        else:
            self.on_disconnected()

        properties = [
            'xcom.xt1.3049',
            'xcom.xt1.3136',
            'xcom.xt1.3137',
            'xcom.bat.7002',
            'xcom.bat.7003',
            'xcom.vt1.11004',
            'xcom.vs1.15010'
        ]
        self.client.read_properties(properties)
        self.client.subscribe_to_properties(properties)

    def deactivate(self):
        self.client.unsubscribe_from_properties([
            'xcom.xt1.3049',
            'xcom.xt1.3136',
            'xcom.xt1.3137',
            'xcom.bat.7002',
            'xcom.bat.7003',
            'xcom.vt1.11004',
            'xcom.vs1.15010'
        ])

    def on_connected(self, access_level, gateway_version):
        self.__settings_button.set_state(True)

    def on_disconnected(self):
        self.__settings_button.set_state(False)

    def on_property_updated(self, property_id, value):
        if property_id == 'xcom.xt1.3049':
            self._on_off_button.set_state(value == 1.0)
        if property_id == 'xcom.xt1.3136':
            self.__consumed_power.set(f'{value:.3f}')
        if property_id == 'xcom.xt1.3137':
            self.__ac_charge_power.set(f'{value:.3f}')
        if property_id == 'xcom.bat.7002':
            self.__battery_level.set(f'{value:3.0f}')
            self.__update_battery_indicator(value)
        if property_id == 'xcom.bat.7003':
            self.__battery_charge_power.set(f'{value:.0f}')
        if property_id == 'xcom.bat.11004':
            self.__pv_charge_power.set(f'{value:.0f}')
        if property_id == 'xcom.bat.15010':
            self.__pv_charge_power.set(f'{value:.0f}')

    def on_device_message(self, message):
        count = self.__new_messages_count.get()
        if count < 99:
            count += 1
            self.__new_messages_count.set(count)

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
            self.client.write_property('xcom.xts.1415')
        else:
            self.client.write_property('xcom.xts.1399')
        button.set_state(not button.state())

    def __on_messages_button_clicked(self):
        self.__new_messages_count.set(0)
        self.change_to_frame('messages')


class BatteryDashboardFrame(DashboardFrame):
    def setup_ui(self):
        dashboard_image = Image.open('img/Battery.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = DashboardButton(self, 'img/BackButton.png', callback=lambda: self.change_to_frame('overview'))
        self.__back_button.place(x=24, y=24, width=46, height=46)

        self.__power = tk.StringVar()
        self.__power.set('...')
        self.__power_label = tk.Label(self, textvariable=self.__power, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__power_label.place(x=374, y=221, width=158, height=46)

        self.__voltage = tk.StringVar()
        self.__voltage.set('...')
        self.__voltage_label = tk.Label(self, textvariable=self.__voltage, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__voltage_label.place(x=673, y=221, width=158, height=46)

        self.__current = tk.StringVar()
        self.__current.set('...')
        self.__current_label = tk.Label(self, textvariable=self.__current, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__current_label.place(x=374, y=335, width=158, height=46)

        self.__charge = tk.StringVar()
        self.__charge.set('...')
        self.__charge_label = tk.Label(self, textvariable=self.__charge, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__charge_label.place(x=673, y=335, width=158, height=46)

        self.__temperature = tk.StringVar()
        self.__temperature.set('...')
        self.__temperature_label = tk.Label(self, textvariable=self.__temperature, font='Arial 36 bold', bg='#DDEBF0', fg='black')
        self.__temperature_label.place(x=374, y=447, width=158, height=46)

        self.__battery_level_indicator = tk.Canvas(self, bg='white', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__battery_level_indicator.place(x=150, y=240, width=98, height=246)
        self.__update_battery_indicator(0)

    def activate(self):
        properties = [
            'xcom.bat.7000',
            'xcom.bat.7001',
            'xcom.bat.7002',
            'xcom.bat.7003',
            'xcom.bat.7033'
        ]
        self.client.read_properties(properties)
        self.client.subscribe_to_properties(properties)

    def deactivate(self):
        self.client.unsubscribe_from_properties([
            'xcom.bat.7000',
            'xcom.bat.7001',
            'xcom.bat.7002',
            'xcom.bat.7003',
            'xcom.bat.7033'
        ])

    def on_property_updated(self, property_id, value):
        if property_id == 'xcom.bat.7003':
            self.__power.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7000':
            self.__voltage.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7001':
            self.__current.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7002':
            self.__charge.set(format_float_value(value, max_decimals=0))
            self.__update_battery_indicator(value)
        if property_id == 'xcom.bat.7033':
            self.__temperature.set(format_float_value(value, max_decimals=1))

    def __update_battery_indicator(self, level):
        self.__battery_level_indicator.delete('all')
        for i in range(10):
            if (100 - i * 10) <= level:
                color = '#4B8CA3'
            else:
                color = '#C2DBE4'
            self.__battery_level_indicator.create_line(0, 14 + i * 24, 98, 14 + i * 24, width=12, fill=color)


class EnergyDashboardFrame(DashboardFrame):
    def setup_ui(self):
        dashboard_image = Image.open('img/Energy.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = DashboardButton(self, 'img/BackButton.png', callback=lambda: self.change_to_frame('overview'))
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

    def activate(self):
        self.client.read_properties([
            'xcom.xt1.3080',
            'xcom.xt1.3081',
            'xcom.xt1.3082',
            'xcom.xt1.3083',
            'xcom.bat.7007',
            'xcom.bat.7008',
            'xcom.bat.7009',
            'xcom.bat.7010'
        ])

    def deactivate(self):
        pass

    def on_property_updated(self, property_id, value):
        if property_id == 'xcom.xt1.3080':
            self.__grid_yesterday.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.xt1.3081':
            self.__grid_today.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.xt1.3082':
            self.__consumption_yesterday.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.xt1.3083':
            self.__consumption_today.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7007':
            self.__battery_charged_today.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7009':
            self.__battery_charged_yesterday.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7008':
            self.__battery_discharged_today.set(format_float_value(value, max_decimals=2))
        if property_id == 'xcom.bat.7010':
            self.__battery_discharged_yesterday.set(format_float_value(value, max_decimals=2))


class MessagesDashboardFrame(DashboardFrame):
    def setup_ui(self):
        dashboard_image = Image.open('img/Messages.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = DashboardButton(self, 'img/BackButton.png', callback=lambda: self.change_to_frame('overview'))
        self.__back_button.place(x=24, y=24, width=46, height=46)

        self.__message_list = tk.Canvas(self, bg='#DDEBF0', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__message_list.place(x=22, y=160, width=980, height=396)

    def activate(self):
        self.client.read_messages(limit=20)

    def deactivate(self):
        pass

    def on_messages_read(self, status, count, messages):
        self.__messages = messages
        self.__update_message_canvas()

    def on_device_message(self, message):
        self.__messages.append(message)
        if len(self.__messages) > 20:
            self.__messages.pop(0)
        self.__update_message_canvas()

    def __update_message_canvas(self):
        self.__message_list.delete('all')
        for i, message in enumerate(self.__messages):
            self.__message_list.create_line(20, i * 20, 950, i * 20, width=1, fill="#549CB5")
            self.__message_list.create_text(30, 2 + i * 20, anchor=tk.NW, text=f'{message.access_id}.{message.device_id}')
            self.__message_list.create_text(166, 2 + i * 20, anchor=tk.NW, text=f'{message.message} ({message.message_id})')
            self.__message_list.create_text(815, 2 + i * 20, anchor=tk.NW, text=f'{message.timestamp}')


class ConnectionDashboardFrame(DashboardFrame):
    def setup_ui(self):
        dashboard_image = Image.open('img/Connection.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = DashboardButton(self, 'img/BackButton.png', callback=lambda: self.change_to_frame('overview'))
        #self.__back_button.place(x=24, y=24, width=46, height=46)

        self.__connection_status = DashboardSwitch(self, 'img/Connected.png', 'img/NotConnected.png')
        self.__connection_status.place(x=480, y=193, width=64, height=64)
        self.__connection_status.set_state(self.client.state() == SIConnectionState.CONNECTED)

        self.__host = tk.StringVar(self)
        self.__host.set('localhost')
        self.__host_entry = tk.Entry(self, textvariable=self.__host, font='Arial 24 bold', bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__host_entry.place(x=194, y=327, width=456, height=40)

        self.__port = tk.IntVar(self)
        self.__port.set(1987)
        self.__port_entry = tk.Entry(self, textvariable=self.__port, font='Arial 24 bold', bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__port_entry.place(x=694, y=327, width=102, height=40)

        self.__username = tk.StringVar(self)
        self.__username.set('')
        self.__username_entry = tk.Entry(self, textvariable=self.__username, font='Arial 24 bold', bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__username_entry.place(x=194, y=419, width=290, height=40)

        self.__password = tk.StringVar(self)
        self.__password.set('')
        self.__password_entry = tk.Entry(self, textvariable=self.__password, font='Arial 24 bold', bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0,
                                         insertborderwidth=0, selectborderwidth=0, show='*', disabledbackground='#DDEBF0')
        self.__password_entry.place(x=535, y=419, width=290, height=40)

        self.__button = DashboardSwitch(self, 'img/DisconnectButton.png', 'img/ConnectButton.png', callback=self.__connect_or_disconnect, initial_state=False)
        self.__button.place(x=411, y=507, width=202, height=52)

        self.on_disconnected()

    def activate(self):
        if self.client.state() == SIConnectionState.CONNECTED:
            self.on_connected(SIAccessLevel.NONE, '')
        else:
            self.on_disconnected()

    def deactivate(self):
        pass

    def on_connected(self, access_level, gateway_version):
        self.__back_button.place(x=24, y=24, width=46, height=46)
        self.__connection_status.set_state(True)
        self.__button.set_state(True)
        self.__host_entry.config(state=tk.DISABLED)
        self.__port_entry.config(state=tk.DISABLED)
        self.__username_entry.config(state=tk.DISABLED)
        self.__password_entry.config(state=tk.DISABLED)

    def on_disconnected(self):
        self.__back_button.place(x=-100, y=-100, width=0, height=0)
        self.__connection_status.set_state(False)
        self.__button.set_state(False)
        self.__host_entry.config(state=tk.NORMAL)
        self.__port_entry.config(state=tk.NORMAL)
        self.__username_entry.config(state=tk.NORMAL)
        self.__password_entry.config(state=tk.NORMAL)

    def __connect_or_disconnect(self, _):
        if self.__button.state():
            self.client.disconnect()
        else:
            self.client.connect(self.__host.get(), port=self.__port.get(), user=self.__username.get(), password=self.__password.get())


class MainWindow(tk.Tk, SIAsyncGatewayClientCallbacks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = SIAsyncGatewayClient()
        self.client.set_callbacks(self)

        self.title("Dashboard")
        self.geometry("1024x640")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.active_frame = None
        self.frames = {
            'overview': OverviewDashboardFrame(container, self.client),
            'battery': BatteryDashboardFrame(container, self.client),
            'energy': EnergyDashboardFrame(container, self.client),
            'messages': MessagesDashboardFrame(container, self.client),
            'connection': ConnectionDashboardFrame(container, self.client)
        }
        self.change_to_frame('connection')

    def change_to_frame(self, name):
        frame = self.frames[name]
        if frame is not None:
            if self.active_frame is not None:
                try:
                    self.active_frame.deactivate()
                except:
                    pass
            self.active_frame = frame
            try:
                frame.activate()
            except:
                pass
            frame.tkraise()

    def on_connected(self, access_level, gateway_version):
        self.active_frame.on_connected(access_level, gateway_version)
        print(f'Connected with access level {access_level}.')
        self.client.enumerate()

    def on_disconnected(self):
        self.active_frame.on_disconnected()

    def on_enumerated(self, status, device_count):
        print(f'Devices enumerated with status {status}, {device_count} devices present.')
        self.client.describe('xcom')

    def on_description(self, status, id, description):
        print(f'Got system description  with status {status}.')
        print(description)

    def on_property_read(self, status, property_id, value):
        self.active_frame.on_property_read(status, property_id, value)

    def on_properties_read(self, results):
        self.active_frame.on_properties_read(results)

    def on_property_updated(self, property_id, value):
        self.active_frame.on_property_updated(property_id, value)

    def on_device_message(self, message):
        self.active_frame.on_device_message(message)

    def on_messages_read(self, status, count, messages):
        self.active_frame.on_messages_read(status, count, messages)

    def on_error(self, error):
        self.active_frame.on_error(error)


mainWindow = MainWindow()
mainWindow.mainloop()
