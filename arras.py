from init import (
    mbox,
    dump,
    RegionType,
    Settings,
    format_score,
    create_dict,
    get_code,
    NONE,
    SINGLE,
    BOTH,
    NO_EXCEPTION,
    parse_server_tag,
    regions,
    file_settings,
    file_logdata,
    base_dir,
)

from os import startfile as os_startfile
from datetime import UTC, datetime, date
from typing import ClassVar, Literal, Never
from pathlib import Path
import traceback as tb
from json import load

ENCODING = "utf-8"

if __name__ != "__main__":
    import warnings

    warnings.warn(
        f"This file is NOT meant to be imported, but rather ran directly! process name: {__name__=}"
    )

# sample code (6f0cb12f:#eo:e5forge:Arbitrator-Astronomic:0/2/6/10/10/10/10/12/0/0:7148698:20683:71:13:4:5017:62:1710762682:JDo5u44GPYop3lwZ)

# (6f0cb12f:  #eo:                e5forge:  Arbitrator-Astronomic:  0/2/6/10/10/10/10/12/0/0:  7148698:
#  unknown    server URL address  gamemode  tank class              build                      score

# 20683:                71:    13:      4:                   5017:               62:      1710762682:  JDo5u44GPYop3lwZ)
# time alive in seconds kills  assists  boss kills / assits  polygons destroyed  unknown  unknown      unknown

# region Code class


