from init import (
    mbox,
    datetime, date,
    os, tb,

    Settings,
    Never,
    Literal,

    format_score,
    move,
    dump, load,
    create_dict,
    get_clipboard,

    NONE, SINGLE, BOTH, NO_EXCEPTION, ContentsType,

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

    def construct_dirname(self) -> str:
        cur_date = str(datetime.now()).split(" ")[0].split("-")
        del cur_date[0]
        month, day = cur_date

        formatted = f"{month}.{day}."
        self.datetime = formatted

        return f"{formatted} {self.score} {self.cls}"


# -------------------------------------------------------------------------
# file input output operations, creates main dir, moves and os.renames ss, creates code file
# -------------------------------------------------------------------------


class FileIO:
    def __init__(self, ctx: CodeData, data: Settings) -> None:
        self.ctx = ctx
        self.data = data
        self.message: str | Literal[False] = False

        self._dir = self.create_dir()

        if self._dir is not None:
            self.code_file()
            self.filenames = self.add_ss(self._dir)

        WriteUnclaimed(data, self.ctx.code)

    def code_file(self):
        with open(
            os.path.join(self.ctx.dirname, "code.txt"), "w", encoding="utf-8"
        ) as file:
            file.write(self.ctx.code)

    def create_dir(self) -> str | None:
        # create_dir actually just returns str, but my type checker doesn't know calling
        # ExceptionHandler or WriteDown returns Never (both call the exit() function)

        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(self.ctx.gamemode)
                      
            if not os.path.exists(self.ctx.dirname):
                os.mkdir(self.ctx.dirname)
            self.abspath = os.path.abspath(self.ctx.dirname)  

            return os.path.join(os.getcwd(), ctx.dirname)

        except FileNotFoundError as f:
            ExceptionHandler(
                f"System cannot find the gamemode directory, either it doesn't exist or has a different name: dir: {self.ctx.gamemode}"
            )

        except PermissionError as p:
            ExceptionHandler(
                f"System doesn't have enough permissions to access needed files, please move the software to a more common place, dir: {self.ctx.gamemode}"
            )

        except Exception as e:
            ExceptionHandler(
                f"An Unrecognized Error Occured, please report this to the software owner, dir: {self.ctx.gamemode},\ntraceback: {str(e)}"
            )

    def add_ss(self, _dirname: str) -> tuple[str | None, str | None]: # not a type hinting error

        if self.data.pic_export == NONE:  # do not run this function if the user wishes to not save any death ss
            return (None, None)

        try:
            os.chdir(self.data.ss_dir)
        except FileNotFoundError as e:
            ExceptionHandler(
                f"Screenshot directory doesn't exist, please go to modify.py and set it with the instructions"
            )
        except Exception as e:
            ExceptionHandler(
                f"An Error Occured, please report this to the software owner, export the logdata file and send it to the owner, dir: {self.data.ss_dir}, traceback: {str(e)}"
            )

        sorted_files = [f for f in os.listdir() if os.path.isfile(f)]
        sorted_files.sort(
            key=os.path.getctime, reverse=True
        )  # my type checker gets annoyed if we dont split this into 2 lines

        abs_files: tuple[str, str] = (
            os.path.abspath(sorted_files[0]),
            os.path.abspath(sorted_files[1]),
        )
        ss1, ss2 = (sorted_files[0], sorted_files[1])

        os.chdir(_dirname)
        #print(f"{abs_files=}\nss: {ss1, ss2}\n{self.data.pic_export}\n{os.getcwd()=}")


        if data.pic_export == BOTH:

            try:
                for file in abs_files:
                    move(file, os.getcwd())
            
                if os.path.getsize(ss1) < os.path.getsize(ss2):
                    os.rename(ss1, f"{data.fullscreen_ss}.png")
                    os.rename(ss2, f"{data.windowed_ss}.png")
                else:
                    os.rename(ss2, f"{data.fullscreen_ss}.png")
                    os.rename(ss1, f"{data.windowed_ss}.png")
            except:     
                self.message = tb.format_exc()

        elif data.pic_export == SINGLE: 

            try:
                move(abs_files[0], os.getcwd())
                os.rename(ss1, f"{data.single_ss}.png")
            except:
                self.message = tb.format_exc()

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

        if not os.path.exists(file_logdata):
            with open(
                os.path.join(base_dir, "Desktop", f"{date.today()} ArrasErr.log"),
                "w",
                encoding="utf-8",
            ) as file:
                file.writelines(self.message.strip() + "\n")

            self.display_exception(
                "Logdata file doesn't exist, the traceback has been written on your desktop instead,\nto fix this problem, please run the installer and select the 'no' option"
            )
            if self.kill:
                exit()

        with open(file_logdata, "r", encoding="utf-8") as file:
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

        with open(file_logdata, "w", encoding="utf-8") as newfile:
            newfile.writelines(contents)
        exit()

    def info_string(self) -> str:
        exc = tb.format_exc().strip()
        

        BIG_STRING = f"""
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
arras.py instance at {str(datetime.now()).split(".")[0]}, instance number {self.dummy}:

{"An unrecognized" if exc != NO_EXCEPTION else "A recognized"} Exception in arras.py occured at {str(datetime.now()).split(".")[0]}

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
    def __init__(self, ctx: CodeData, data: Settings, io: FileIO, /, *, text: str | Literal[False] = False) -> None:
        self.ctx = ctx
        self.data = data
        self.io = io

        self.text: str | Literal[False] = text
        # i dont like this, i will replace this
        # this is no good

        self.contents = self.read_logdata()

        self.dummy = self.get_report_int()

        self.contents.append(self.create_data())

        self.write_logdata(self.contents)

    def read_logdata(self) -> list[str]:
        with open(file_logdata, "r", encoding="utf-8") as file:
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
{"An ignored file error occured:\n   " + self.text if self.text else "\r"}
arras.py instance at {str(datetime.now()).split(".")[0]}, instance number {self.dummy}:

Path: {self.ctx.dirname}
Sub-path: {self.ctx.gamemode}
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

        with open(file_settings, "w", encoding="utf-8") as file:
            dump(fp=file, obj=self.contents.get_dict())

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Instant functionality starts here
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


if not os.path.exists(file_settings):

    try: raise FileNotFoundError(f"FileNotFoundError: Path (File) '{file_settings}' doesn't exist")
    except FileNotFoundError: ...
    # this is to make sure that tb.format_exc() works as expected

    ExceptionHandler(
        "Cannot find settings file\nplease run the installer and select the 'no' option to fix this problem\nnote that all settings will be set to default\nand the entire logging file will be reset if you do so"
    )

with open(file_settings, "r", encoding="utf-8") as file:
    contents: dict[str, ContentsType] = load(file)


if import_type:
    code: str = get_clipboard()
else:
    code = input("code> ")


if len(code.split(":")) < 10:
    ExceptionHandler("Input text is not a code: code doesn't have more than 10 parts when split by a colon")

data: Settings = create_dict(contents)
ctx = CodeData(code)


if data.confirmation:
    if mbox.askyesno(title="Confirmation", message="Are you sure you want to create a save?") != True:
        exit()

try:
    var = FileIO(ctx, data)

    mbox.showinfo(title="Success", message="Successfully created a save!")

    try:
        if data.open_dirname:
            os.startfile(os.path.abspath(var.abspath))
    except:
        ExceptionHandler("An internal error has occured when trying to show the directory location\nreport this to the owner\nall tasks were ran successfully", kill=False)
        WriteDown(ctx, data, var, text=var.message)

except Exception as e:
    ExceptionHandler(f"A critical internal error has occured when attempting file IO operations\nreport this to the owner immediately\nmake sure to backup the code and the screenshot\nmessage: {str(e)}\ntraceback can be found in the logger file")
    exit() # code unreachable

WriteDown(ctx, data, var, text=var.message)