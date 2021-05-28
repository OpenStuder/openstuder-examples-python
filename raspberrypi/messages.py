import tkinter as tk

from PIL import Image, ImageTk

from uielements import DashboardPage, Button


class MessagesDashboardPage(DashboardPage):
    def _setup_ui(self):
        dashboard_image = Image.open('img/Messages.png')
        self.__background_render = ImageTk.PhotoImage(dashboard_image)
        self.__background = tk.Label(self, image=self.__background_render)
        self.__background.place(x=0, y=0, relwidth=1, relheight=1)

        self.__back_button = Button(self, 'img/BackButton.png', callback=lambda: self._change_to_frame('overview'))
        self.__back_button.place(x=20, y=12, width=46, height=46)

        self.__message_list = tk.Canvas(self, bg='white', bd=0, borderwidth=0, highlightthickness=0, insertborderwidth=0, selectborderwidth=0)
        self.__message_list.place(x=20, y=110, width=760, height=350)

    def _activate(self, system_info):
        self.client.read_messages(limit=20)

    def _deactivate(self):
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
            self.__message_list.create_line(0, i * 17, 760, i * 17, width=1, fill="black")
            self.__message_list.create_text(5, 8 + i * 17, anchor=tk.W, text=f'{message.access_id}.{message.device_id}', font=self._default_font(size=11))
            self.__message_list.create_text(120, 8 + i * 17, anchor=tk.W, text=f'{message.message} ({message.message_id})', font=self._default_font(size=11, weight='normal'))
            self.__message_list.create_text(640, 8 + i * 17, anchor=tk.W, text=f'{message.timestamp}', font=self._default_font(size=13, weight='normal'))
