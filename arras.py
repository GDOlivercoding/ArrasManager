from init import (
    mbox,
    datetime, date,
    tb, sd,

    Settings,
    Never,
    Literal,

    format_score,
    move,
    dump, load,
    create_dict,
    perf_counter, sleep,
    os_startfile,
    get_clipboard,

    NONE, SINGLE, BOTH, NO_EXCEPTION, ContentsType, Path,

    regions,
    file_settings,
    file_logdata,
    import_type,
    base_dir,
    Any
)

# this file is not meant to be imported, so if i accidentally do, i find the issue faster
if __name__ != "__main__":
    mbox.showerror(title="ERROR", message=f"This file is NOT meant to be imported, but rather ran directly! process name: {__name__=}")

    raise SystemExit(
        f"This file is NOT meant to be imported, but rather ran directly! process name: {__name__=}"
    )

# sample code
# (6f0cb12f:#eo:e5forge:Arbitrator-Astronomic:0/2/6/10/10/10/10/12/0/0:7148698:20683:71:13:4:5017:62:1710762682:JDo5u44GPYop3lwZ)

# static variables
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

class CodeData:
    """contains non persistent data"""

    def __init__(self, code: str, /) -> None:

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

    def match_gamemode(self) -> str:
        """return the gamemode based on its name"""

        gamemode = "Normal"

        for name, mode in {"old": "Olddreads", "forge": "Newdreads"}.items():
            if name in self.gamemode_tag:
                gamemode = mode

        for tag, mode in {"g": "Grownth", "a": "Arms Race"}.items():
            if self.gamemode_tag.startswith(tag):
                gamemode = mode

        return gamemode

    def match_region(self) -> str:
        region = None

        for k, v in regions.items():
            if self.server[1::][:1:] == k:
                region = v

        if region is None:
            ExceptionHandler(f"The region has not been found, this is an internal error, server: {self.server}")

            exit() # this code is unreachable but its for my type checker

        return region 

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
    def __init__(self, ctx: CodeData, data: Settings) -> None:  
        # this is QOL for the writer class
        # having multiple levels of attributes is annoying
        # but in my evaluation, its the best
        # when we attribute it to self so the write class
        # can access it
        self.ctx = ctx 

        self.code, self.dirname = ctx.code, ctx.dirname
        self.data = data

        self.dirname.mkdir(exist_ok=True)

        with self.dirname.joinpath("code.txt").open("w") as file:
            file.write(self.code)

        self.filenames = self.add_ss()

        WriteUnclaimed(data, self.code)

    def add_ss(self) -> tuple[Path | None, Path | None]: # not a type hinting error

        if self.data.pic_export == NONE:  # do not run this function if the user wishes to not save any death ss
            return (None, None)

        if not self.data.ss_dir.exists():
            # TODO: figure out what to do if the screenshot directory doesnt exist
            raise FileNotFoundError("Screenshot directory doesnt exist")

        # here get the latest created files from the screenshot directory
        new = {file.stat().st_birthtime: file for file in self.data.ss_dir.iterdir()}
        ss1, ss2 = sorted(new.values(), reverse=True)[:2]

        if data.pic_export == BOTH:
            # we rename the files first since pathlib.Path 
            # will return the new renamed file path
            # this is not good since the moving operation is the one more likely
            # to fail
            ss1.rename(self.data.fullscreen_ss)
            ss2.rename(self.data.windowed_ss)
            for f in (ss1, ss2):
                move(f, self.data.ss_dir)       

        elif data.pic_export == SINGLE: 
            # same as above
            ss1.rename(self.data.single_ss)
            move(ss1, self.data.ss_dir)

        else:
            ExceptionHandler(f"Picture export integer isn't in the allowed range, integer: {data.pic_export}")

        return (ss1, ss2) if self.data.pic_export == BOTH else (ss1, None)


#  --------------------------------------------------
#  If an exception occurs, this class will handle it and write it down
#  --------------------------------------------------


