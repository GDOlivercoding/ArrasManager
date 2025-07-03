import os
from parser import match_gamemode, parse_mode
from init import (
    Settings,
    dump,
    file_logdata,
    file_settings,
    screenshot_dir,
    base_dir,
    gamemode,
)

from tkinter import (
    Entry,
    Frame,
    Tk,
    Label,
    Checkbutton,
    StringVar,
    Scale,
    BooleanVar,
    Menu,
    Text,
    Button,
    Scrollbar,
    Listbox,
    Y,
    BOTH,
    RIGHT,
    HORIZONTAL,
    DISABLED,
    END,
    Toplevel,
    filedialog as fdialog,
    messagebox as mbox,
    simpledialog,
    ttk,
)

from datetime import datetime
import json
import webbrowser
from pathlib import Path
from os import startfile
from time import perf_counter
from functools import partial
from pyautogui import size

width, height = size()
x, y = width // 2, height // 2

geometry = f"{x}x{y}"
was_deleted = False

ENCODING = "utf-8"


class Value:
    windowed: StringVar
    fullscreen: StringVar
    single: StringVar

    open_clock: datetime = datetime.now()
    close_clock: datetime


# main window
window = Tk()
window.title("Modify how arras.py functions")
window.geometry(geometry)
window.resizable(False, False)

# read settings
with file_settings.open("r") as file:
    data = Settings(**json.load(fp=file))

START_DATA = Settings(**data.get_dict())

MainHeader = Label(
    text="All changes are automatically recorded when closing the program",
    font=("great vibes", 15),
)
MainHeader.pack(anchor="center")

mytab = ttk.Notebook(window)
tab1 = ttk.Frame(mytab)
tab3 = ttk.Frame(mytab)
tab5 = ttk.Frame(mytab)

mytab.add(tab1, text="Settings")
mytab.add(tab3, text="View Local Files")
mytab.add(tab5, text="Unclaimed Saves")

mytab.pack(anchor="nw")

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# functions, TODO: fix naming convention
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

# convenience functions


def listbox_edit(listbox: Listbox, index: int, new: str):
    listbox.delete(index)
    listbox.insert(index, new)


def listbox_replace(listbox: Listbox, new_elements: list[str]):
    listbox.delete(0, END)
    listbox.insert(END, *new_elements)


def delete_logger() -> None:
    global was_deleted

    if not mbox.askyesno(
        title="Confirmation",
        message="Are you sure you want to delete the ENTIRE logging file?"
        "The file will still exist and log data, all of its contents WILL be deleted!",
    ):
        return
    with file_logdata.open("w") as file:
        file.write("0")

    was_deleted = True

    mbox.showinfo(title="Success", message="Successfully reset the logging file!")


def ss_dir_button(data: Settings, cur_path: StringVar):
    a = fdialog.askdirectory()
    if not a:
        mbox.showerror(title="Error", message="No directory selected")
        return
    cur_path.set(f"Current Path: {a}")
    data.ss_dir = Path(a)
    mbox.showinfo(
        title="Success",
        message=f"Successfully changed the screenshots folder to {data.ss_dir}!",
    )


def settings_reset(
    cb_confirmation: Checkbutton, pic_scale: Scale, data: Settings, cur_path: StringVar
) -> None:
    if not (
        mbox.askyesno(
            title="Confirmation",
            message="Are you sure you want to reset your settings? All options will be set to default",
        )
    ):
        return

    with file_settings.open("w") as file:
        dump(
            fp=file,
            obj={
                "confirmation": True,
                "pic_export": 0,
                "screenshot_dir": str(Path.home() / "Pictures" / "Screenshots"),
            },
        )

    cb_confirmation.select()  # -> True
    pic_scale.set(0)  # -> 0  # -> False
    data.ss_dir = screenshot_dir
    cur_path.set(f"Current Path: {data.ss_dir}")
    mbox.showinfo(title="Success", message="Successfully set all options to default!")
    return


