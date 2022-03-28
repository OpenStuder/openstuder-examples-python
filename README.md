# Python examples for OpenStuder client

The examples have been tested on **Ubuntu 20.04 LTS**, but they should run fine on Windows and macOS or any other Linux distribution too.

However, the instructions how to prepare your system and run the examples are for Linux (Ubuntu), but it should be not very hard to adapt those for your OS.

## Requirements

### Git

You need **git** to clone the projects to your local machine.

	# sudo apt install git

### Python 3.7+, pip, virtualenv and Tk bindings for Python (tkinter)

	# sudo apt install python3 python3-pip python3-tk
	# sudo pip3 install virtualenv

## cli

Simple interactive shell to demonstrate the use if the **synchronous** client. We recommend to start with this example if you are new to OpenStuder as this is by far the simplest example.

![](common/cli.svg)

All the code is in the file **sicli**, to run the example do:

	# git clone https://github.com/OpenStuder/openstuder-examples-python.git
	# cd openstuder-examples-python/cli
	# virtualenv venv
	# source venv/bin/activate
	# pip install -r requirements.txt
	# chmod +x sicli
	# ./sicli -h
	
## cli-bluetooth

Simple interactive shell to demonstrate the use if the **Bluetooth** client. If a openstuder gateway has bluetooth enabled, you can alternatively connect to the gateway
using Bluetooth. This might be simpler as the PC and the gateway do not need to be in the same Network in order to communicate.

![](common/cli-bluetooth.gif)

All the code is in the file **sicli**, to run the example do:

	# git clone https://github.com/OpenStuder/openstuder-examples-python.git
	# cd openstuder-examples-python/cli-bluetooth
	# virtualenv venv
	# source venv/bin/activate
	# pip install -r requirements.txt
	# chmod +x sicli
	# ./sicli -h


## datalog-gui  

Simple GUI application to plot or download logged property values from an OpenStuder gateway. *tkinter* based. This example demonstrates the use of the **synchronous** client.

![](common/datalog-gui.gif)

Tested to work on Ubuntu Linux and macOS, whereby it looks terrible on macOS Big Sur due to incompatibilities of tkinter with the new look and feel of macOS.

All the code is in the file **main.py**, to run the example do:

	# git clone https://github.com/OpenStuder/openstuder-examples-python.git
	# cd openstuder-examples-python/datalog-gui
	# virtualenv venv
	# source venv/bin/activate
	# pip install -r requirements.txt
	# python main.py

## dashboard

Dashboard GUI application showing the most important values from a Xcom485i or Demo installation. *tkinter* based. This example demonstrates the use of the **asynchronous** client.

![](common/dashboard.gif)

Tested to work on Ubuntu Linux and macOS.

The code is in multiple files to simplify understanding the code:

- **installation.py**: Installation abstractions - Contains information which properties have to be read for the values displayed and contains the business logic to sum values from multiple devices.
- **uielements.py**: Basic user interface widgets like buttons, switches and the dashboard page base class.
- **connection.py**: Dashboard page used to establish connection to OpenStuder gateway.
- **overview.py**: Overview dashboard page.
- **energy.py**: Energy summary dashboard page.
- **battery.py**: Battery details dashboard page.
- **messages.py**: Message list dashboard page.
- **main.py**: Application entry point and main window.

To run the example do:

	# git clone https://github.com/OpenStuder/openstuder-examples-python.git
	# cd openstuder-examples-python/dashboard
	# virtualenv venv
	# source venv/bin/activate
	# pip install -r requirements.txt
	# python main.py
