import sys
from init import (
    dump,
    RegionType,
    format_score,
    create_dict,
    NO_EXCEPTION,
    parse_server_tag,
    regions,
    file_settings,
    file_logdata,
    base_dir,
)

from parse import parse
from enum import StrEnum
from os import startfile as os_startfile
from datetime import UTC, datetime, date
from typing import Never
from pathlib import Path
import traceback as tb
from json import load
import tkinter.messagebox as mbox

ENCODING = "utf-8"

# sample code (6f0cb12f:#eo:e5forge:Arbitrator-Astronomic:0/2/6/10/10/10/10/12/0/0:7148698:20683:71:13:4:5017:62:1710762682:JDo5u44GPYop3lwZ)

# (6f0cb12f:  #eo:                e5forge:  Arbitrator-Astronomic:  0/2/6/10/10/10/10/12/0/0:  7148698:
#  unknown    server URL address  gamemode  tank class              build                      score

# 20683:                71:    13:      4:                    5017:               62:      1710762682:  JDo5u44GPYop3lwZ)
# time alive in seconds kills  assists  boss kills / assists  polygons destroyed  unknown  unknown      unknown

def ymdhms(dt: datetime, sep: str):
    return f"{dt.year}-{dt.month}-{dt.day} {sep} {dt.hour}:{dt.minute}:{dt.second}"

class DirSortedMode(StrEnum):
    Normal = "Normal"
    Olddreads = "Olddreads"
    Newdreads = "Newdreads"
    Growth = "Growth"
    Arms_Race = "Arms Race"

# region Code class

class Code:
    """Represents an Arras.io save code"""

    def __init__(self, code: str) -> None:
        self.inner_code = code.removeprefix("`").removesuffix("`")

        self.from_parts(self.inner_code.split(":"))

    def from_parts(self, parts: list[str]) -> None:
        self.server = parts[1]
        self.gamemode_tag = parts[2]
        self.cls = parts[3]

        try:
            self.raw_score = int(parts[5])
            self.formatted_score = format_score(self.raw_score)
        except ValueError as e:
            exception_handler(str(e))

        self.runtime = int(parts[6])

        self.gamemode = self.match_gamemode(self.gamemode_tag)
        self.region = self.match_region(self.server)
        self.dirname = self.construct_dirname()

    @staticmethod
    def match_gamemode(gamemode: str):
        """return the gamemode based on its name"""
        # this is going to be hard to make stable

        output_mode: DirSortedMode = DirSortedMode.Normal

        # stable function
        parsed = parse(gamemode)

        # stable
        if "old" in parsed:
            output_mode = DirSortedMode.Olddreads

        # stable
        elif "Grownth" in parsed:
            output_mode = DirSortedMode.Growth

        # XXX careful for this check
        elif "Arms_Race" in parsed:
            output_mode = DirSortedMode.Arms_Race

        elif any(node in ('labyrinth', 'forge') for node in parsed):
            output_mode = DirSortedMode.Newdreads

        return output_mode 

    @staticmethod
    def match_region(server: str) -> RegionType:
        region = None

        region_char = server[1]

        for region_tag, region_name in regions.items():
            if region_char == region_tag:
                region = region_name
                break

        return region  # type: ignore

    def construct_dirname(
        self,
    ) -> Path:
        """
        Returns a `pathlib.Path` pointing to a (yet) non existing directory
        from the current month and day, the code's score and tank (class)
        """

        cur_date = datetime.now(UTC)
        
        month = cur_date.month
        day = cur_date.day

        if len(str(month)) == 1:
            month = f"0{month}"  # type: ignore

        month_and_day = f"{month}.{day}."

        gamemode = self.gamemode
        score = self.formatted_score
        tank_class = self.cls

        path = Path(__file__).parent / gamemode / " ".join([month_and_day, score, tank_class])

        return path

# region FileIO class

def fileio(code: Code) -> tuple[Path | None, Path | None]:
    """
    Make the directory, add code file and screenshots 
    """
    code.dirname.mkdir(exist_ok=True)

    with (code.dirname / "code.txt").open("w", encoding=ENCODING) as file:
        file.write(code.inner_code)

    if code in data.unclaimed.keys():
        mbox.showwarning(
            title="WARNING", message="This code has already been registered!"
        )

    data.unclaimed[code.inner_code] = datetime.isoformat(datetime.now())  

    with file_settings.open("w", encoding=ENCODING) as file:
        dump(obj=data.get_dict(), fp=file)

    if not data.pic_export: 
        return (None, None)

    if not data.ss_dir.exists():
        # TODO: figure out what to do if the screenshot directory doesnt exist
        raise FileNotFoundError(
            f"Screenshot directory doesnt exist, directory={data.ss_dir}"
        )

    new = {file.stat().st_birthtime: file for file in data.ss_dir.iterdir()}
    windowed, fullscreen = [new[s] for s in sorted(new.keys(), reverse=True)[:2]]

    # if ss1 is smaller, then switch the variables
    # this means ss1 is always going to be bigger
    # this means that ss1 is always windowed, and ss2 is always fullscreen
    if windowed.stat().st_size < fullscreen.stat().st_size:
        windowed, fullscreen = fullscreen, windowed

    if data.pic_export == 2:
        windowed.rename(code.dirname / windowed.with_stem(data.windowed_ss).name)
        fullscreen.rename(code.dirname / fullscreen.with_stem(data.fullscreen_ss).name)
        return (windowed, fullscreen)

    windowed.rename(code.dirname / windowed.with_stem(data.single_ss).name)
    return (windowed, None)
    


