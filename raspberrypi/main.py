import tkinter as tk
from openstuder import SIAsyncGatewayClientCallbacks, SIAsyncGatewayClient

from battery import BatteryDashboardPage
from connect import ConnectDashboardPage
from energy import EnergyDashboardPage
from messages import MessagesDashboardPage
from overview import OverviewDashboardPage


class MainWindow(tk.Tk, SIAsyncGatewayClientCallbacks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = SIAsyncGatewayClient()
        self.client.set_callbacks(self)

        self.installation = None

        self.title("Dashboard")
        self.geometry("800x480")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.active_frame = None
        self.frames = {
            'connect': ConnectDashboardPage(container, self.client),
            'overview': OverviewDashboardPage(container, self.client),
            'battery': BatteryDashboardPage(container, self.client),
            'energy': EnergyDashboardPage(container, self.client),
            'messages': MessagesDashboardPage(container, self.client),
        }
        self.change_to_frame('connect')

    def change_to_frame(self, name):
        frame = self.frames[name]
        if frame is not None:
            if self.active_frame is not None:
                try:
                    self.active_frame._deactivate()
                except Exception as exception:
                    print(exception)
            self.active_frame = frame
            try:
                frame._activate(self.installation)
            except Exception as exception:
                print(exception)
            frame.tkraise()

    def on_connected(self, access_level, gateway_version):
        self.active_frame.on_connected(access_level, gateway_version)

    def on_disconnected(self):
        self.active_frame.on_disconnected()

    def on_enumerated(self, status, device_count):
        self.active_frame.on_enumerated(status, device_count)

    def on_description(self, status, id_, description):
        self.active_frame.on_description(status, id_, description)

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