def export_logdata() -> None:
    if not mbox.askyesno(
        title="Confirmation",
        message="Are you sure? This will create a copy of the log file!",
    ):
        return

    with file_logdata.open("r", encoding=ENCODING) as file:
        contents = file.readlines()

    filepath = fdialog.askdirectory(initialdir=base_dir / "Desktop")
    if not filepath:
        mbox.showerror(title="No input", message="No directory selected")
        return

    filepath = Path(filepath)

    with (filepath / "Logdata copy.txt").open("w") as file:
        file.writelines(contents)

    mbox.showinfo(
        title="Success",
        message="Successfully created a copy of the logger file in the desired directory!",
    )


def settings_save_button(data: Settings) -> None:
    with file_settings.open("w") as file:
        dump(fp=file, obj=data.get_dict())

    mbox.showinfo(title="Success", message="Settings saved")


def manage_saves_widget():
    TOP = Toplevel(window)
    TOP.geometry(geometry)
    TOP.title("Manage saves - modify.py")

    def indice_checks(listbox: Listbox) -> tuple[str, int] | None:
        indice = listbox.curselection()

        if not indice:
            mbox.showinfo("Nothing selected", "No save selected")
            return

        indice = indice[0]

        name = listbox.get(indice)

        if name not in table:
            mbox.showerror("Nothing selected", "Didn't select a valid save")
            return

        return (name, indice)

    def view_code():
        get = indice_checks(MAIN)
        if not get:
            return

        name, indice = get

        tk = Tk()
        tk.title(title := f"Viewing {name}")
        tk.geometry(geometry)

        path = table[name]

        header = Label(tk, text=title, font="TkDefaultFont 30")
        header.pack(anchor="n")

        text = Text(tk, wrap="none")
        text.pack(anchor="s", fill=BOTH, expand=True)

        to_insert = []

        files = {file.name: file for file in path.iterdir()}

        if "code.txt" in files.keys():
            code_file = files["code.txt"]
        else:
            mbox.showerror(
                "Code file not found",
                f"Cant find code of {str(path)}"
                ", create a txt file with the code"
                "and try again",
            )
            tk.destroy()
            return

        ss1, ss2 = None, None

        for suffix in ["png", "jpg", "jpeg"]:
            images = list(path.glob(f"*.{suffix}"))

            if (amount := len(images)) == 2:
                ss1, ss2 = images
                break

            elif amount == 1:
                ss1, ss2 = images[0], None
                break

        try:
            code = code_file.read_text().strip()
        except Exception:
            mbox.showerror(
                "Could not get code",
                f"Cant get code of {str(code_file)}"
                ", create a txt file with the code"
                "and try again",
            )
            tk.destroy()
            return

        mode = code.split(":")[2]  # Unreadable unsanitary

        to_insert.append(f"code: {code}")
        to_insert.append(f"path: {str(path)}")
        to_insert.append(f"gamemode: {match_gamemode(mode)}")
        to_insert.append(f"mode: {' '.join(parse_mode(mode))}")

        text.insert(END, "\n".join(to_insert))
        text.config(state="disabled")

        missing = partial(
            mbox.showinfo, title="Missing", message="This screenshot is missing"
        )

        ss_frame = Frame(tk)
        ss_frame.pack(side="bottom")

        ss1_button = Button(
            ss_frame,
            text="Screenshot 1",
            command=(lambda: os.startfile(ss1)) if ss1 is not None else missing,
        )

        ss2_button = Button(
            ss_frame,
            text="Screenshot 2",
            command=(lambda: os.startfile(ss2)) if ss2 is not None else missing,
        )

        ss1_button.pack(side="left", pady=20)
        ss2_button.pack(side="left", padx=30, pady=20)
        open_button = Button(
            ss_frame, text="Open Location", command=lambda: os.startfile(path)
        )

        open_button.pack(side="left", pady=20)

    def search_fn():
        get = search_entry.get().lower()

        if not get:
            listbox_replace(MAIN, table_seps)
            return

        new_table = []

        for name in table.keys():
            if get in name.lower():
                new_table.append(name)

        if not new_table:
            new_table.append(f"No matches for '{get}'")

        listbox_replace(MAIN, new_table)

    def end_run(listbox: Listbox):
        get = indice_checks(listbox)
        if not get:
            return

        name, indice = get

        ans = mbox.askyesno(
            "Confirmation",
            "This will archive this save in the Ended Runs directory"
            "The history of the save will not be deleted",
        )

        if not ans:
            return

        _path = Path(__file__).parent / "Ended Runs"

        save_path = table[name]

        # i tested this and it works as expected
        save_path.rename(_path / save_path.name)

        # absolutely obliterate the save from memory lol
        table_seps.remove(name)
        del table[name]
        listbox.delete(indice)

        mbox.showinfo("Success", "Successfully archived saved (Ended run)")

    def statistics():
        wind = Toplevel()
        wind.title("Save Statistics")
        wind.geometry(geometry)

        text = Text(wind)
        text.pack(expand=True, fill=BOTH)

        total_scores: dict[int, str] = {}

        for path in table.values():
            score = int((code := (path / "code.txt").read_text()).split(":")[5])
            total_scores[score] = code

        to_insert = [
            f"Total saved scores: {len(table) + len(ended_runs_table)}",
            f"Total saves: {len(table)}",
        ]

        for k, v in statistics_table.items():
            to_insert.append(f"{k} saves: {v}")

        to_insert.append(f"Ended runs: {len(ended_runs_table)}")
        to_insert.append(
            f"Total hours spent waiting to save: {(len(table) + len(ended_runs_table)) * 5 / 60:.2f}h"
        )
        print([total_scores[score] for score in sorted(total_scores, reverse=True)[:5]])
        to_insert.append(f"Total amount of score saved: {sum(total_scores):,}")

        text.insert(END, "\n".join(to_insert))

    wrapper = Frame(TOP)
    wrapper.pack(side="top", anchor="w")

    wrapper_button = partial(Button, master=wrapper)
    packer = {"side": "left", "pady": 20, "padx": (20, 0)}

    viewer = wrapper_button(text="View", command=view_code)
    viewer.pack(**packer)

    deleter = wrapper_button(text="Discard Save", command=lambda: end_run(MAIN))
    deleter.pack(**packer)

    scroll = Scrollbar(TOP)
    scroll.pack(side="right", fill=Y)

    statistics_button = wrapper_button(text="Statistics", command=statistics)
    statistics_button.pack(**packer)

    # search bar

    search_frame = Frame(TOP)
    search_frame.pack()

    search_entry = Entry(search_frame, width=70, font="TkDefaultFont 15")
    search_entry.pack(anchor="center", side="left")

    search_btn = Button(search_frame, text="Search", command=search_fn)
    search_btn.pack(side="right")

    MAIN = Listbox(TOP, yscrollcommand=scroll.set)
    MAIN.pack(expand=True, fill=BOTH)

    scroll.config(command=MAIN.yview)

    # now the sauce

    join = Path(__file__).parent

    # table is on the functional side
    # table seps is to be inserted into the listbox

    table: dict[str, Path] = {}
    table_seps: list[str] = []
    statistics_table: dict[str, int] = {}

    SEP_LEN = 25
    SEP_CHAR = "-"
    SEP = SEP_CHAR * SEP_LEN
    ENDED_RUNS = "Ended Runs"

    start = perf_counter()
    print("Started indexing saves...")

    for name in gamemode + [ENDED_RUNS]:
        dir_start = perf_counter()
        print(f"Indexing {name}...")

        dir = join / name

        temp: dict[str, Path] = {}

        for d in (d for d in dir.iterdir() if d.is_dir()):
            assert name not in table, f"NAME STRING IN TABLE: {name}"
            temp[d.name] = d

        if name == ENDED_RUNS:
            ended_runs_table = {**temp}  # mutable issues
            continue

        table.update(temp)

        statistics_table[name] = len(temp)
        table_seps.extend([SEP, name, SEP, *temp])

        if not temp:
            table_seps.append(f"No Saves for {name}")
            table_seps.append("")
            # to make a space we have to do this because newlines dont work

        dir_end = perf_counter()
        print(f"Ended indexing {name} took {dir_end - dir_start:.2f}s")

    end = perf_counter()
    print(f"Ended indexing, took {end - start:.2f}s")

    listbox_replace(MAIN, table_seps)

    def erase_and_search():
        listbox_edit(MAIN, 0, "")
        search_fn()

    TOP.bind("<Return>", lambda _event: search_fn())
    TOP.bind("<Escape>", lambda _event: erase_and_search())
    TOP.mainloop()


