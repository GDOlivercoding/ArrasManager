from init import (
    # modules
    os,
    datetime,
    timedelta,
    fdialog,
    sd,
    mbox,
    ttk,
    Path,
    # cls
    Settings,
    partial,
    Never,
    Literal,
    # funcs
    create_dict,
    load,
    dump,
    copy_clipboard,  # actually a function
    # vars
    file_logdata,
    file_settings,
    import_type,
    was_deleted,
    # tkinter
    # tkinter gui elements (cls)
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
    t_BOTH,
    RIGHT,
    HORIZONTAL,
    DISABLED,
    END,
)

# force self directory

os.chdir(os.path.dirname(os.path.abspath(__file__)))

_ = open_clock = f"{datetime.now():%X}"
__ = _.split(":")
open_val: list[int] = []
for i in __:
    open_val.append(int(i))


# main window
window = Tk()
window.title("Modify how arras.py functions")
window.geometry("700x550")
window.resizable(False, False)

# read settings
with open(
    file_settings,
    "r",  # read mode
    encoding="utf_8",
) as file:
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
tab2 = ttk.Frame(mytab)
tab3 = ttk.Frame(mytab)
tab4 = ttk.Frame(mytab)
tab5 = ttk.Frame(mytab)
mytab.add(tab1, text="Settings")
mytab.add(tab2, text="App Info")
mytab.add(tab3, text="View Local Txts")
mytab.add(tab4, text="Advanced Automation")
mytab.add(tab5, text="Unclaimed Saves")
mytab.pack(anchor="nw")

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# functions, TODO: fix naming convention
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


def delete_logger() -> None:
    global was_deleted  # check global environment in envs

    if (
        mbox.askyesno(
            title="Confirmation",
            message="Are you sure you want to delete the ENTIRE logging file? The file will still exist and log data, all of its contents WILL be deleted!",
        )
        != True
    ):
        return
    with open(file_logdata, "w", encoding="utf-8") as file:
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

    with open(file_settings, "w", encoding="utf-8") as file:
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
    data.ss_dir = Path.home() / "Pictures" / "Screenshots"
    cur_path.set(f"Current Path: {data.ss_dir}")
    mbox.showinfo(title="Success", message="Successfully set all options to default!")
    return


def export_logdata() -> None:
    if (
        mbox.askyesno(
            title="Confirmation",
            message="Are you sure? This will create a copy of the log file!",
        )
        != True
    ):
        return

    with open(file_logdata, "r", encoding="utf-8") as file:
        contents = file.readlines()

    fp: str = fdialog.askdirectory(initialdir=Path.home() / "Desktop")
    if not fp:
        mbox.showerror(title="No input", message="No directory selected")
        return

    with open(os.path.join(fp, "Logdata copy.txt"), "w", encoding="utf-8") as f:
        f.writelines(contents)
    mbox.showinfo(
        title="Success",
        message="Successfully created a copy of the logger file in the desired directory!",
    )
    return None


def c_sub_dt(list1: list[int], list2: list[int]) -> str:
    """returns a datetime string format
    with the time in between the two values"""
    rlist: list[int] = []

    if list1[0] > list2[0]:
        return "1day+"
    else:
        rlist.append(list2[0] - list1[0])

    c = -1
    while True:
        c += 1

        try:
            if list1[c] > list2[c]:
                rlist[c - 1] = int(rlist[c - 1]) + 1
                rlist.append(list1[c] - list2[c])
            else:
                rlist.append(list2[c] - list1[c])
        except IndexError:
            break

    slist: list[str] = [str(i) for i in rlist]

    c = -1
    for i in slist:
        c += 1
        if len(i) < 2:
            slist[c] = "0" + i

    newstring: str = ":".join(slist)
    return str(newstring)


def get_height(text: str) -> int:
    return len(text.split("\n"))


def save_button_press(data: Settings) -> None:
    with open(file_settings, "w", encoding="utf-8") as file:
        dump(fp=file, obj=data.get_dict())

    mbox.showinfo(title="Success", message="Settings saved")
    return


# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# text blocks for input, TODO: fix naming convention
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------

setting1: str = """Ask for confirmation when creating a save
the time when the confirmation window is supposed to be opened
should be before anything happens
safe option to make sure nothing bad happens if you accidentally
run the program!"""
setting2: str = """Set the amount of screenshots you take
when you save

default is 0 but now screenshots are required for some saves
i recommend at least 1 screenshot for minimal proof

for now you have to manually screenshot them with Win + PrtSc
but in the future i'll make it completely automatic
from the point when you start AFKing to save"""

