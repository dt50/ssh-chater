from typing import Any, Iterable
from textual.widgets import ListView, ListItem, Label
from textual.app import ComposeResult


class Listitem(ListItem):
    def __init__(self, entry: str) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        yield Label(
            str(self.entry)
        )


class Listview(ListView):
    def __init__(self, rooms: Iterable[str] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.rooms = rooms

    def on_mount(self) -> None:
        self._refresh()

    def set_rooms(self, rooms: Iterable[str]) -> None:
        self.rooms = rooms
        self._refresh()

    def _refresh(self) -> None:
        # Clear out anything that's in here right now.
        self.clear()
        # Now populate with the content of the current working directory. We
        # want to be able to go up, so let's make sure there's an entry for
        # that...
        if self.rooms:
            for room in self.rooms:
                self.append(Listitem(room))