# -----------------------------------------------------------------------------------------
# main functionality goes under here
# tab1: Settings
# -----------------------------------------------------------------------------------------

menubar = Menu(window)
window.config(menu=menubar)

menubar.add_command(label="Save Settings", command=lambda: settings_save_button(data))

menubar.add_command(
    label="GitHub Repository",
    command=lambda: webbrowser.open(
        "https://github.com/GDOlivercoding/ArrasManager", new=2
    ),
)

menubar.add_command(label="Manage Saves", command=manage_saves_widget)

settings_frame = ttk.Notebook(tab1)
confirm_tab = ttk.Frame(settings_frame)
open_dirname_tab = ttk.Frame(settings_frame)
pic_export_tab = ttk.Frame(settings_frame)
pic_dir_tab = ttk.Frame(settings_frame)
pic_filenames_tab = ttk.Frame(settings_frame)

settings_frame.add(confirm_tab, text="Confirmation")
settings_frame.add(pic_export_tab, text="Picture exporting")
settings_frame.add(pic_dir_tab, text="Screenshot directory")
settings_frame.add(pic_filenames_tab, text="Screenshot filenames")
settings_frame.add(open_dirname_tab, text="Reveal directory in file explorer")

settings_frame.pack(anchor="nw", pady=(10, 0))

