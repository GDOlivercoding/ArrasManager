from tkinter import (

    # tkinter gui elements
    Tk,
    Label,
    Checkbutton,
    StringVar,
    Scale,
    BooleanVar,
    Menu,
    Text,
    Entry,
    Button,
    Scrollbar,
    Listbox,

    # tkinter constants
    Y,
    BOTH as t_BOTH,
    RIGHT,
    HORIZONTAL,
    DISABLED,
    END,

    # modules from the tkinter package
    filedialog as fdialog,
    messagebox as mbox,
    simpledialog as sd, # big big thigy, i wanted this for a while
    ttk as ttk # unnecessary alias
)

from shutil import move
from sys import exit
from datetime import datetime, date, timedelta
from typing import Never, Callable, Protocol, overload, Any, Literal, Final, Iterable
from json import load, dump as _dump
from os import startfile as os_startfile
import os
from pathlib import Path
import traceback as tb
from dataclasses import dataclass, field
from time import perf_counter, sleep

# checking dependencies (not required)
try:
    from pyperclip import (
        paste as get_clipboard,
        copy as copy_clipboard
    )

    import_type: bool = True
except ImportError:
    import_type = False

try:
    import pyautogui as pag
    pag_import: bool = True
except ImportError:
    #mbox.showerror(title="Import Error", message="You do not have pyautogui installed\nThis app requires pyautogui to be installed\ncheck requirements.txt")
    # pag is unused for now, so it is not a requirement
    pag_import = False

try:
    from pygetwindow import getWindowsWithTitle
    gw_import: bool = True
except ImportError:
    gw_import = False

base_dir: Path = Path.home()
dir_arras: Path = base_dir / "AppData" / "Local" / "Arras"
file_logdata: Path = dir_arras / "logdata.txt"
file_settings: Path = dir_arras / "settings.json"
screenshot_dir: Path = base_dir / "Pictures" / "Screenshots"

was_deleted: bool = False

NONE: Final = 0
SINGLE: Final = 1
BOTH: Final = 2
NO_EXCEPTION: Final = "NoneType: None"

class SupportsWrite(Protocol):
  def write(self, data: Any, /) -> Any:
    ...

type JSONSerializable = None | bool | str | float | int | tuple | list | dict
type ContentsType = Any | list[str] | dict[str, str]

regions: dict[str, str] = {
    "e": "Europe",
    "w": "US West",
    "c": "US Central",
    "o": "Oceania",
}

settings_keys: list[str] = [    
    "fullscreen_ss",
    "windowed_ss",
    "single_ss",
    "confirmation",
    "pic_export",
    "ss_dir",
    "automation",
    "force_automation",
    "ask_time",
    "def_time",
    "open_dirname",
    "unclaimed"
]

settings_base_values: list[ContentsType] = [
    "fullscreen ss",
    "windowed ss",
    "ss",
    True,
    0,
    str(screenshot_dir),
    False,
    False,
    False,
    5 * 60,
    False,
    {}
]

# my own simple implementation of the functools partial
# tis all i need

def dump(obj: Any, fp: SupportsWrite):
    return _dump(obj=obj, fp=fp, indent=4)

class partial[T, **P]:
    """
    create a Callable with the keywords arguments predefined
    """

    def __init__(self, func: Callable[P, T], *args: Any, **kwargs: Any) -> None:
        """
        func parameter is the Callable to create
        any keywords are automatically added to the arguments of the Callable
        """
        if not isinstance(func, type):
            raise TypeError(f"partial expects a class reference not a {func!r}")
        
        self.func = func
        self.args = args
        self.kws = kwargs

    def __call__(self, *fargs: P.args, **kwds: P.kwargs) -> T:
        return self.func(*self.args, *fargs, **self.kws, **kwds)

@dataclass
class Settings:
    """contains settings.json, persistent data"""

    fullscreen_ss: str = "fullscreen_ss"
    windowed_ss: str = "windowed_ss"
    single_ss: str = "ss"
    confirmation: bool = True
    pic_export: Literal[0, 1, 2] = 0
    ss_dir: Path = Path(screenshot_dir)
    automation: bool = False
    force_automation: bool = False
    ask_time: bool = False
    def_time: int = 5 * 60
    open_dirname: bool = False
    unclaimed: dict[str, str] = field(default_factory=dict)

    def get_dict(self) -> dict[str, ContentsType]:
        """Return the Settings object converted to a dictionary and ready to go!
        (Makes the object JSON serializable)
        """

        return {k: v if isinstance(v, JSONSerializable) # type: ignore[InvalidParameterType]
                else str(v) 
                for k, v in vars(self).items()} 


def create_dict(contents: dict[str, ContentsType], /) -> Settings:
    """We unpack contents as a dictionary into the Settings object, this ensures the positional arguments dont matter"""
    # before i used to unpack the .values() but now i realized i can just unpack the whole dictionary
    # this function remains since its a way to manage all new instances of the Settings class

    return Settings(**contents) # type: ignore

def format_score(raw_i: int, /) -> str:
    """return the raw score integer formatted"""
    raw = str(raw_i) # we want an integer but we will format it as a string

    match len(raw):

        case 6:  # 784_125 = 784K
            return f"{raw[:3:]}K"

        case 7:  # 1_754_125 = 1.75m
            return f"{raw[:1:]}.{raw[1::][:2:]}m"

        case 8:  # 41_754_125 = 41.7m
            return f"{raw[:2:]}.{raw[:3:][2::]}m"

        case 9:  # 241_754_125 = 241m
            return f"{raw[:3:]}m"

        case 10:  # 1_241_754_125 = 1.24b
            return f"{raw[:1:]}.{raw[1::][:2:]}b"

        case _:
            raise ValueError(
                f"Score Integer isn't in the savable range: {len(raw)}"
            )

# contains defaults for Settings object
write: dict[str, ContentsType] = {}

for key, value in zip(settings_keys, settings_base_values, strict=True):
    write[key] = value

# we give out some info if we run the file directly
if __name__ == "__main__":
    print(f"\n{base_dir=}\n{dir_arras=}\n{file_logdata=}\n{file_settings}\n{screenshot_dir=}\n\n")

    print("regions:\n")
    for k, v in regions.items():
        print(f"{k} = {v}")

    print("\nbase keys:\n")
    for i in settings_keys:
        print(i)

    print("\nbase values:\n")
    for i in settings_base_values:
        print(i)

    print("\nwrite variable:\n")
    for k, v in write.items():
        print(f"{k} = {v}")

    mbox.showinfo(title="Not for use", message="This is a system file, check the console if you're looking for debug info\notherwise hit 'ok' to exit")

# not for export
del screenshot_dir