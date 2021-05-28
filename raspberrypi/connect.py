import tkinter as tk
from tkinter import messagebox as tkmb

from PIL import Image, ImageTk
from openstuder import SIConnectionState, SIAccessLevel, SIStatus, SIDescriptionFlags

from installation import Xcom485IInstallation, DemoInstallation
from uielements import DashboardPage, Button, Switch


class ConnectDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Connecting.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

    def _activate(self, system_info):
        self.client.connect("192.168.1.121")

    def _deactivate(self):
        pass

    def on_connected(self, access_level, gateway_version):
        self.client.enumerate()

    def on_disconnected(self):
        pass

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
        self._change_to_frame('overview')
