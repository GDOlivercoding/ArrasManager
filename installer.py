from init import (
    partial, 
    os,
    fdialog, 
    mbox, 
    create_dict,
    dump, 
    move, 
    load,
    file_logdata,
    file_settings,
    base_dir,
    dir_arras,
    write,
    copy_dict
)
from os import (
    getcwd as cwd,
    chdir as cd
)
from pathlib import Path

import tkinter as tk
import ttkbootstrap as ttk

class InstallerFunctions: 

    @staticmethod
    def full():
        
        store = fdialog.askdirectory(
            title="Select directory to execute installation in, for example the Desktop directory"
        )

        if not store:
            return

        dir_saves = os.path.join(store, "Arras.io Saves")

        os.mkdir(dir_saves)
        os.chdir(dir_saves)

        to_make = ["Normal", "Olddreads", "Arms Race", "Ended Runs", "Arras Python"]
        for item in to_make:
            try:
                os.mkdir(item)
            except:
                ...

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        sys_files = ("modify.py", "arras.py", "installer.py", "init.py", "requirements.txt")
        for file in sys_files:
            try:
                move(file, dir_saves)
            except: ...

        if not os.path.exists(dir_arras):
            os.mkdir(dir_arras)

        with open(file_logdata, "w") as file:
            file.write("0")

        with open(file_settings, "w", encoding="utf-8") as file:
            dump(obj=write, fp=file)

        mbox.showinfo(
            title="Success",
            message=f"Successfully set up the software! All python files have been moved to {os.path.join(dir_saves, "Arras Python")}",
        )

    @staticmethod
    def repair_all():
        with open(file_settings, "r") as file:
            contents = file.readlines()

        try:
            int(contents[0])
        except ValueError:
            contents[0] = str(0)
            with open(file_logdata, "w") as file:
                file.writelines(contents)

        with open(file_settings, "r") as file:
            contents = load(fp=file)

        try:
            create_dict(contents)
        except: 
            
            dictionary = copy_dict(write)
            
            dictionary["unclaimed"] = contents["unclaimed"]

            with open(file_settings, "w") as file:
                dump(fp=file, obj=dictionary)

        mbox.showinfo(title="Success", message="Successfully repaired the files!")

    @staticmethod
    def tree():
        get_dir = fdialog.askdirectory(title="Directory to create the tree in")
        if not get_dir:
            return

        cur = Path.cwd()
        dirpath = cur / "Arras.io Saves"

        try:
            os.mkdir(dirpath)
        except: ...

        cd(dirpath)
        for dir in ["Normal", "Olddreads", "Arms Race", "Ended Runs", "Arras Python"]:
            os.mkdir(dir)

        mbox.showinfo("Success", "Successfully constructed the directory tree!")

funcs = InstallerFunctions()

font: dict = {"font": ("great vibes", 20)}

window = tk.Tk()
window.title("Arras installer")
window.geometry("700x600")
window.resizable(False, False)

top_header = ttk.Label(window, text="Common functions:", font=("great vibes", 30))
top_header.pack(anchor="center", pady=(0, 20))



top_frame = ttk.Frame(window)
top_frame.pack(anchor="center")
frame_button = partial(tk.Button, master=top_frame, font=("great vibes", 18))

full_installation = frame_button(text="full installation", command=funcs.full)
full_installation.pack(side="left")

repair_files = frame_button(text="repair data files", command=funcs.repair_all)
repair_files.pack(side="left", padx=10)

construct_tree = frame_button(text="construct dir tree", command=funcs.tree)
construct_tree.pack(side="left", padx=10)

tk.Label(window, text="More options", **font).pack(pady=(300, 0))

bottom_frame1 = ttk.Frame(window)
bottom_frame1.pack(anchor="center", pady=20)

packer = {"side": "left", "padx": 10}

bottom_button = partial(tk.Button, master=bottom_frame1, font=("great vibes", 18))

clean_logger = bottom_button(text="clean logger")
clean_logger.pack(**packer)

clean_settings = bottom_button(text="clean settings")
clean_settings.pack(**packer)

full_reset = bottom_button(text="fully reset settings")
full_reset.pack(**packer)

window.tk.mainloop()