header = Label(confirm_tab, text="Setting 1:", font=("great vibes", 30))
header.pack(anchor="nw")

# confirmation setting

var_confirmation = BooleanVar()

cb_confirmation = Checkbutton(
    confirm_tab,
    text="Ask for confirmation when creating a save",
    variable=var_confirmation,
    onvalue=True,
    offvalue=False,
    font=("great vibes", 15),
    background="light green",
    foreground="gray",
    activebackground="green",
    activeforeground="dark gray",
)

cb_confirmation.pack(anchor="nw")
if data.confirmation:
    cb_confirmation.invoke()

setting_5 = Label(open_dirname_tab, text="Setting 5:", font=("great vibes", 30))
setting_5.pack(anchor="nw")

var_dirname = BooleanVar()

cb_open_dirname = Checkbutton(
    open_dirname_tab,
    text="Open directory location in file explorer",
    variable=var_dirname,
    onvalue=True,
    offvalue=False,
    font=("great vibes", 15),
    background="light green",
    foreground="gray",
    activebackground="green",
    activeforeground="dark gray",
)
cb_open_dirname.pack(anchor="nw", pady=(10, 0))

if data.open_dirname:
    cb_open_dirname.invoke()

# pic amt setting

header2 = Label(pic_export_tab, text="Setting 2:", font=("great vibes", 30))
header2.pack(anchor="nw")

pic_label = Label(pic_export_tab, text="Picture saving", font=("great vibes", 20))
pic_label.pack(anchor="nw")

pic_scale = Scale(
    pic_export_tab,
    orient=HORIZONTAL,
    from_=2,
    to=0,
    length=100,
    tickinterval=1,
    font=("great vibes", 10),
    resolution=1,
    showvalue=False,
)
pic_scale.set(data.pic_export)
pic_scale.pack(anchor="nw")

header3 = Label(pic_dir_tab, text="Setting 3:", font=("great vibes", 30))
header3.pack(anchor="nw")

ss_text = Label(pic_dir_tab, text="Screenshots folder", font=("great vibes", 20))
ss_text.pack(anchor="nw")

folder_button = Button(
    pic_dir_tab, text="Set folder", command=lambda: ss_dir_button(data, cur_path)
)
folder_button.pack(anchor="nw")

cur_path = StringVar()
cur_path.set(f"Current Path: {data.ss_dir}")

ss_text2 = Label(pic_dir_tab, text="", textvariable=cur_path, font=("great vibes", 10))
ss_text2.pack(anchor="nw")

Value.windowed = StringVar(value=data.windowed_ss, name="windowed")
Value.fullscreen = StringVar(value=data.fullscreen_ss, name="fullscreen")
Value.single = StringVar(value=data.single_ss, name="single")