# NOTE: unused (setting3)
_tickinput: str = """Create an addition line in the file that logs all data (logdata.txt),
that prompts the user to save the code and makes it more organized when
looking for unclaimed codes, default is False.
The extra code claim prompt is going to shown at the end of the report in logdata.txt.
the code is still going to be saved in the individual directory (save)."""

setting3: str = """Set the directory to where the program should reach for the screenshots to save
by default it is C:/Users/*/Pictures/Screenshots
some computers may have it renamed or have a different language
This should be the folder where PrtSc screenshots get saved
to get the screenshots folder manually:
- Take screenshot with Win + PrtSc
- Open file explorer
- Recently opened
- Right click the last file(the screenshot) and view properties
There is a specified path
come back and input the path here"""

modify_text: str = """modify.py is used to change and do everything with how the program behaves.
it can be launched at any time and provides settings and useful information.

you can currently see 3 tabs of which you saw 2 already:

- Settings tab
  Add confirmation
  Change the amount of death screenshots to save
  And setup the screenshot directory

- App Info
  The current tab
  Contains information about the app
  And all of its files

- View local txts
  View data files
  Modify them
  Reset them
  Export them
"""
arras_text: str = """arras.py is the main application
when ran, it will collect the code
extract it
and create a directory based in and on the code
run when you have the appropriate amount of screenshots taken
and when you have your code saved in your clipboard (optional)
"""
inst_text: str = """
installer.py is meant to be ran when you download the 3 files of my software
when ran you're present with 3 options:

 - Yes
   this will initialise the main installation process
   it's what you've done to get here
   creates data files and
   creates the whole directory tree

 - No
   This will rapair your data files
   if they're broken or if you damaged them
   Run if you've gotten an error telling you to do so

 - Cancel
   Do not perform any activity
"""
app_info: str = """Hello and welcome to the arras save manager!
This app allows you to organize and store your saves easily.

HOW TO USE:
When saving, this app (arras.py) is meant to be run and create a directory with screenshots and the code.
First the way the app obtains the code to store it and extract information from it create the dirname and
puts it in the correct directory:

by default when ran, the app manually asks you to enter the code, but if you install a extra package it can take the code
from your clipboard improving convenince.
if you want such action to happen open up a command prompt and run:

pip install pyperclip (<- not a spelling error)
                      or
pip install clipboard

both will work (For advanced people, pyperclip overrides clipboard when both installed), this is 100% optional and is used
cleanly for convenience

disabling taking the code from your clipboard when one of those libraries are installed will be added in the near future

when used it can also easily store screenshots of your score
in the "Settings" tab of the app you have opened right now you can set how many screenshots to save

But yes unfortunately those screenshots have to be manually taken by you,
set the amount you want and the program will rename them
and move them to the appropriate directory (To take the screenshot, press win + PrtSc)

if your computer isn't set in english or you have modified your screenshots directory, you may have to set that yourself
in the settings 

Aight heres the actual "How to use":
- Save a score in game
- Take the amount of screenshots you set using Win + PrtSc
- Copy the code
- Enter the code in the console (if you havent downloaded any external library mentioned above
otherwise the code gets taken from your clipboard)

the program will automatically store the code and screenshots in the correct gamemode folder 
also will create a name for the folder with a "date, score, tank class" format

YOUR DATA IS NOT BEING SENT ANYWHERE
THIS PROGRAM IS 100% LOCAL AND OFFLINE
YOUR DATA IS BEING STORED IN A LOCAL FILE CALLED LOGDATA.TXT, WHICH IS USED ONLY WHEN AN ERROR OCCURS, 
OR TO RECALL HISTORY LOCALLY!!
THIS PROGRAM WILL NOT STEAL ANY OF YOUR INPUTS
LOGGING IN THE LOGDATA.TXT FILE CAN BE DISABLED

If you do not understand anything said here, DM celestial_raccoon on discord and i'll add it to this massive wall of text"""

# -----------------------------------------------------------------------------------------
# main functionality goes under here
# tab1: Settings
# -----------------------------------------------------------------------------------------

menubar = Menu(window)
window.config(menu=menubar)