class Code:
    """contains non persistent data"""

    # guard
    instantiated: ClassVar[bool] = False

    def __init__(self, code: str, /) -> None:
        Code.instantiated = True
        self.code = code.removeprefix("`").removesuffix("`")

        self.extract_code(self.code.split(":"))

    def extract_code(self, parts: list[str]) -> None:
        self.parts = parts
        self.server = parts[1]
        self.gamemode_tag = parts[2]
        self.cls = parts[3]
        self.build = parts[4]
        self.runtime = int(parts[6])
        self.kills = int(parts[7])
        self.assists = int(parts[8])
        self.boss_kills = int(parts[9])

        # we seperate this to change the message into something else since format_score gives a ValueError
        try:
            self.raw_score = int(parts[5])
            self.score = format_score(self.raw_score)
        except ValueError as e:
            ExceptionHandler(str(e))

        self.build_parts = [int(i) for i in self.build.split("/")]
        self.build_sum = sum(self.build_parts)

        self.gamemode = self.match_gamemode(self.gamemode_tag)
        self.region = self.match_region(self.server)
        self.dirname = self.construct_dirname()

        self.restore = self.restore_check()

    @staticmethod
    def match_gamemode(
        gamemode: str,
    ) -> Literal["Normal", "Olddreads", "Newdreads", "Grownth", "Arms Race"]:
        """return the gamemode based on its name"""

        gamemode = "Normal"

        for name, mode in {"olds": "Olddreads", "forge": "Newdreads"}.items():
            if name in gamemode:
                gamemode = mode

        for tag, mode in {"g": "Grownth", "a": "Arms Race"}.items():
            if gamemode.startswith(tag):
                gamemode = mode

        return gamemode  # type: ignore

    @staticmethod
    def match_region(server: str) -> RegionType:
        region = None

        region_char = server[1]

        for region_tag, region_name in regions.items():
            if region_char == region_tag:
                region = region_name
                break

        if region is None:
            ExceptionHandler(
                f"The region has not been found, this is an internal error, server: {server}"
            )

        return region  # type: ignore

    def construct_dirname(
        self,
        /,
        *,
        gamemode: str | None = None,
        score: str | None = None,
        tankclass: str | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> Path:
        """
        Returns a `pathlib.Path` pointing to a (yet) non existing directory
        from the current month and day, the code's score and tank (class)

        specify any of the 5 optionally keyword parameters to override the instance's default
        """
        cur_date = datetime.now(UTC)

        if month is None:
            month = cur_date.month
        if day is None:
            day = cur_date.day

        if len(str(month)) == 1:
            month = f"0{month}"  # type: ignore

        formatted = f"{month}.{day}."

        gamemode = gamemode or self.gamemode
        score = score or self.score
        cls = tankclass or self.cls

        path = Path(__file__).parent / gamemode / " ".join([formatted, score, cls])

        return path

    def restore_check(self) -> None | Path:
        # make sure to write a lot of comments here
        # figure out of self.code is a restore of
        # one of codes in data.restore

        for code in data.restore:
            parts = code.split(":")
            _server = parts[1]
            gamemode_tag = parts[2]
            cls = parts[3]
            build = parts[4]
            score = int(parts[5])
            runtime = int(parts[6])
            kills = int(parts[7])
            assists = int(parts[8])
            boss_kills = int(parts[9])

            print("\nnew code: {code}".format(code=code))

            # if any of runtime, score, kills, assists or boss kills
            # is higher on the restored code it cant be a restore

            INT32_LIMIT_BYPASS_CHECK = False

            if (
                INT32_LIMIT_BYPASS_CHECK
                and cls == self.cls
                and sum(int(skill) for skill in build.split("/"))
                >= sum(int(skill) for skill in self.build.split("/"))
            ):
                score = float("inf")

            if (
                runtime < self.runtime
                or score < self.raw_score  # XXX when going over the
                # 32 bit integer limit, this wont be able to tell
                # but because its so rare, i dont care
                or kills < self.kills
                or assists < self.assists
                or boss_kills < self.boss_kills
            ):
                print("One of the stats of the tank is lower than the original")
                continue

            # anything with a self. prefix signalizes
            # the stat of the currently-being-saved code
            # the ones without prefix signalize
            # the yet-to-be-restored code thats being
            # iterated over

            gamemode = self.match_gamemode(gamemode_tag)

            # this is the most i can do for now
            if (
                self.gamemode == gamemode
                or self.gamemode == "Newdreads"
                and gamemode == "Normal"
            ):
                # if the gamemode isn't same, the code is wrong...
                # unless you transform into a dreadnought (v2/3)

                if (
                    gamemode == "Arms Race" and self.gamemode_tag != gamemode_tag
                    # or self.cls != cls
                ):
                    # explaination:
                    # in arms race, since theres no nexus, you cant change server maps
                    # like elsewhere
                    # for example, once youre in maze 4tdm, you cannot change the tdm count
                    # or if its maze
                    # checking for class doesn't work because it might not be final
                    continue

                if gamemode not in ("Olddreads", "Newdreads") and sum(
                    int(skill) for skill in build.split("/")
                ) > sum(int(skill) for skill in self.build.split("/")):
                    # the continuation code cannot have less upgrades (unless its a dreadnought server)

                    # (if the sum of skills in the continuation are lower, this it not the code)
                    continue

                print(f"code {code} succeeded the restore check")
                return Path(data.restore[code])

            print(f"code {code} doesnt match the original's gamemode")

        return None


# region FileIO class


class FileIO:
    def __init__(self) -> None:
        if not Code.instantiated:
            raise ValueError("CodeData not instantiated")
        elif not Settings.__instances__:
            raise ValueError("Settings not instantiated")

        ctx.dirname.mkdir(exist_ok=True)

        with (ctx.dirname / "code.txt").open("w", encoding=ENCODING) as file:
            file.write(ctx.code)

        self.filenames = self.add_ss()

        self.resolve_restore()

        write_unclaimed(data, ctx.code)

    def resolve_restore(self):
        if not ctx.restore:
            return

        ctx.restore.rename(ctx.dirname / ctx.restore.name)

        for d in (d for d in ctx.restore.iterdir() if d.is_dir()):
            d.rename(d.parent / d.name)

        for k, v in {**data.restore}.items():  # dict size change
            if v == ctx.restore:
                del data.restore[k]

    def add_ss(self) -> tuple[Path | None, Path | None]:  # not a type hinting error
        if (
            data.pic_export == NONE
        ):  # do not run this function if the user wishes to not save any death ss
            return (None, None)

        if not data.ss_dir.exists():
            # TODO: figure out what to do if the screenshot directory doesnt exist
            raise FileNotFoundError(
                f"Screenshot directory doesnt exist, directory={data.ss_dir}"
            )

        # here get the latest created files from the screenshot directory
        new = {file.stat().st_birthtime: file for file in data.ss_dir.iterdir()}
        ss1, ss2 = [new[s] for s in sorted(new.keys(), reverse=True)[:2]]

        # if ss1 is smaller, then switch the variables
        # this means ss1 is always going to be bigger
        # this means that ss1 is always windowed, and ss2 is always fullscreen
        if ss1.stat().st_size < ss2.stat().st_size:
            ss1, ss2 = ss2, ss1

        if data.pic_export == BOTH:
            ss1.rename(ctx.dirname / ss1.with_stem(data.windowed_ss).name)
            ss2.rename(ctx.dirname / ss2.with_stem(data.fullscreen_ss).name)

        elif data.pic_export == SINGLE:
            ss1.rename(ctx.dirname / ss1.with_stem(data.single_ss).name)

        else:
            ExceptionHandler(
                f"Picture export integer isn't in the allowed range, integer: {data.pic_export}"
            )

        return (ss1, ss2) if data.pic_export == BOTH else (ss1, None)


#  --------------------------------------------------
#  If an exception occurs, this class will handle it and write it down
#  --------------------------------------------------


class ExceptionHandler:
    def __init__(self, message: str, kill=True) -> None:
        self.message = message
        self.kill = kill

        self.display_exception()
        self.write_exception()

    def display_exception(self, text: str | None = None):
        mbox.showerror(
            title="ERROR", message=text if text is not None else self.message
        )

    def write_exception(self) -> Never:
        if not file_logdata.exists():
            with (base_dir / "Desktop" / f"{date.today()} ArrasErr.log").open(
                "w", encoding=ENCODING
            ) as file:
                file.writelines(self.message.strip() + "\n")

            self.display_exception(
                "Logdata file doesn't exist, the traceback has been written on your desktop instead,"
                "\nto fix this problem, please run the installer and select the repair data files option"
            )
            if self.kill:
                exit()

        with file_logdata.open("r", encoding=ENCODING) as file:
            contents = file.readlines()

        try:
            self.dummy = int(contents[0])

        except ValueError:
            self.dummy = 1

        except IndexError:
            self.dummy = 1
            contents.append("1")

        else:
            self.dummy += 1

            contents[0] = str(self.dummy) + "\n"

        contents.append(self.info_string())

        with file_logdata.open("w", encoding=ENCODING) as newfile:
            newfile.writelines(contents)
        exit()

    def info_string(self) -> str:
        exc = tb.format_exc().strip()

        BIG_STRING = f"""
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
arras.py instance at {str(datetime.now()).split(".")[0]}, instance number {self.dummy}:

{"An unrecognized" if exc != NO_EXCEPTION else "A recognized"} exception in arras.py occured at {str(datetime.now()).split(".")[0]}

message:
    {self.message.replace("\n", "\n    ")}

full stacktrace:
    {exc if exc != NO_EXCEPTION else "This isn't an internal error, please refer to the message above"}
"""
        return BIG_STRING


# ------------------------------------------------------------------------------
# write various information in the logdata file upon the program succeeding
# ------------------------------------------------------------------------------


class WriteDown:
    def __init__(self) -> None:
        self.contents = self.read_logdata()

        self.dummy = self.get_report_int()

        self.contents.append(self.create_data())

        self.write_logdata(self.contents)

    def read_logdata(self) -> list[str]:
        with file_logdata.open("r", encoding=ENCODING) as file:
            return file.readlines()

    def write_logdata(self, to_write: list[str]) -> Never:
        with file_logdata.open("w", encoding=ENCODING) as file:
            file.writelines(to_write)
        exit()

    def get_report_int(self) -> int:
        try:
            dummy = int(self.contents[0].strip())
        except ValueError:
            dummy = 0
        except IndexError:
            self.contents.append("1")
            dummy = 0

        return dummy + 1

    def create_data(self):
        td = date.today()

        BIG_STRING: str = f"""
-----------------------------------------------------------------
-----------------------------------------------------------------
arras.py instance at {td.day}.{td.month}, instance number {self.dummy}:

Path: {ctx.dirname.stem}
Full-path: {ctx.dirname}
picture1: {var.filenames[0]}
picture2: {var.filenames[1]}

Settings:
> confirmation: {data.confirmation}
> pic_export: {data.pic_export}
> screenshot_directory: {data.ss_dir}

Data:
code: {ctx.code}
server: {ctx.server}
gamemode: {ctx.gamemode}
full mode: {parse_server_tag(ctx.gamemode_tag)}
region: {ctx.region}
tank class: {ctx.cls}
tank build: {ctx.build}
total score: {ctx.score}

runtime in hours: {ctx.runtime / 3600:.1f}h
runtime in minutes: {ctx.runtime // 60}min

"""
        return BIG_STRING


def write_unclaimed(contents: Settings, code: str, /) -> None:
    """
    helper to write down the code for the unclaimed codes list for convenience
    called from the FileIO class
    """
    if code in contents.unclaimed.keys():
        mbox.showwarning(
            title="WARNING", message="This code has already been registered!"
        )
    contents.unclaimed[code] = datetime.isoformat(datetime.now())  # type: ignore "unclaimed" is a dictionary

    with file_settings.open("w", encoding=ENCODING) as file:
        dump(obj=contents.get_dict(), fp=file)


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Instant functionality starts here
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

if not file_settings.exists():
    try:
        raise FileNotFoundError(f"Path (File) '{file_settings}' doesn't exist")
    except FileNotFoundError:
        pass
    # this is to make sure that tb.format_exc() works as expected

    ExceptionHandler(
        "Cannot find settings file\nplease run the installer and select the 'no' option to fix this problem\nnote that all settings will be set to default\nand the entire logging file will be reset if you do so"
    )

with file_settings.open("r", encoding=ENCODING) as file:
    data = create_dict(load(file))

if data.confirmation:
    if not mbox.askyesno(
        title="Confirmation", message="Are you sure you want to create a save?"
    ):
        exit()

code = get_code()

ctx = Code(code)

try:
    var = FileIO()

    mbox.showinfo(title="Success", message="Successfully created a save!")

    try:
        if data.open_dirname:
            os_startfile(ctx.dirname)
    except:
        ExceptionHandler(
            "Cannot open destination directory.",
            kill=False,
        )
        WriteDown()

except Exception as e:
    ExceptionHandler(
        f"A critical internal error has occured when attempting file IO operations"
        "\nreport this to the owner immediately\n"
        "make sure to backup the code and the screenshot"
        f"\nmessage: {str(e)}\ntraceback can be found in the logger file"
    )
    # code unreachable

WriteDown()