def screenshot_setter(str_var: StringVar, label: Label):
    string = simpledialog.askstring(
        f"{str(str_var).capitalize()}", f"Enter name for {str(str_var)} screenshot"
    )

    # ignore non and empty strings
    if string:
        str_var.set(string)
        label.config(text=string)


packer: dict = {"anchor": "nw", "pady": (0, 30)}

displayer = partial(Label, master=pic_filenames_tab, font=("great vibes", 10))
setter = partial(Button, master=pic_filenames_tab, text="Set")

Label1 = Label(pic_filenames_tab, text="Windowed picture:", font=("great vibes", 20))
Label1.pack(anchor="nw", pady=(20, 0))

windowed_displayer = displayer(text=Value.windowed.get())
windowed_setter = setter(
    command=lambda: screenshot_setter(Value.windowed, windowed_displayer)
)
windowed_setter.pack(anchor="nw")

windowed_displayer.pack(**packer)

Label2 = Label(pic_filenames_tab, text="Fullscreen picture", font=("great vibes", 20))
Label2.pack(anchor="nw", pady=(20, 0))

fullscreen_displayer = displayer(text=Value.fullscreen.get())
fullscreen_setter = setter(
    command=lambda: screenshot_setter(Value.fullscreen, fullscreen_displayer)
)
fullscreen_setter.pack(anchor="nw")

fullscreen_displayer.pack(**packer)

label_single = Label(
    pic_filenames_tab, text="Singular picture", font=("great vibes", 20)
)
label_single.pack(anchor="nw", pady=(20, 0))

single_displayer = displayer(text=Value.single.get())
single_setter = setter(
    command=lambda: screenshot_setter(Value.single, single_displayer)
)
single_setter.pack(anchor="nw")

single_displayer.pack(**packer)

# Files info tab 3


def view_widget(context: str, title: str):
    new_window = Tk()
    new_window.title(title)
    new_window.geometry("800x400")
    new_window.resizable(False, False)

    scroll = Scrollbar(new_window)
    scroll.pack(side=RIGHT, fill=Y)

    main_text = Text(new_window, yscrollcommand=scroll.set)

    for line in context.splitlines():
        main_text.insert(END, line + "\n")

    main_text.config(state=DISABLED)
    main_text.pack(anchor="nw", expand=True, fill=BOTH)

    scroll.config(command=main_text.yview)


# tab 4: view local txts
tab4_header = Label(tab3, text="View Local Files", font=("great vibes", 40))
tab4_header.pack(anchor="center")

settings_label = Label(tab3, text="Settings file", font=("great vibes", 30))
settings_label.pack(anchor="nw")

settings = data.get_dict()
store = []
for item in settings.items():
    store.append(f"{item[0]}: {item[1]}")


def view_settings(data: Settings):
    view_widget(
        title="Settings.json",
        context="\n".join(f"{k}: {v}" for k, v in data.get_dict().items()),
    )


view_stgs_button = Button(
    tab3, text="View settings", command=lambda data=data: view_settings(data)
)
view_stgs_button.pack(anchor="nw")

reset_settings = Button(
    tab3,
    text="Reset settings",
    command=lambda: settings_reset(cb_confirmation, pic_scale, data, cur_path),
)
reset_settings.pack(anchor="nw", pady=(20, 0))

# <--------------------------------->

logger_label = Label(tab3, text="Logger file", font=("great vibes", 30))
logger_label.pack(anchor="nw", pady=(20, 0))

if file_logdata.exists():
    with file_logdata.open("r", encoding=ENCODING) as file:
        contents = file.readlines()

    new_contents = " ".join(contents)
else:
    new_contents = "0"

new_contents = new_contents[1:]

logfolder_button = Button(
    tab3,
    text="View logs",
    command=lambda new_contents=new_contents: view_widget(
        title="Logdata.txt", context=new_contents
    ),
)
logfolder_button.pack(anchor="nw")

# <---------------------------------->

del_logger_button = Button(tab3, text="Reset logdata file", command=delete_logger)
del_logger_button.pack(anchor="nw", pady=(20, 0))

