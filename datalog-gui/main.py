import io
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.simpledialog as tksd
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd
import center_tk_window as tkct
import openstuder
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from PIL import Image, ImageTk
import tkcalendar as tkcal
import datetime
matplotlib.use('TkAgg')


class ConnectDialog(tksd.Dialog):
    """
    Dialog asking the user for the host, port and credentials to connect to the OpenStuder gateway.
    """

    def __init__(self, parent):
        """
        Constructs and directly shows the dialog.
        """

        # Declare properties.
        self._host = None
        self._host_label = None
        self._host_entry = None
        self._port = None
        self._port_label = None
        self._port_entry = None
        self._username = None
        self._username_label = None
        self._username_entry = None
        self._password = None
        self._password_label = None
        self._password_entry = None

        # Call superclass constructor.
        super(ConnectDialog, self).__init__(parent, title='Connect...')

    def body(self, frame):
        """
        Custom dialog body, called from superclass.
        """

        # Create and setup variable, label and text entry for host.
        self._host = tk.StringVar(self, 'localhost')
        self._host_label = tk.Label(frame, text='Host')
        self._host_label.grid(row=0, column=0)
        self._host_entry = tk.Entry(frame, textvariable=self._host)
        self._host_entry.grid(row=0, column=1)

        # Create and setup variable, label and text spinbox for TCP port.
        self._port = tk.IntVar(self, 1987)
        self._port_label = tk.Label(frame, text='Port')
        self._port_label.grid(row=1, column=0)
        self._port_entry = tk.Spinbox(frame, from_=1, to=65535, textvariable=self._port)
        self._port_entry.grid(row=1, column=1)

        # Create and setup variable, label and text entry for username.
        self._username = tk.StringVar(self)
        self._username_label = tk.Label(frame, text='Username')
        self._username_label.grid(row=2, column=0)
        self._username_entry = tk.Entry(frame, textvariable=self._username)
        self._username_entry.grid(row=2, column=1)

        # Create and setup variable, label and text entry for password.
        self._password = tk.StringVar(self)
        self._password_label = tk.Label(frame, text='Password')
        self._password_label.grid(row=3, column=0)
        self._password_entry = tk.Entry(frame, textvariable=self._password)
        self._password_entry.grid(row=3, column=1)
        self._password_entry['show'] = '*'

        # Return the frame.
        return frame

    def ok(self, event=None):
        """
        Called from superclass when OK button was pressed.
        """

        super(ConnectDialog, self).ok(event)

        # Set result to true to signal that OK was pressed.
        self.result = True

    def cancel(self, event=None):
        """
        Called from superclass when Cancel button was pressed.
        """

        super(ConnectDialog, self).cancel(event)

        # Set result to false to signal that Cancel was pressed.
        self.result = False

    def host(self):
        """
        Returns the host.

        :return: Host as string.
        """

        return self._host.get()

    def port(self):
        """
        Returns the TCP port.

        :return: TCP port as integer.
        """

        return self._port.get()

    def username(self):
        """
        Returns the username or None if the entry is empty.

        :return: Username as string or None of not present.
        """

        username = self._username.get()
        if len(username) > 0:
            return username
        else:
            return None

    def password(self):
        """
        Returns the password or None if the entry is empty.

        :return: Password as string or None of not present.
        """
        password = self._password.get()
        if len(password) > 0:
            return password
        else:
            return None


class ProgressDialog(tk.Toplevel):
    """
    Simple progress dialog featuring a customizable text and the progress bar.
    """

    def __init__(self, master, text, total_steps):
        """
        Constructs and shows the progress bar.

        :param master: Parent window.
        :param text: Text to show on top of the progress bar.
        :param total_steps: Total number of steps.
        """

        super(ProgressDialog, self).__init__(master)
        self._master = master

        # Center the dialog on the parent window.
        self.minsize(300, 100)
        self.maxsize(300, 100)
        tkct.center_on_parent(master, self)

        # Place label and set text.
        self._label = tk.Label(self, text=text)
        self._label.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(10, 0) ,padx=10)

        # Place progress bar and configure it.
        self._progress = ttk.Progressbar(self, maximum=total_steps)
        self._progress.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(0, 10), padx=10)

        # Block parent window.
        self.grab_set()

        # Ensure pending events are processed.
        self._master.update()

    def step(self):
        """
        Increases the progress by one step and updates the UI.

        :return: None
        """

        # Update progress bar.
        self._progress.step(1)

        # Ensure pending events are processed.
        self._master.update()

    def finish(self):
        """
        Closes the dialog and returns controls to the parent window.

        :return: None
        """

        # Unblock parent window.
        self.grab_release()

        # Destroy the window.
        self.destroy()


