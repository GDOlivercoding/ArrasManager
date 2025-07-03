from typing import (
    Protocol,
    Any,
    Literal,
    Final,
)
from json import dump as _dump
from pathlib import Path
from dataclasses import dataclass, field

# here are the paths for certain directories and files

base_dir: Path = Path.home()
dir_arras: Path = base_dir / "AppData" / "Local" / "Arras"
file_logdata: Path = dir_arras / "logdata.txt"
file_settings: Path = dir_arras / "settings.json"
screenshot_dir: Path = base_dir / "Pictures" / "Screenshots"

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

# region tag: region name
regions: dict[str, "RegionType"] = {
    "e": "Europe",
    "w": "US West",
    "c": "US Central",
    "a": "Asia",  # How did i just completely miss Asia...
    "o": "Oceania",
}

# more gamemode region type things, varies...
Region = list(regions.values())
gamemode: list[str] = ["Normal", "Olddreads", "Newdreads", "Growth", "Arms race"]
type RegionType = Literal["Europe", "US West", "US Central", "Oceania", "Asia"]
type GamemodeType = Literal["Normal", "Olddreads", "Newdreads", "Growth", "Arms Race"]

# a list of strings of names of the settings file
settings_keys: list[str] = [
    "fullscreen_ss",
    "windowed_ss",
    "single_ss",
    "confirmation",
    "pic_export",
    "ss_dir",
    "open_dirname",
    "unclaimed",
]

# default values of the settings
settings_base_values: list[Any] = [
    "fullscreen ss",
    "windowed ss",
    "ss",
    True,
    0,
    str(screenshot_dir),
    False,
    {},
]


# we modify the original function to pretty print
def dump(obj: Any, fp: SupportsWrite, indent=4):
    return _dump(obj=obj, fp=fp, indent=indent)


# region Settings class


@dataclass
class Settings:
    """contains settings.json, persistent data"""

    fullscreen_ss: str = "fullscreen_ss"
    windowed_ss: str = "windowed_ss"
    single_ss: str = "ss"
    confirmation: bool = True
    pic_export: Literal[0, 1, 2] = 0
    ss_dir: Path = screenshot_dir
    open_dirname: bool = False
    unclaimed: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        # do not remove this, when creating an object
        # the original value is string
        self.ss_dir = Path(self.ss_dir)

    def get_dict(self) -> dict[str, Any]:
        """Return the Settings object converted to a dictionary and ready to go!
        (Makes the object JSON serializable)
        """
        return {
            k: (v if isinstance(v, JSONSerializable) else str(v))
            for k, v in self.__dict__.items()
        }

    def is_data_same(self, other: "Settings") -> bool:
        for k, v in vars(self).items():
            if v != getattr(other, k):
                return False

        return True


def create_dict(contents: dict[str, Any], /) -> Settings:
    """We unpack contents as a dictionary into the Settings object, this ensures the positional arguments dont matter"""
    # before i used to unpack the .values() but now i realized i can just unpack the whole dictionary
    # this function remains since its a way to manage all new instances of the Settings class

    return Settings(**contents)


# receive a score integer in the savable range
# and convert it into something we would put
# in a directory name
# looks aboslutely horrendous but i can guarantee
# you that i will never edit this function


def format_score(raw_i: int | str, /) -> str:
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


# contains defaults for Settings object
write: dict[str, Any] = {
    k: v for k, v in zip(settings_keys, settings_base_values, strict=True)
}


def parse_server_tag(server_tag: str) -> str:
    """
    parse a server tag (ex.: w33olds5forge or m4a) into humanly readable text
    (ex.: old dreadnoughts forge or maze 4tdm arms race)
    """
    s = ""

    # olds tag: w33olds5forge
    if "olds" in server_tag:
        s += "old dreadnoughts "

        # w33olds9labyrinth
        if "labyrinth" in server_tag:
            return s + "labyrinth"

        # w33olds5forge
        if "forge" in server_tag:
            return s + "forge"

        # w33oldscdreadnoughtso3
        if "dreadnoughts" in server_tag:
            s += "main map "
            s += parse_server_tag(server_tag.partition("dreadnoughts")[2])
            return s

    # XXX check if you can save in labyrinth # yes you can
    if "forge" in server_tag:
        return "new dreadnoughts forge"

    # XXX you can do this now
    if "labyrinth" in server_tag:
        return "new dreadnoughts labyrinth"

    if "nexus" in server_tag:
        return "nexus"

    # g indicates grownth in the tag
    if "g" in server_tag:
        s += "grownth "

    # o indicates open
    if "o" in server_tag:
        s += "open "
        is_open = True
    else:
        is_open = False

    # a2 | a4m
    if "a" in server_tag:
        s += "arms race "

    is_tdm = False

    # if theres an integer in the tag, it makes it a tdm gamemode
    for char in server_tag:
        try:
            i = int(char)
        except ValueError:
            continue

        s += f"{i}tdm "
        is_tdm = True
        break

    if is_open and not is_tdm:
        raise ValueError(f"Server tag flagged as open but isn't tdm, {server_tag=}")

    if "m" in server_tag:
        s += "maze"

    if not s:
        raise ValueError(f"Unparsable tag, tag={server_tag}")

    return s.strip()


def main():
    import tkinter.messagebox as mbox

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


# we give out some info if we run the file directly
if __name__ == "__main__":
    main()