class ExceptionHandler:
    def __init__(self, message: str, kill=True) -> Never:
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
            with base_dir.joinpath("Desktop", f"{date.today()} ArrasErr.log").open("w") as file:
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
    def __init__(self, io: FileIO) -> None:
        self.ctx = io.ctx
        self.data = io.data
        self.io = io

        self.contents = self.read_logdata()

        self.dummy = self.get_report_int()

        self.contents.append(self.create_data())

        self.write_logdata(self.contents)

    def read_logdata(self) -> list[str]:
        with file_logdata.open() as file:
            return file.readlines()

    def write_logdata(self, to_write: list[str]) -> Never:
        with open(file_logdata, "w", encoding="utf-8") as file:
            file.writelines(to_write)
        exit()

    def get_report_int(self) -> int:
        try:
            dummy = int(self.contents[0])
            
        except ValueError:
            dummy = 1
        except IndexError:
            self.contents.append("1")
            dummy = 1

        return dummy

    def create_data(self):
        BIG_STRING: str = f"""
-----------------------------------------------------------------
-----------------------------------------------------------------
arras.py instance at {str(datetime.now()).split(".")[0]}, instance number {self.dummy}:

Path: {self.ctx.dirname.stem}
Full-path: {self.io.dirname}
picture1: {self.io.filenames[0]}
picture2: {self.io.filenames[1]}

Settings:
> Confirmation: {self.data.confirmation}
> pic_export: {self.data.pic_export}
> screenshot_directory: {self.data.ss_dir}

Data:
code: {self.ctx.code}
server: {self.ctx.server}
gamemode: {self.ctx.gamemode}
region: {self.ctx.region}
tank class: {self.ctx.cls}
tank build: {self.ctx.build}
total score: {self.ctx.score}

runtime in hours: {self.ctx.runtime / 3600:.1f}h
runtime in minutes: {self.ctx.runtime // 60}min

"""
        return BIG_STRING
    


class WriteUnclaimed:
    """helper to write down the code for the unclaimed codes list for convenience
    called from the FileIO class
    """

    def __init__(self, contents: Settings, code: str, /) -> None:
        self.code = code
        self.contents = contents

        if self.code in self.contents.unclaimed.keys():
            mbox.showwarning(title="WARNING", message="This code has already been registered!\nIt is registered as 'unclaimed' in the Unclaimed tab of modify.py!")

        self.contents.unclaimed[self.code] = datetime.isoformat(datetime.now()) # type: ignore "unclaimed" is a dictionary

        with file_settings.open("w") as file:
            dump(obj=self.contents.get_dict(), fp=file)

class _EnabledAutomation:
    """this is the implementation for the absolute automation but there a question on how do we receive the code itself"""
    # TODO: figure out how to get the code im so braindead right now

    def __init__(self, data: Settings) -> None:
        self.data = data
        if not import_type:
            mbox.showerror("module not downloaded", "'Pyperclip' is a required module to access this functionality, please read the README file")
            exit()
       
    def wait(self):
        if self.data.ask_time:
            sleep_time = sd.askinteger(title="Wait time", prompt="Amount of time to wait in seconds\nbefore attempting to save")
            if sleep_time is None:
                mbox.showwarning("App closed", "Saving cancelled!")
                exit()

        else:
            sleep_time = self.data.def_time

        before = perf_counter()
        mbox.showinfo(f"The app is now going to wait {self.data.def_time}s before saving!")
        after = perf_counter()

        wait_time = (after - before) // 1
        sleep(sleep_time - wait_time)
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Instant functionality starts here
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


if not file_settings.exists():

    try: raise FileNotFoundError(f"FileNotFoundError: Path (File) '{file_settings}' doesn't exist")
    except FileNotFoundError: ...
    # this is to make sure that tb.format_exc() works as expected

    ExceptionHandler(
        "Cannot find settings file\nplease run the installer and select the 'no' option to fix this problem\nnote that all settings will be set to default\nand the entire logging file will be reset if you do so"
    )

with file_settings.open("r") as file:
    data = create_dict(load(file))

#if data.automation:
#    if data.confirmation:
#        if mbox.askyesno(title="Confirmation", message="Are you sure you want to create a save?") != True:
#            exit()
#        EnabledAutomation(data)

if import_type:
    code: str = get_clipboard()
else:
    code = input("code> ")


if len(code.split(":")) < 10:
    ExceptionHandler("Input text is not a code: code doesn't have more than 10 parts when split by a colon")

ctx = CodeData(code)

if data.confirmation:
    if not mbox.askyesno(title="Confirmation", message="Are you sure you want to create a save?"):
        exit()

try:
    var = FileIO(ctx, data)

    mbox.showinfo(title="Success", message="Successfully created a save!")

    try:
        if data.open_dirname:
            os_startfile(var.dirname)
    except:
        ExceptionHandler("An internal error has occured when trying to show the directory location\nreport this to the owner\nnote that everything went well, there's nothing to fear", kill=False)
        WriteDown(var)

except Exception as e:
    ExceptionHandler(f"A critical internal error has occured when attempting file IO operations\nreport this to the owner immediately\nmake sure to backup the code and the screenshot\nmessage: {str(e)}\ntraceback can be found in the logger file")
    exit() # code unreachable

WriteDown(var)