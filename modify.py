from init import (
    Settings,
    partial,
    create_dict,
    dump, 

    file_logdata,
    file_settings,
    screenshot_dir,
    base_dir,
    was_deleted,
)

from tkinter import (    
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

    filedialog as fdialog,
    messagebox as mbox,
    simpledialog, 
)

from tkinter import ttk
from datetime import datetime
from json import load
from typing import Never
import webbrowser
from pathlib import Path

class Value:
    windowed: StringVar
    fullscreen: StringVar
    single: StringVar

    open_clock: datetime = datetime.now()
    close_clock: datetime


# main window
window = Tk()
window.title("Modify how arras.py functions")
window.geometry("700x550")
window.resizable(False, False)

# read settings
with file_settings.open("r") as file:
    data = create_dict(load(fp=file))

# MAINHEADER:
MainHeader = Label(
    text="All changes are automatically recorded when closing the program",
    font=("great vibes", 15),
)
MainHeader.pack(anchor="center")

# CONSTRUCT MAIN TAB WINDOWS
mytab = ttk.Notebook(window)
tab1 = ttk.Frame(mytab)
#tab2 = ttk.Frame(mytab)
tab3 = ttk.Frame(mytab)
#tab4 = ttk.Frame(mytab)
tab5 = ttk.Frame(mytab)
mytab.add(tab1, text="Settings")
#mytab.add(tab2, text="App Info")
mytab.add(tab3, text="View Local Txts")
#mytab.add(tab4, text="Advanced Automation")
mytab.add(tab5, text="Unclaimed Saves")
mytab.pack(anchor="nw")

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# functions, TODO: fix naming convention
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


def delete_logger() -> None:
    global was_deleted  # check global environment in envs

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


def _button_press(data: Settings, cur_path: StringVar):
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