class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create OpenStuder client instance.
        self._client = openstuder.SIGatewayClient()

        # Setup UI.
        self.title('OpenStuder Datalog GUI Demo')

        # Create menu to connect and disconnect from/to gateway.
        self._menu = tk.Menu(self, bg='#014289', fg='white')
        self.config(menu=self._menu)
        self._gatewayMenu = tk.Menu(bg='#014289', fg='white')
        self._menu.add_cascade(label='Gateway', menu=self._gatewayMenu)
        self._gatewayMenu.add_command(label='Connect...', command=self.on_connect_button_clicked)
        self._gatewayMenu.add_command(label='Disconnect', command=self.on_disconnect_button_clicked)
        self._gatewayMenu.entryconfig('Disconnect', state='disabled')

        # Create main container.
        self._container = tk.Frame(self)
        self._container.pack(fill=tk.BOTH, expand=True)

        # Create controls frame controls for the query.
        self._controlsFrame = tk.Frame(self._container, bg='#549DB5')
        self._controlsFrame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        # Add logo image.
        logo_image = Image.open('logo.png')
        self._logo_render = ImageTk.PhotoImage(logo_image)
        self._logo = tk.Label(self._controlsFrame, image=self._logo_render, width=250, height=62, bg='#549DB5', fg='white')
        self._logo.pack(side=tk.TOP, fill=tk.NONE)

        # Add from date picker control.
        self._from_date_label = tk.Label(self._controlsFrame, text='From:', fg='white', bg='#549DB5')
        self._from_date_label.pack(side=tk.TOP, pady=(10, 0))
        self._from_date_picker = tkcal.DateEntry(self._controlsFrame, foreground='white', background='#549DB5')
        self._from_date_picker.set_date(datetime.datetime.now())
        self._from_date_picker.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Add to date picker control.
        self._to_date_label = tk.Label(self._controlsFrame, text='To:', fg='white', bg='#549DB5')
        self._to_date_label.pack(side=tk.TOP, pady=(10, 0))
        self._to_date_picker = tkcal.DateEntry(self._controlsFrame, foreground='white', bg='#549DB5')
        self._to_date_picker.set_date(datetime.datetime.now())
        self._to_date_picker.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Add property list to pick the one to display/download.
        self._property_list_label = tk.Label(self._controlsFrame, text='Properties:', fg='white', bg='#549DB5')
        self._property_list_label.pack(side=tk.TOP, pady=(10, 0))
        self.property_list = tk.Listbox(self._controlsFrame, selectmode=tk.MULTIPLE)
        self.property_list.pack(side=tk.TOP, fill=tk.BOTH, padx=10, expand=True)

        # Add plot button.
        self._plot_button = tk.Button(self._controlsFrame, text='Plot data', command=self.on_plot_button_clicked)
        self._plot_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 2))
        self._plot_button.config(state=tk.DISABLED)

        # Add download button.
        self._download_button = tk.Button(self._controlsFrame, text='Download data...', command=self.on_download_button_clicked)
        self._download_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(2, 10))
        self._download_button.config(state=tk.DISABLED)

        # Add plot output widget including navigator controls.
        self.figure = plt.Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self._container)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self._container)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X, expand=False)

        tkct.center_on_screen(self)
        self.update()

        # Initially open the connect dialog.
        self.on_connect_button_clicked()

    def on_connect_button_clicked(self):

        # Show connect dialog.
        dialog = ConnectDialog(self)

        # Check if ok was clicked, if not do nothing.
        if dialog.result:
            try:
                # Try to connect to the gateway using the parameters from the dialog.
                access_level = self._client.connect(dialog.host(), dialog.port(), dialog.username(), dialog.password())

                # Show error if no access was granted by the gateway.
                if access_level == openstuder.SIAccessLevel.NONE:
                    tkmb.showerror(message='Could not connect to the gateway, credentials were rejected')
                    self._client.disconnect()
                    return
            except openstuder.SIProtocolError as error:
                tkmb.showerror(message=f'Could not connect to the gateway: {error.reason()}')
                self._client.disconnect()
                return
            except ConnectionRefusedError as error:
                tkmb.showerror(message='Could not connect to the gateway: Connection was refused by peer')
                self._client.disconnect()
                return

            # Enable/disable UI elements for connected state.
            self._gatewayMenu.entryconfig('Disconnect', state=tk.NORMAL)
            self._gatewayMenu.entryconfig('Connect...', state=tk.DISABLED)
            self._plot_button.config(state=tk.NORMAL)
            self._download_button.config(state=tk.NORMAL)

            # Get list of available data log properties.
            try:
                status, property_ids = self._client.read_datalog_properties()
                if status != openstuder.SIStatus.SUCCESS:
                    tkmb.showerror(message=f'Could not get available properties list: {status.name}')
                    return

                # On success, add the properties to the list box.
                for index, property_id in enumerate(property_ids):
                    self.property_list.insert(index, property_id)

            except openstuder.SIProtocolError as error:
                tkmb.showerror(message=f'Could not get available properties list: {error.reason()}')
                return

    def on_disconnect_button_clicked(self):

        # Disconnect OpenStuder client.
        self._client.disconnect()

        # Enable/disable UI elements for unconnected state.
        self._gatewayMenu.entryconfig('Disconnect', state=tk.DISABLED)
        self._gatewayMenu.entryconfig('Connect...', state=tk.NORMAL)
        self._plot_button.config(state=tk.DISABLED)
        self._download_button.config(state=tk.DISABLED)

        # Clear properties list.
        self.property_list.delete(0, tk.END)

        # Clear and redraw plot.
        self.axes.cla()
        self.canvas.draw()

    def on_plot_button_clicked(self):
        # Get list of selected properties.
        selection = self.property_list.curselection()

        # Show download progress dialog.
        progress = ProgressDialog(self, 'Downloading plot data...', len(selection))

        # Clear current plots.
        self.axes.cla()

        # Iterate over the list of selected properties and download and plot one by one.
        for selected in selection:

            # Get current property ID.
            property_id = self.property_list.get(selected)

            # Try to get the property data.
            try:
                status, _, count, csv = self._client.read_datalog_csv(property_id,
                                                                      from_=datetime.datetime.combine(self._from_date_picker.get_date(), datetime.datetime.min.time()),
                                                                      to=datetime.datetime.combine(self._to_date_picker.get_date(), datetime.datetime.max.time()))

                # Check that the status is ok, otherwise fail.
                if status != openstuder.SIStatus.SUCCESS:
                    tkmb.showerror(message=f'Error retrieving data for property {property_id}: {status.name}')
                    continue

                # Convert received CSV data to pandas table.
                data = pd.read_csv(io.StringIO(csv), sep=',', header=None)

                # Convert date string in column 0 to Python Datetime.
                data[0] = pd.to_datetime(data[0])

                # Rename columns from pure indexes to user-friendly names.
                data.rename(columns={0: 'time', 1: property_id}, inplace=True)

                # Plot the data.
                data.plot(ax=self.axes, x=0, y=1)

                # Update progress bar.
                progress.step()

            except openstuder.SIProtocolError as error:
                tkmb.showerror(message=f'Error retrieving data for property {property_id}: {error.reason()}')
                continue

        # Finally update the plot on the UI.
        self.canvas.draw()

        # Close progress dialog.
        progress.finish()

    def on_download_button_clicked(self):

        # Get list of selected properties.
        selection = self.property_list.curselection()

        # Ask the user to which directory the CSV files have to be saved to.
        directory = tkfd.askdirectory()

        # Do nothing if the user pressed the cancel button.
        if directory:

            # Show download progress dialog.
            progress = ProgressDialog(self, 'Downloading data...', len(selection))

            # Iterate over the list of selected properties and download and save one by one.
            for selected in selection:
                property_id = self.property_list.get(selected)

                # Try to get the property data.
                try:
                    status, _, count, csv = self._client.read_datalog_csv(property_id,
                                                                          from_=datetime.datetime.combine(
                                                                              self._from_date_picker.get_date(),
                                                                              datetime.datetime.min.time()),
                                                                          to=datetime.datetime.combine(
                                                                              self._to_date_picker.get_date(),
                                                                              datetime.datetime.max.time()))

                    # Check that the status is ok, otherwise fail.
                    if status != openstuder.SIStatus.SUCCESS:
                        tkmb.showerror(message=f'Error when retrieving data for property {property_id}')
                        continue

                    # Write CSV data into file.
                    with open(f'{directory}/{property_id}.csv', 'w') as file:
                        file.write(csv)

                    # Update progress bar.
                    progress.step()

                except openstuder.SIProtocolError as error:
                    tkmb.showerror(message=f'Error retrieving data for property {property_id}: {error.reason()}')
                    continue

            # Close progress dialog.
            progress.finish()


if __name__ == '__main__':
    mainWindow = MainWindow()
    mainWindow.mainloop()
