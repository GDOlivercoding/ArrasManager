from typing import (
    ClassVar,
    Callable,
    Protocol,
    Self,
    Any,
    Literal,
    Final,
)
from json import dump as _dump
from pathlib import Path
from dataclasses import dataclass, field
import tkinter.messagebox as mbox

# any libraries imported as:
# import library (as alias)
# should be imported from here
# as it saves little performance when we already import init

# here are the paths for certain directories and files

base_dir: Path = Path.home()
dir_arras: Path = base_dir / "AppData" / "Local" / "Arras"
file_logdata: Path = dir_arras / "logdata.txt"
file_settings: Path = dir_arras / "settings.json"
screenshot_dir: Path = base_dir / "Pictures" / "Screenshots"

# i will delete this
# in modify.py, monitores, if the user has deleted their log file
# if they have, this flag is set to True, and the program wont
# log for that instance
was_deleted: bool = False

# for more readable Settings.pic_export comparisons
NONE: Final = 0
SINGLE: Final = 1
BOTH: Final = 2

# a code split by a colon should equal or exceed this number
# very easy way to tell if something is a real code
VALID_CODE_INTEGER: Final = 10

# traceback.format_exc() returns this string when there is no past exceptions raised
NO_EXCEPTION: Final = "NoneType: None"

# SupporsWrite proto
class SupportsWrite(Protocol):
    def write(self, data: Any, /) -> Any: ...

# for the json library, all these types should be acceptable
# to be json serialized
JSONSerializable = None | bool | str | float | int | tuple | list | dict

# the values of the settings.json file
# this is just to visually uhhhh
# know? that this should cary the values of the file yup
ContentsType = object

# region tag: region name
regions: dict[str, str] = {
    "e": "Europe",
    "w": "US West",
    "c": "US Central",
    "o": "Oceania",
}

# more gamemode region type things, varies...
gamemode: list[str] = ["Normal", "Olddreads", "Newdreads", "Grownth", "Arms race"]
RegionType = Literal["Europe", "US West", "US Central", "Oceania"]
Region = list(regions.values())
GamemodeType = Literal["Normal", "Olddreads", "Newdreads", "Grownth", "Arms Race"]

# a list of strings of names of the settings file
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
    "unclaimed",
]

# default values of the settings
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
    {},
]

# we modify the original function to pretty print
def dump(obj: Any, fp: SupportsWrite, indent=4):
    return _dump(obj=obj, fp=fp, indent=indent)

# my own simple partial
# saves some performance because we dont have to
# import the entiredy of functools
# type hinted, and not overflood with unused features

# used by tk apps to make repetitive widgets
class partial[T, **P]:
    def __init__(
        self: Self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        self.func: Callable[P, T] = func
        self.args: tuple[Any, ...] = args
        self.kwargs: dict[str, Any] = kwargs

    def __call__(self: Self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*self.args, *args, **self.kwargs, **kwargs)

# this class represents the settings.json file
# commonly referenced as `data` in files where they
# want to use the settings

@dataclass
class Settings:
    """contains settings.json, persistent data"""

    fullscreen_ss: str = "fullscreen_ss"
    windowed_ss: str = "windowed_ss"
    single_ss: str = "ss"
    confirmation: bool = True
    pic_export: Literal[0, 1, 2] = 0
    ss_dir: Path = screenshot_dir
    automation: bool = False
    force_automation: bool = False
    ask_time: bool = False
    def_time: int = 5 * 60
    open_dirname: bool = False
    unclaimed: dict[str, str] = field(default_factory=dict)

    # guard
    # dunder to be ignored
    __instances__: ClassVar[int] = 0

    def __post_init__(self):
        Settings.__instances__ += 1
        # do not remove this, when creating an object
        # the original value is string
        self.ss_dir = Path(self.ss_dir)

    def get_dict(self) -> dict[str, ContentsType]:
        """Return the Settings object converted to a dictionary and ready to go!
        (Makes the object JSON serializable)
        """

        return {
            k: (v if isinstance(v, JSONSerializable) else str(v))
            for k, v in vars(self).items()
        }

# as per the docstring, i use this as a shortand initializer for the settngs file
# this still stays, as its a nice way to guard all instance of it
# though, obsolete

def create_dict(contents: dict[str, ContentsType], /) -> Settings:
    """We unpack contents as a dictionary into the Settings object, this ensures the positional arguments dont matter"""
    # before i used to unpack the .values() but now i realized i can just unpack the whole dictionary
    # this function remains since its a way to manage all new instances of the Settings class

    return Settings(**contents)  # type: ignore

# receive a score integer in the savable range
# and convert it into something we would put
# in a directory name
# looks aboslutely horrendous but i can guarantee
# you that i will never edit this function

def format_score(raw_i: int, /) -> str:
    """return the raw score integer formatted"""
    raw = str(raw_i)  # we want an integer but we will format it as a string

    match len(raw):

        case 6:  # 784_125 = 784K
            return f"{raw[:3]}K"

        case 7:  # 1_754_125 = 1.75m
            return f"{raw[0]}.{raw[1:][:2]}m"

        case 8:  # 41_754_125 = 41.7m
            return f"{raw[:2]}.{raw[:3][2:]}m"

        case 9:  # 241_754_125 = 241m
            return f"{raw[:3]}m"

        case 10:  # 1_241_754_125 = 1.24b
            return f"{raw[0]}.{raw[1:][:2]}b"

        case _:
            raise ValueError(f"Score Integer isn't in the savable range: {len(raw)}")

# get a code from the user
# always returns a code

def get_code() -> str:
    try:
        import pyperclip

        code = pyperclip.paste()

        if len(code.split(":")) >= VALID_CODE_INTEGER:
            return code
        else:
            raise ValueError

    except (ModuleNotFoundError, ValueError):
        while True:
            if len((code := input("Input code: ")).split(":")) >= VALID_CODE_INTEGER:
                return code
            else:
                print("Invalid code")

# contains defaults for Settings object
write: dict[str, ContentsType] = {
    k: v for k, v in zip(settings_keys, settings_base_values, strict=True)
}

# we give out some info if we run the file directly
if __name__ == "__main__":
    print(
        f"\n{base_dir=}\n{dir_arras=}\n{file_logdata=}\n{file_settings}\n{screenshot_dir=}\n\n"
    )

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

    mbox.showinfo(
        title="Not for use",
        message="This is a system file, check the console if you're looking for debug info\notherwise hit 'ok' to exit",
    )