#  --------------------------------------------------
#  If an exception occurs, this class will handle it and write it down
#  --------------------------------------------------


def exception_handler(message: str) -> Never:

    def display_exception(text: str | None = None):
        mbox.showerror(
            title="ERROR", message=text if text is not None else message
        )

    def info_string(dummy: int) -> str:
        sys.last_exc
        exc = tb.format_exc().strip()
        now = datetime.now()
        at_ymdhms = ymdhms(now, "at")

        BIG_STRING = f"""
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
arras.py instance on {at_ymdhms}, instance number {dummy}:

An exception in arras.py occured:

message:
    {message.replace("\n", "\n    ")}

full stacktrace:
    {exc if exc != NO_EXCEPTION else "This isn't an internal error, please refer to the message above"}
"""
        return BIG_STRING

    
    if not file_logdata.exists():
        with (base_dir / "Desktop" / f"{date.today()} ArrasErr.log").open(
            "w", encoding=ENCODING
        ) as file:
            file.writelines(message.strip() + "\n")

        display_exception(
            "Logdata file doesn't exist, the traceback has been written on your desktop instead,"
            "\nto fix this problem, please run the installer and select the repair data files option"
        )

    with file_logdata.open("r", encoding=ENCODING) as file:
        contents = file.readlines()

    try:
        dummy = int(contents[0])

    except ValueError:
        dummy = 1

    except IndexError:
        dummy = 1
        contents.append("1")

    else:
        dummy += 1

        contents[0] = str(dummy) + "\n"

    contents.append(info_string(dummy))

    with file_logdata.open("w", encoding=ENCODING) as newfile:
        newfile.writelines(contents)

    exit()


# ------------------------------------------------------------------------------
# write various information in the logdata file upon the program succeeding
# ------------------------------------------------------------------------------


def writedown(windowed: Path | None, fullscreen: Path | None):
    with file_logdata.open("r", encoding=ENCODING) as file:
        contents =  file.readlines()

    try:
        dummy = int(contents[0].strip())
    except ValueError:
        dummy = 0
    except IndexError:
        contents.append("1")
        dummy = 0

    dummy += 1

    def create_data():
        td = date.today()

        BIG_STRING = f"""
-----------------------------------------------------------------
-----------------------------------------------------------------
arras.py instance at {td.day}.{td.month}, instance number {dummy}:

Name: {code.dirname.stem}
Full path: {code.dirname}
windowed: {windowed}
fullscreen: {fullscreen}

Settings:
> confirmation: {data.confirmation}
> pic_export: {data.pic_export}
> screenshot_directory: {data.ss_dir}

Data:
code: {code.inner_code}
sorted mode: {code.gamemode}
full mode: {parse_server_tag(code.gamemode_tag)}
region: {code.region}
total score: {code.formatted_score}

runtime in hours: {code.runtime / 3600:.2f}h
runtime in minutes: {code.runtime // 60}min

"""
        return BIG_STRING
    
    contents.append(create_data())
    
    with file_logdata.open("w", encoding=ENCODING) as file:
        file.writelines(contents)


def get_code() -> str:
    VALID_CODE_INTEGER = 10
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


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Instant functionality starts here
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

if not file_settings.exists():
    try:
        raise FileNotFoundError(f"Settings file {str(file_settings)!r} doesn't exist")
    except FileNotFoundError:
        pass
    # this is to make sure that tb.format_exc() work as expected

    exception_handler(
        "Cannot find settings file" 
        "\nplease run the installer and select the 'no' option to fix this problem" 
        "\nnote that all settings will be set to default" 
        "\nand the entire logging file will be reset if you do so"
    )

with file_settings.open("r", encoding=ENCODING) as file:
    data = create_dict(load(file))

if data.confirmation:
    if not mbox.askyesno(
        title="Confirmation", message="Are you sure you want to create a save?"
    ):
        exit()

code = Code(get_code())

try:
    windowed, fullscreen = fileio(code)

    mbox.showinfo(title="Success", message="Successfully created a save!")

    try:
        if data.open_dirname:
            os_startfile(code.dirname)
    except Exception:
        writedown(windowed, fullscreen)
        exception_handler(
            "Cannot open destination directory."
        )

except Exception as e:
    exception_handler(
        f"A critical internal error has occured when attempting file IO operations"
        "\nreport this to the owner immediately\n"
        "make sure to backup the code and the screenshot"
        f"\nmessage: {str(e)}\ntraceback can be found in the logger file"
    )

writedown(windowed, fullscreen)