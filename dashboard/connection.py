import tkinter as tk
from tkinter import messagebox as tkmb

from PIL import Image, ImageTk
from openstuder import SIConnectionState, SIAccessLevel, SIStatus, SIDescriptionFlags

from installation import Xcom485IInstallation, DemoInstallation
from uielements import DashboardPage, Button, Switch


class ConnectionDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Connection.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = Button(self, 'img/BackButton.png', callback=lambda: self._change_to_frame('overview'))

        self.__connection_status = Switch(self, 'img/Connected.png', 'img/NotConnected.png')
        self.__connection_status.place(x=480, y=193, width=64, height=64)
        self.__connection_status.set_state(self.client.state() == SIConnectionState.CONNECTED)

        self.__host = tk.StringVar(self)
        self.__host.set('localhost')
        self.__host_entry = tk.Entry(self, textvariable=self.__host, font=self._default_font(size=24), bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__host_entry.place(x=194, y=327, width=456, height=40)

        self.__port = tk.IntVar(self)
        self.__port.set(1987)
        self.__port_entry = tk.Entry(self, textvariable=self.__port, font=self._default_font(size=24), bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__port_entry.place(x=694, y=327, width=102, height=40)
        self.__port_inc = Button(self, 'img/PortInc.png', callback=self.__increment_port)
        self.__port_inc.place(x=808, y=330, width=24, height=14)
        self.__port_dec = Button(self, 'img/PortDec.png', callback=self.__decrement_port)
        self.__port_dec.place(x=808, y=349, width=24, height=14)

        self.__username = tk.StringVar(self)
        self.__username.set('')
        self.__username_entry = tk.Entry(self, textvariable=self.__username, font=self._default_font(size=24), bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0,
                                     selectborderwidth=0, disabledbackground='#DDEBF0')
        self.__username_entry.place(x=194, y=419, width=290, height=40)

        self.__password = tk.StringVar(self)
        self.__password.set('')
        self.__password_entry = tk.Entry(self, textvariable=self.__password, font=self._default_font(size=24), bg='#DDEBF0', fg='black', bd=0, borderwidth=0, highlightthickness=0,
                                         insertborderwidth=0, selectborderwidth=0, show='*', disabledbackground='#DDEBF0')
        self.__password_entry.place(x=535, y=419, width=290, height=40)

        self.__button = Switch(self, 'img/DisconnectButton.png', 'img/ConnectButton.png', callback=self.__connect_or_disconnect, initial_state=False)
        self.__button.place(x=411, y=507, width=202, height=52)

        self.on_disconnected()

    def _activate(self, system_info):
        if self.client.state() == SIConnectionState.CONNECTED:
            self.on_connected(SIAccessLevel.NONE, '')
        else:
            self.on_disconnected()

    def _deactivate(self):
        pass

    def on_connected(self, access_level, gateway_version):
        self.client.enumerate()

    def on_disconnected(self):
        self.__back_button.place(x=-100, y=-100, width=0, height=0)
        self.__connection_status.set_state(False)
        self.__button.set_state(False)
        self.__host_entry.config(state=tk.NORMAL)
        self.__port_entry.config(state=tk.NORMAL)
        self.__username_entry.config(state=tk.NORMAL)
        self.__password_entry.config(state=tk.NORMAL)

    def on_enumerated(self, status, device_count):
        if status == SIStatus.SUCCESS:
            self.client.describe(flags=SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
        else:
            self.client.disconnect()
            tkmb.showerror('Enumeration error', f'Error during device enumeration: {status}')

    def on_description(self, status, id_, description):
        if status != SIStatus.SUCCESS:
            self.client.disconnect()
            tkmb.showerror('Describe error', f'Error requesting system description: {status}')
            return

        if 'instances' not in description:
            self.client.disconnect()
            tkmb.showerror('Initialize error', 'Error requesting system description: data missing')
            return

        instances = description['instances']
        if len(instances) == 0:
            self.client.disconnect()
            tkmb.showerror('Initialize error', 'Error initializing dashboards: no installation found')
            return

        if len(instances) != 1:
            self.client.disconnect()
            tkmb.showerror('Initialize error', 'Error initializing dashboards: multiple installations found')
            return

        device_access = instances[0]

        if 'driver' not in device_access:
            self.client.disconnect()
            tkmb.showerror('Initialize error', 'Error initializing dashboards: no driver information provided')
            return

        driver = device_access['driver']

        if 'devices' not in device_access:
            self.client.disconnect()
            tkmb.showerror('Initialize error', f'Error initializing dashboards: No devices')
            return

        devices = device_access['devices']

        if driver == 'Xcom485i':
            self.master.master.installation = Xcom485IInstallation(device_access['id'], devices)
        elif driver == 'Demo':
            self.master.master.installation = DemoInstallation(device_access['id'])
        else:
            self.client.disconnect()
            tkmb.showerror('Initialize error', f'Error initializing dashboards: Driver "{driver}" not supported')
            return

        self.__back_button.place(x=24, y=24, width=46, height=46)
        self.__connection_status.set_state(True)
        self.__button.set_state(True)
        self.__host_entry.config(state=tk.DISABLED)
        self.__port_entry.config(state=tk.DISABLED)
        self.__username_entry.config(state=tk.DISABLED)
        self.__password_entry.config(state=tk.DISABLED)

    def __connect_or_disconnect(self, _):
        if self.__button.state():
            self.client.disconnect()
        else:
            self.client.connect(self.__host.get(), port=self.__port.get(), user=self.__username.get(), password=self.__password.get())

    def __increment_port(self):
        if self.client.state != SIConnectionState.CONNECTED:
            self.__port.set(self.__port.get() + 1)

    def __decrement_port(self):
        if self.client.state != SIConnectionState.CONNECTED:
            self.__port.set(self.__port.get() - 1)