export_log = Button(tab3, text="Export logdata", command=export_logdata)
export_log.pack(anchor="nw", pady=(20, 0))

saves_label = Label(tab3, text="Saves Location", font=("great vibes", 30))
saves_label.pack(anchor="nw", pady=(20, 0))

open_saves = partial(startfile, filepath=Path(__file__).parent)

open_saves_button = Button(tab3, text="Open", command=open_saves)
open_saves_button.pack(anchor="w", padx=(10, 0), pady=(5, 0))


# tab 5: Unclaimed
def copy_command():
    selection = lb_unclaimed.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = lb_unclaimed.get(selection)

    try:
        import pyperclip

    except ModuleNotFoundError:
        mbox.showerror(
            title="ERROR",
            message="'pyperclip' module is not installed, this functionality can only be accessed with the module",
        )
        return

    pyperclip.copy(f"$claim {code}")
    mbox.showinfo(title="Success", message="Successfully copied message!")


def claim_command():
    global lb_unclaimed, data
    selection = lb_unclaimed.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = lb_unclaimed.get(selection)

    if not mbox.askyesno(title="CONFIRMATION", message="Are you sure?"):
        return

    try:
        del data.unclaimed[code]
        lb_unclaimed.delete(selection)
    except ValueError:
        mbox.showerror(title="ERROR", message="Selected object not found")


scrollbar = Scrollbar(tab5)
scrollbar.pack(side=RIGHT, fill=Y)

lb_unclaimed = Listbox(tab5, font=("great vibes", 8))
lb_unclaimed.config(width=550, height=20, yscrollcommand=scrollbar.set)
lb_unclaimed.insert(END, *data.unclaimed.keys())
lb_unclaimed.pack(anchor="center")

scrollbar.config(command=lb_unclaimed.yview, width=20)

button = Button(tab5, text="Copy Claim Command", font=("", 10), command=copy_command)
button.pack(pady=20, anchor="center")

button = Button(
    tab5, text="Claim Code (Remove from list)", font=" 10", command=claim_command
)
button.pack(pady=(50, 0), anchor="center")


# save changes upon exiting
def destroy_application(
    data: Settings,
    var_confirmation: BooleanVar,
    var_dirname: BooleanVar,
    pic_scale: Scale,
):
    Value.close_clock = datetime.now()

    # get values
    data.confirmation = var_confirmation.get()
    data.open_dirname = var_dirname.get()

    scale_int = pic_scale.get()

    if scale_int in (0, 1, 2):
        data.pic_export = scale_int
    else:
        data.pic_export = 0

    data.fullscreen_ss = Value.fullscreen.get()
    data.windowed_ss = Value.windowed.get()
    data.single_ss = Value.single.get()

    # dump settings
    with file_settings.open("w") as file:
        dump(data.get_dict(), fp=file)

    # if logdata was set to be reset or if the user didnt change anything
    # do not write to it

    if was_deleted or data.is_data_same(START_DATA):
        exit()

    # ------------------------------------------------------------
    # logdata block
    # ------------------------------------------------------------

    with file_logdata.open("r", encoding=ENCODING) as file:
        contents = file.readlines()

    try:
        dummy = int(contents[0].strip())
    except ValueError:
        dummy = 0
        contents[0] = "1"

    except IndexError:
        dummy = 0
        contents.append("0")

    dummy += 1
    contents[0] = str(dummy) + "\n"

    SET_TO: str = f"""

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
modify.py instance at {datetime.now().strftime("%d.%m.")}, instance number {dummy}:     

Saving:
confirmation set to {data.confirmation}
picture save set to {data.pic_export}
ssdir set to {data.ss_dir}

modify.py ran at {Value.open_clock}
killed at {Value.close_clock}
total time spent in modify.py: {(Value.close_clock - Value.open_clock).seconds}s
"""
    contents.append(SET_TO)
    with file_logdata.open("w", encoding="utf-8") as file:
        file.writelines(contents)

    exit()


window.protocol(
    "WM_DELETE_WINDOW",  # WINDOW MANAGER DELETE WINDOW
    lambda data=data: destroy_application(
        data,
        var_confirmation,
        var_dirname,
        pic_scale,
    ),
)

window.tk.mainloop()