menubar.add_command(label="Save Settings", command=lambda: save_button_press(data))
menubar.add_command(
    label="Open Docs",
    command=lambda: mbox.showinfo(
        title="Not Implemented", message="Not implemented yet"
    ),
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

confirm_txt_widget = Text(confirm_tab)
confirm_txt_widget.insert(END, setting1)
confirm_txt_widget.config(state="disabled", height=get_height(setting1), width=75)
confirm_txt_widget.pack(anchor="nw")

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


pic_txt_widget = Text(pic_export_tab)
pic_txt_widget.insert(END, setting2)
pic_txt_widget.config(state="disabled", height=get_height(setting2), width=65)
pic_txt_widget.pack(anchor="nw")


# NOTE: unused setting3
r"""
code = BooleanVar()
code.set(False)
ticklbl = Checkbutton(
    tab1,
    text="Add an extra code to logdata.txt",
    variable=code,
    onvalue=True,
    offvalue=False,
    font=("great vibes", 15),
    background="light green",
    foreground="gray",
    activebackground="green",
    activeforeground="dark gray",
)
ticklbl.pack(anchor="nw")
if data. == True:
    contents.append("New report: set_code is True, extra code checkbutton invoked\n")
    ticklbl.invoke()
contents.append("\n")


ticktext = Text(tab1)
ticktext.insert(END, tickinput)
ticktext.config(state="disabled", height=6, width=71)
ticktext.pack(anchor="nw")

header4 = Label(tab1, text="Setting 4:", font=("great vibes", 30))
header4.pack(anchor="nw")"""

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

ss_text_widget = Text(pic_dir_tab)
ss_text_widget.insert(END, setting3)
ss_text_widget.config(state=DISABLED, height=get_height(setting3), width=80)
ss_text_widget.pack(anchor="nw")


# lets think how we do this
# maybe we could make an entry field

windowed, fullscreen, single = [
    StringVar(value=data.windowed_ss, name="windowed"),
    StringVar(value=data.fullscreen_ss, name="fullscreen"),
    StringVar(value=data.single_ss, name="single"),
]


def widget_setter(var: StringVar, /, *, title: str, prompt: str):
    val = sd.askstring(title, prompt)
    if val is not None:
        var.set(val)


widget_caller = lambda mode: widget_setter(
    mode,
    title=f"{str(mode).capitalize()}",
    prompt=f"Enter name for {str(mode)} screenshot",
)

packer: dict = {"anchor": "nw", "pady": (0, 30)}

displayer = partial(Label, master=pic_filenames_tab, font=("great vibes", 10))
setter = partial(Button, master=pic_filenames_tab, text="Set")

Label1 = Label(pic_filenames_tab, text="Fullscreen picture:", font=("great vibes", 20))
Label1.pack(anchor="nw", pady=(20, 0))

windowed_setter = setter(command=lambda: widget_caller(windowed))
windowed_setter.pack(anchor="nw")

windowed_displayer = displayer(text=windowed.get())
windowed_displayer.pack(**packer)

Label2 = Label(pic_filenames_tab, text="Windowed picture", font=("great vibes", 20))
Label2.pack(anchor="nw", pady=(20, 0))

fullscreen_setter = setter(command=lambda: widget_caller(fullscreen))
fullscreen_setter.pack(anchor="nw")

fullscreen_displayer = displayer(text=fullscreen.get())
fullscreen_displayer.pack(**packer)

Label3 = Label(pic_filenames_tab, text="Singular picture", font=("great vibes", 20))
Label3.pack(anchor="nw", pady=(20, 0))

single_setter = setter(command=lambda: widget_caller(single))
single_setter.pack(anchor="nw")

single_displayer = displayer(text=single.get())
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
    main_text.pack(anchor="nw", expand=True, fill=t_BOTH)

    scroll.config(command=main_text.yview)


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
inst_descriptor.pack(anchor="nw", pady=(20, 0))

del descriptor_label

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

    settings = data.get_dict()
    store = []

    for k, v in settings.items():
        store.append(f"{k}: {v}")

    view_widget(title="Settings.json", context="\n".join(store))


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

if os.path.exists(file_logdata):
    with open(file_logdata, "r", encoding="utf-8") as file:
        __contents = file.readlines()

    del __contents[0]

    contents = " ".join(__contents)
else:
    contents = "0"

logfolder_button = Button(
    tab3,
    text="View logs",
    command=lambda contents=contents: view_widget(
        title="Logdata.txt", context=contents
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

Label(tab4, text="Extra Automation Settings", font=("great vibes", 25)).pack(
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
scl_def_automation.pack(anchor="nw", padx=(50, 0))


# tab 5: Unclaimed
def copy_command():
    global listbox
    selection = listbox.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = listbox.get(selection)

    if not import_type:
        mbox.showerror(
            title="ERROR",
            message="'pyperclip' module is not installed, this functionality can only be accessed with the module",
        )
    else:
        copy_clipboard(f"$claim {code}")
        mbox.showinfo(title="Success", message="Successfully copied message!")


def claim_command():
    global listbox, data
    selection = listbox.curselection()
    if not selection:
        mbox.showerror(title="ERROR", message="No code selected")
        return

    code = listbox.get(selection)

    if mbox.askyesno(title="CONFIRMATION", message="Are you sure?") != True:
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

# white: normal
# yellow: half +- time expired
# red: about to expire
# black: expired

colored_unclaimed: dict[str, Literal["white", "yellow", "red", "black"]] = {}

"""
for code, iso in data.unclaimed.items():
    time = datetime.fromisoformat(iso)
    comparison = datetime.now()
    comparison -= time

    if comparison <= timedelta(days=0):
        colored_unclaimed[code] = "black"

    elif comparison <= timedelta(days=10):
        colored_unclaimed[code] = "red"

    elif comparison <= timedelta(days=30):
        colored_unclaimed[code] = "yellow"

    else:
        colored_unclaimed[code] = "white"
    print(code, iso, comparison)

"""
for code, iso in data.unclaimed.items():
    listbox.insert(END, code)

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
    var_automation: BooleanVar,
    var_force: BooleanVar,
    scale: Scale,
    def_scale: Scale,
    open_val: list[int],
    Ef: StringVar,
    Ew: StringVar,
    Es: StringVar,
) -> Never:
    """
    Ef: Entry Fullscreen,
    Ew: ^^^^^ Windowed,
    Es: ^^^^^ Singular"""

    # get values
    data.confirmation = var_confirmation.get()
    data.open_dirname = var_dirname.get()
    data.automation = var_automation.get()
    data.force_automation = var_force.get()

    scale_int = scale.get()
    data.def_time = int(
        def_scale.get()
    )  # i have to reconvert to int so my type checker can stfu

    if scale_int in (0, 1, 2):
        data.pic_export = scale_int
    else:
        data.pic_export = 0
    # data.ss_dir is modified by itself

    data.fullscreen_ss = Ef.get()
    data.windowed_ss = Ew.get()
    data.single_ss = Es.get()

    # dump settings
    with open(file_settings, "w", encoding="utf_8") as file:
        dump(data.get_dict(), fp=file)
    # if logdata was set to be reset do not write to it
    if was_deleted is True:
        exit()

    # ------------------------------------------------------------
    # logdata block
    # ------------------------------------------------------------

    with open(file_logdata, "r", encoding="utf-8") as file:
        contents = file.readlines()

    _ = close_clock = f"{datetime.now():%X}"
    __ = _.split(":")
    close_val: list[int] = []
    for i in __:
        close_val.append(int(i))

    try:
        dummy = int(contents[0])
    except ValueError:
        dummy = 0

    dummy += 1
    contents[0] = str(dummy) + "\n"

    SET_TO: str = f"""

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
modify.py instance at {str(datetime.now()).split(".")[0].split(" ")[0]} {open_clock}, instance number {dummy}:     

Saving:
confirmation set to {data.confirmation}
picture save set to {data.pic_export}
ssdir set to {data.ss_dir}

modify.py ran at {open_clock}
killed at {close_clock}
total time spent in modify.py: {c_sub_dt(list1=open_val, list2=close_val)}
"""
    contents.append(SET_TO)
    with open(file_logdata, "w", encoding="utf-8") as file:
        file.writelines(contents)
    exit()


window.protocol(
    "WM_DELETE_WINDOW",  # WINDOW MANAGER DELETE WINDOW
    lambda data=data: Save(
        data,
        var_confirmation,
        var_dirname,
        var_automation,
        var_force,
        pic_scale,
        scl_def_automation,
        open_val,
        windowed,
        fullscreen,
        single,
    ),
)

window.mainloop()
