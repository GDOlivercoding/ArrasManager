from init import (
    # modules
    mbox,
    fdialog,
    os,

    # functions
    move,
    dump,

    # variables
    file_logdata,
    file_settings,
    write,
    dir_arras,

)

# confirmation if ran accidentally
match_var = mbox.askyesnocancel(
    title="Are you sure?",
    message="Are you sure you want to run the main installation process?\nYes if you just downloaded this software,\nno to just repair the data files\nor cancel if its already been set up",
)

if match_var == False:
        # make logdata file

        with open(file_logdata, "w") as file:
            file.write("0")

        # make settings file
        with open(file_settings, "w", encoding="utf-8") as file:

            dump(obj=write, fp=file)

        mbox.showinfo(title="Success", message="Successfully repaired the data files!")
        exit()

elif match_var == None:
    exit()

# ask for directory of choice of where the directory should be made in
store = fdialog.askdirectory(
    title="Select directory to execute installation in, for example the Desktop directory"
)

# if the user decides to cancel the installation
if not store:
    mbox.showerror(
        title="Error", message="No directory selected, installation cancelled"
    )
    exit()

# create main Arras.io Saves directory
dir_saves = os.path.join(store, "Arras.io Saves")

os.mkdir(dir_saves)
os.chdir(dir_saves)

# create subdirectories
to_make = ["Normal", "Olddreads", "Arms Race", "Ended Runs", "Arras Python"]
for item in to_make:
    try:
        os.mkdir(item)
    except:
        ...

# move all sys files to the main directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys_files = ("modify.py", "arras.py", "installer.py", "init.py", "requirements.txt")
for file in sys_files:
    try:
        move(file, dir_saves)
    except:
        ...

# AppData dir and the files it stores
if not os.path.exists(dir_arras):
    os.mkdir(dir_arras)

# make logdata file
with open(file_logdata, "w") as file:
    file.write("0")

# make settings file
with open(file_settings, "w", encoding="utf-8") as file:
    dump(obj=write, fp=file)

# a good success message is needed for the user to understand that it has REALLY happened
mbox.showinfo(
    title="Success",
    message=f"Successfully set up the software! All python files have been moved to {os.path.join(dir_saves, "Arras Python")}",
)
# after pressing OK the program automatically crashes because there's no more code to execute
