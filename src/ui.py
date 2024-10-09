import json
import os
import socket
from time import monotonic
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Footer, RichLog
from textual import work
from ui.widgets import Listview
from textual.worker import Worker, get_current_worker

from database.queries.users import get_user


class UtilityContainersExample(App):
    BINDINGS = [
        ("q", "custom_quit", "Quit")
    ]

    CSS_PATH = "vertical_layout.tcss"

    start_time = reactive(monotonic)
    time = reactive(0.0)

    def __init__(self, **kwargs):
        self.user = get_user(nick_name=os.getenv('USER'))
        super().__init__(**kwargs)

        SERVER_ADDRESS = '127.0.0.1'
        SERVER_PORT = 12000
        self.socket_instance = socket.socket()
        self.socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Quit", "Quit app", self.action_custom_quit)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                with Vertical(classes="rooms_column"):
                    with Container(classes="rooms_list"):
                        yield Listview()
                with Vertical(classes="chat_column"):
                    yield RichLog(classes="chat")
                    with Container(classes="input_container"):
                        yield Input(classes="input")
        yield Footer()

    async def on_mount(self):
        self.handle_messages(self.socket_instance)
        self.set_interval(10, self.update_rooms)

    def update_rooms(self) -> None:
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""

        data = {
            "type": "message",
            "user": self.user["user"].nick_name,
            "msg": "/show_rooms",
        }

        self.socket_instance.send(json.dumps(data).encode())

    @work(exclusive=True, thread=True)
    async def handle_messages(self, connection: socket.socket):
        worker = get_current_worker()
        text_log = self.query_one(RichLog)
        list_view = self.query_one(Listview)

        while True:
            try:
                msg = connection.recv(1024)
                if msg:
                    try:
                        data = json.loads(msg.decode())

                        if "rooms" in data.keys():

                            if not worker.is_cancelled:
                                self.call_from_thread(list_view.set_rooms, data["rooms"])

                    except json.JSONDecodeError:
                        if not worker.is_cancelled:
                            self.call_from_thread(text_log.write, msg.decode())

                else:
                    connection.close()
                    break

            except Exception as e:
                print(f'Error handling message from server: {e}')
                connection.close()
                break

    def action_custom_quit(self) -> None:
        self.exit()
        self.socket_instance.close()


if __name__ == "__main__":
    app = UtilityContainersExample()
    app.run()
