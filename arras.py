from init import (
    GamemodeType,
    RegionType,
    mbox,
    datetime,
    date,
    tb,
    Settings,
    Never,
    ClassVar,
    format_score,
    move,
    dump,
    load,
    create_dict,
    os_startfile,
    get_clipboard,
    NONE,
    SINGLE,
    BOTH,
    NO_EXCEPTION,
    Path,
    regions,
    file_settings,
    file_logdata,
    import_type,
    base_dir,
)

# this file is not meant to be imported, so if i accidentally do, i find the issue faster
if __name__ != "__main__":
    mbox.showerror(
        title="ERROR",
        message=f"This file is NOT meant to be imported, but rather ran directly! process name: {__name__=}",
    )

    raise SystemExit

# sample code
# (6f0cb12f:#eo:e5forge:Arbitrator-Astronomic:0/2/6/10/10/10/10/12/0/0:7148698:20683:71:13:4:5017:62:1710762682:JDo5u44GPYop3lwZ)

class CodeData:
    """contains non persistent data"""

    # guard
    instantiated: ClassVar[bool] = False

    def __init__(self, code: str, /) -> None:
        CodeData.instantiated = True
        self.code = code

        self.extract_code(self.code.split(":"))

    def extract_code(self, parts: list[str]) -> None:
        try:
            self.server = parts[1]
            self.gamemode_tag = parts[2]
            self.cls = parts[3]
            self.build = parts[4]
            self.runtime = int(parts[6])

        except Exception:
            ExceptionHandler("Invalid code")

        # we seperate this to change the message into something else since format_score gives a ValueError
        try:
            self.score = format_score(int(parts[5]))
        except ValueError as e:
            ExceptionHandler(str(e))

        self.gamemode = self.match_gamemode()
        self.region = self.match_region()
        self.dirname = self.construct_dirname()

    def match_gamemode(self) -> GamemodeType:
        """return the gamemode based on its name"""

        gamemode = "Normal"

        for name, mode in {"old": "Olddreads", "forge": "Newdreads"}.items():
            if name in self.gamemode_tag:
                gamemode = mode

        for tag, mode in {"g": "Grownth", "a": "Arms Race"}.items():
            if self.gamemode_tag.startswith(tag):
                gamemode = mode

        return gamemode  # type: ignore

    def match_region(self) -> RegionType:
        region = None

        for k, v in regions.items():
            if self.server[1] == k:
                region = v
                break

        if region is None:
            ExceptionHandler(
                f"The region has not been found, this is an internal error, server: {self.server}"
            )

            exit()  # this code is unreachable but its for my type checker

        return region  # type: ignore

    def construct_dirname(self) -> Path:
        cur_date = str(datetime.now()).split(" ")[0].split("-")
        del cur_date[0]
        month, day = cur_date

        formatted = f"{month}.{day}."
        self.datetime = formatted

        return Path.cwd() / self.gamemode / Path(f"{formatted} {self.score} {self.cls}")


# -------------------------------------------------------------------------
# file input output operations, creates main dir, moves and os.renames ss, creates code file
# -------------------------------------------------------------------------