def set_default(
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

    with file_logdata.open("r") as file:
        contents = file.readlines()

    fp = fdialog.askdirectory(initialdir=base_dir / "Desktop")
    if not fp:
        mbox.showerror(title="No input", message="No directory selected")
        return
    
    fp = Path(fp)

    with (fp / "Logdata copy.txt").open("w") as f:
        f.writelines(contents)

    mbox.showinfo(
        title="Success",
        message="Successfully created a copy of the logger file in the desired directory!",
    )


def get_height(text: str) -> int:
    return len(text.split("\n"))


def save_button_press(data: Settings) -> None:
    with file_settings.open("w") as file:
        dump(fp=file, obj=data.get_dict())

    mbox.showinfo(title="Success", message="Settings saved")

# -----------------------------------------------------------------------------------------
# main functionality goes under here
# tab1: Settings
# -----------------------------------------------------------------------------------------

menubar = Menu(window)
window.config(menu=menubar)

menubar.add_command(label="Save Settings", command=lambda: save_button_press(data))
menubar.add_command(
    label="Open Docs",
    command=lambda: webbrowser.open("https://github.com/GDOlivercoding/ArrasManager", new=1, autoraise=True)
)

tab_nb = ttk.Notebook(tab1)
confirm_tab = ttk.Frame(tab_nb)
open_dirname_tab = ttk.Frame(tab_nb)
pic_export_tab = ttk.Frame(tab_nb)
pic_dir_tab = ttk.Frame(tab_nb)
pic_filenames_tab = ttk.Frame(tab_nb)

tab_nb.add(confirm_tab, text="Confirmation")
tab_nb.add(pic_export_tab, text="Picture exporting")
tab_nb.add(pic_dir_tab, text="Screenshot directory")
tab_nb.add(pic_filenames_tab, text="Screenshot filenames")
tab_nb.add(open_dirname_tab, text="Reveal directory in file explorer")

tab_nb.pack(anchor="nw", pady=(10, 0))

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

"""confirm_txt_widget = Text(confirm_tab)
confirm_txt_widget.insert(END, setting1)
confirm_txt_widget.config(state="disabled", height=get_height(setting1), width=75)
confirm_txt_widget.pack(anchor="nw")"""

Label(open_dirname_tab, text="Setting 5:", font=("great vibes", 30)).pack(anchor="nw")

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


"""pic_txt_widget = Text(pic_export_tab)
pic_txt_widget.insert(END, setting2)
pic_txt_widget.config(state="disabled", height=get_height(setting2), width=65)
pic_txt_widget.pack(anchor="nw")"""

header3 = Label(pic_dir_tab, text="Setting 3:", font=("great vibes", 30))
header3.pack(anchor="nw")

ss_text = Label(pic_dir_tab, text="Screenshots folder", font=("great vibes", 20))
ss_text.pack(anchor="nw")

folder_button = Button(
    pic_dir_tab, text="Set folder", command=lambda: _button_press(data, cur_path)
)
folder_button.pack(anchor="nw")

cur_path = StringVar()
cur_path.set(f"Current Path: {data.ss_dir}")

ss_text2 = Label(pic_dir_tab, text="", textvariable=cur_path, font=("great vibes", 10))
ss_text2.pack(anchor="nw")

"""ss_text_widget = Text(pic_dir_tab)
ss_text_widget.insert(END, setting3)
ss_text_widget.config(state=DISABLED, height=get_height(setting3), width=80)
ss_text_widget.pack(anchor="nw")"""

Value.windowed = StringVar(value=data.windowed_ss, name="windowed")
Value.fullscreen = StringVar(value=data.fullscreen_ss, name="fullscreen")
Value.single = StringVar(value=data.single_ss, name="single")


def widget_setter(var: StringVar, label: Label, /, *, title: str, prompt: str):
    val = simpledialog.askstring(title, prompt)

    # ignore non and empty strings
    if val:
        var.set(val)
        label.config(text=val)


widget_caller = lambda mode, label: widget_setter(
    mode,
    label,
    title=f"{str(mode).capitalize()}",
    prompt=f"Enter name for {str(mode)} screenshot",
)

packer: dict = {"anchor": "nw", "pady": (0, 30)}

displayer = partial(Label, master=pic_filenames_tab, font=("great vibes", 10))
setter = partial(Button, master=pic_filenames_tab, text="Set")

Label1 = Label(pic_filenames_tab, text="Windowed picture:", font=("great vibes", 20))
Label1.pack(anchor="nw", pady=(20, 0))

windowed_displayer = displayer(text=Value.windowed.get())
windowed_setter = setter(
    command=lambda: widget_caller(Value.windowed, windowed_displayer)
)
windowed_setter.pack(anchor="nw")

windowed_displayer.pack(**packer)

Label2 = Label(pic_filenames_tab, text="Fullscreen picture", font=("great vibes", 20))
Label2.pack(anchor="nw", pady=(20, 0))

fullscreen_displayer = displayer(text=Value.fullscreen.get())
fullscreen_setter = setter(
    command=lambda: widget_caller(Value.fullscreen, fullscreen_displayer)
)
fullscreen_setter.pack(anchor="nw")

fullscreen_displayer.pack(**packer)

Label3 = Label(pic_filenames_tab, text="Singular picture", font=("great vibes", 20))
Label3.pack(anchor="nw", pady=(20, 0))

single_displayer = displayer(text=Value.single.get())
single_setter = setter(command=lambda: widget_caller(Value.single, single_displayer))
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

    for line in context.split("\n"):
        main_text.insert(END, line + "\n")

    main_text.config(state=DISABLED)
    main_text.pack(anchor="nw", expand=True, fill=BOTH)

    scroll.config(command=main_text.yview)

"""
descriptor_label = partial(Label, master=tab2, font=("great vibes", 30))

descriptor_label(text="Main App Info").pack(anchor="nw", pady=(20, 0))

app_descriptor = Button(
    tab2, text="View app info", command=lambda: view_widget(app_info, "App Info")
)
app_descriptor.pack(anchor="nw", pady=(20, 0))

descriptor_label(text="modify guidance").pack(anchor="nw", pady=(20, 0))

modify_descriptor = Button(
    tab2,
    text="modify.py info",
    command=lambda: view_widget(modify_text, "Modify.py Info"),
)
modify_descriptor.pack(anchor="nw", pady=(20, 0))

descriptor_label(text="arras usage").pack(anchor="nw", pady=(20, 0))

arras_descriptor = Button(
    tab2, text="arras.py info", command=lambda: view_widget(arras_text, "arras.py Info")
)
arras_descriptor.pack(anchor="nw", pady=(20, 0))

descriptor_label(text="how to use installer").pack(anchor="nw", pady=(20, 0))

inst_descriptor = Button(
    tab2,
    text="installer.py info",
    command=lambda inst_text=inst_text: view_widget(inst_text, "installer.py Info"),
)
inst_descriptor.pack(anchor="nw", pady=(20, 0))"""

# tab 4: view local txts
tab4_header = Label(tab3, text="View Local Txt Files", font=("great vibes", 40))
tab4_header.pack(anchor="center")

settings_label = Label(tab3, text="Settings file", font=("great vibes", 30))
settings_label.pack(anchor="nw")

settings = data.get_dict()
store = []
for item in settings.items():
    store.append(f"{item[0]}: {item[1]}")


def stgs_func(data: Settings):
    view_widget(
        title="Settings.json",
        context="\n".join(f"{k}: {v}" for k, v in data.get_dict().items()),
    )


view_stgs_button = Button(
    tab3, text="View settings", command=lambda data=data: stgs_func(data)
)
view_stgs_button.pack(anchor="nw")

reset_stgs_button = Button(
    tab3,
    text="Reset settings",
    command=lambda: set_default(cb_confirmation, pic_scale, data, cur_path),
)
reset_stgs_button.pack(anchor="nw", pady=(20, 0))

# <--------------------------------->

logger_label = Label(tab3, text="Logger file", font=("great vibes", 30))
logger_label.pack(anchor="nw", pady=(20, 0))

if file_logdata.exists():
    with file_logdata.open("r") as file:
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

# <----------------------------------->
# tab4: automation

"""Label(tab4, text="Extra Automation Settings", font=("great vibes", 25)).pack(
    anchor="center", pady=(10, 0)
)

var_automation = BooleanVar(value=data.automation)

Checkbutton(
    master=tab4,
    text="Enable Advanced Automation",
    font=("great vibes", 20),
    variable=var_automation,
    onvalue=True,
    offvalue=False,
    background="light green",
    foreground="gray",
    activebackground="green",
    activeforeground="dark gray",
).pack(anchor="nw")

var_force = BooleanVar(value=data.force_automation)

Checkbutton(
    master=tab4,
    text="Force Automation Popup",
    font=("great vibes", 20),
    variable=var_force,
    onvalue=True,
    offvalue=False,
    background="light green",
    foreground="gray",
    activebackground="green",
    activeforeground="dark gray",
).pack(anchor="nw", pady=(10, 0))

Label(
    tab4,
    text="Default amount of seconds to wait\nbefore attempting to save\nwith current resources:",
    font=("great vibes", 15),
).pack(anchor="nw", pady=(10, 0))

scl_def_automation = Scale(
    tab4, from_=300, to=0, orient=HORIZONTAL, length=220, resolution=10
)
scl_def_automation.set(data.def_time)
scl_def_automation.pack(anchor="nw", padx=(50, 0))"""


# tab 5: Unclaimed
def copy_command():
    global listbox
    selection = listbox.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = listbox.get(selection)

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
    global listbox, data
    selection = listbox.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = listbox.get(selection)

    if not mbox.askyesno(title="CONFIRMATION", message="Are you sure?"):
        return

    try:
        del data.unclaimed[code]
        listbox.delete(selection)
    except ValueError:
        mbox.showerror(title="ERROR", message="Selected object not found")


scrollbar = Scrollbar(tab5)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(tab5, font=("great vibes", 8))
listbox.config(width=550, height=20, yscrollcommand=scrollbar.set)
listbox.insert(END, *data.unclaimed.keys())
listbox.pack(anchor="center")

scrollbar.config(command=listbox.yview, width=20)

button = Button(tab5, text="Copy Claim Command", font=("", 10), command=copy_command)
button.pack(pady=20, anchor="center")

button = Button(
    tab5, text="Claim Code (Remove from list)", font=("", 10), command=claim_command
)
button.pack(pady=50, anchor="center")


# save changes upon exiting
def Save(
    data: Settings,
    var_confirmation: BooleanVar,
    var_dirname: BooleanVar,
    #var_automation: BooleanVar,
    #var_force: BooleanVar,
    scale: Scale,
    #def_scale: Scale,
) -> Never:

    Value.close_clock = datetime.now()

    # get values
    data.confirmation = var_confirmation.get()
    data.open_dirname = var_dirname.get()
    #data.automation = var_automation.get()
    #data.force_automation = var_force.get()

    scale_int = scale.get()
    #data.def_time = int(def_scale.get())

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
    # if logdata was set to be reset do not write to it
    if was_deleted:
        exit()

    # ------------------------------------------------------------
    # logdata block
    # ------------------------------------------------------------

    with file_logdata.open("r") as file:
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
modify.py instance at {str(datetime.now()).split(".")[0].split(" ")[0]} {Value.open_clock}, instance number {dummy}:     

Saving:
confirmation set to {data.confirmation}
picture save set to {data.pic_export}
ssdir set to {data.ss_dir}

modify.py ran at {Value.open_clock}
killed at {Value.close_clock}
total time spent in modify.py: {Value.close_clock - Value.open_clock}
"""
    contents.append(SET_TO)
    with file_logdata.open("w", encoding="utf-8") as file:
        file.writelines(contents)
    exit()


window.protocol(
    "WM_DELETE_WINDOW",#  # WINDOW MANAGER DELETE WINDOW
    lambda data=data: Save(
        data,
        var_confirmation,
        var_dirname,
        #var_automation,
        #var_force,
        pic_scale,
        #scl_def_automation,
    ),
)

window.tk.mainloop()