class FileIO:
    def __init__(self) -> None:
        if not CodeData.instantiated:
            raise ValueError("CodeData not instantiated")
        elif not Settings.__instances__:
            raise ValueError("Settings not instantiated")

        ctx.dirname.mkdir(exist_ok=True)

        with (ctx.dirname / "code.txt").open("w") as file:
            file.write(ctx.code)

        self.filenames = self.add_ss()

        WriteUnclaimed(data, ctx.code)

    def add_ss(self) -> tuple[Path | None, Path | None]:  # not a type hinting error

        if data.pic_export == NONE:  # do not run this function if the user wishes to not save any death ss
            return (None, None)

        if not data.ss_dir.exists():
            # TODO: figure out what to do if the screenshot directory doesnt exist
            raise FileNotFoundError(f"Screenshot directory doesnt exist, directory={data.ss_dir}")

        # here get the latest created files from the screenshot directory
        new = {file.st.st_birthtime: file for file in data.ss_dir.iterdir()}
        ss1, ss2 = [new[s] for s in sorted(new.keys(), reverse=True)[:2]]

        # if ss1 is smaller, then switch the variables
        # this means ss1 is always going to be bigger
        # this means that ss1 is always windowed, and ss2 is always fullscreen
        if ss1.st.st_size < ss2.st.st_size:
            ss1, ss2 = ss2, ss1

        if data.pic_export == BOTH:
            # we rename the files first since pathlib.Path
            # will return the new renamed file path
            # this is not good since the moving operation is the one more likely
            # to fail
            # resulting in more damage
            # if the moving operation fails

            ss1 = ss1.rename(data.windowed_ss + ss1.suffix)
            ss2 = ss2.rename(data.fullscreen_ss + ss2.suffix)
            for f in (ss1, ss2):
                move(f, ctx.dirname)

        elif data.pic_export == SINGLE:
            # same as above
            ss1 = ss1.rename(data.single_ss + ss1.suffix)
            move(ss1, ctx.dirname)

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

    def write_exception(self) -> None:

        if not file_logdata.exists():
            with (base_dir / "Desktop" / f"{date.today()} ArrasErr.log").open(
                "w"
            ) as file:
                file.writelines(self.message.strip() + "\n")

            self.display_exception(
                "Logdata file doesn't exist, the traceback has been written on your desktop instead,"
                "\nto fix this problem, please run the installer and select the repair data files option"
            )
            if self.kill:
                exit()

        with file_logdata.open("r") as file:
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

        with file_logdata.open("w") as newfile:
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
        with file_logdata.open("r") as file:
            return file.readlines()

    def write_logdata(self, to_write: list[str]) -> Never:
        with open(file_logdata, "w", encoding="utf-8") as file:
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
        BIG_STRING: str = f"""
-----------------------------------------------------------------
-----------------------------------------------------------------
arras.py instance at {str(datetime.now()).split(".")[0]}, instance number {self.dummy}:

Path: {ctx.dirname.stem}
Full-path: {ctx.dirname}
picture1: {var.filenames[0]}
picture2: {var.filenames[1]}

Settings:
> Confirmation: {data.confirmation}
> pic_export: {data.pic_export}
> screenshot_directory: {data.ss_dir}

Data:
code: {ctx.code}
server: {ctx.server}
gamemode: {ctx.gamemode}
region: {ctx.region}
tank class: {ctx.cls}
tank build: {ctx.build}
total score: {ctx.score}

runtime in hours: {ctx.runtime / 3600:.1f}h
runtime in minutes: {ctx.runtime // 60}min

"""
        return BIG_STRING

class WriteUnclaimed:
    """helper to write down the code for the unclaimed codes list for convenience
    called from the FileIO class
    """
    def __init__(self, contents: Settings, code: str, /) -> None:

        if code in contents.unclaimed.keys():
            mbox.showwarning(
                title="WARNING",
                message="This code has already been registered!"
            )
        contents.unclaimed[code] = datetime.isoformat(datetime.now())  # type: ignore "unclaimed" is a dictionary

        with file_settings.open("w") as file:
            dump(obj=contents.get_dict(), fp=file)

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Instant functionality starts here
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

if not file_settings.exists():

    try:
        raise FileNotFoundError(
            f"Path (File) '{file_settings}' doesn't exist"
        )
    except FileNotFoundError:
        ...
    # this is to make sure that tb.format_exc() works as expected

    ExceptionHandler(
        "Cannot find settings file\nplease run the installer and select the 'no' option to fix this problem\nnote that all settings will be set to default\nand the entire logging file will be reset if you do so"
    )

with file_settings.open("r") as file:
    data = create_dict(load(file))

if data.confirmation:
    if not mbox.askyesno(
        title="Confirmation", message="Are you sure you want to create a save?"
    ):
        exit()

if import_type:
    code = get_clipboard()
else:
    code = input("code> ")


if len(code.split(":")) < 10:
    ExceptionHandler(
        "Input text is not a code: code doesn't have more than 10 parts when split by a colon"
    )

ctx = CodeData(code)

try:
    var = FileIO()

    mbox.showinfo(title="Success", message="Successfully created a save!")

    try:
        if data.open_dirname:
            os_startfile(ctx.dirname)
    except:
        ExceptionHandler(
            "An internal error has occured when trying to show the directory location\nreport this to the owner\nnote that everything went well, there's nothing to fear",
            kill=False,
        )
        WriteDown()

except Exception as e:
    ExceptionHandler(
        f"A critical internal error has occured when attempting file IO operations\nreport this to the owner immediately\nmake sure to backup the code and the screenshot\nmessage: {str(e)}\ntraceback can be found in the logger file"
    )
    exit()  # code unreachable

WriteDown()
