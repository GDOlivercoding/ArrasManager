from init import (
    partial,
    os,
    fdialog,
    mbox,
    Path,
    dump,
    move,
    load,
    file_logdata,
    file_settings,
    dir_arras,
    write,
    gamemode,
)
import tkinter as tk
import ttkbootstrap as ttk


def full():
    store = fdialog.askdirectory(
        title="Select directory to execute installation in, for example the Desktop directory"
    )

    if not store:
        return
    if not store:
        return

    dir_saves = Path(store) / "Arras.io saves"

    dir_saves.mkdir()

    to_make = ["Normal", "Olddreads", "Arms Race", "Ended Runs", "Arras Python"]
    for item in to_make:
        (dir_saves / item).mkdir()

    for file in [f for f in Path(__file__).iterdir() if f.is_file()]:
        try:
            move(file, dir_saves)
        except FileExistsError:
            pass

    dir_arras.mkdir(exist_ok=True)

    with file_logdata.open("w") as file:
        file.write("0")

    with file_settings.open("w") as file:
        dump(obj=write, fp=file)

    mbox.showinfo(
        title="Success",
        message=f"Successfully set up the software! All python files have been moved to {os.path.join(dir_saves, "Arras Python")}",
    )


def repair_all():
    with file_logdata.open() as file:
        contents = file.readlines()

    try:
        int(contents[0])
    except IndexError:
        contents.append("0")
        with open(file_logdata, "w") as file:
            file.writelines(contents)

    with file_settings.open() as file:
        contents = load(fp=file)

    dictionary = {**write}

    try:
        dictionary["unclaimed"] = contents["unclaimed"]
    except KeyError:
        # if there are no unclaimed codes
        # we simply do nothing
        pass

    with file_settings.open("w") as file:
        dump(fp=file, obj=dictionary)


def tree():
    get_dir = fdialog.askdirectory(title="Directory to create the tree in")
    if not get_dir:
        return

    (dirpath := (Path.cwd() / "Arras.io saves")).mkdir(exist_ok=True)

    for dir in gamemode:
        (dirpath / dir).mkdir()

    mbox.showinfo("Success", "Successfully constructed the directory tree!")


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

full_installation = frame_button(text="full installation", command=full)
full_installation.pack(side="left")

repair_files = frame_button(text="repair data files", command=repair_all)
repair_files.pack(side="left", padx=10)

construct_tree = frame_button(text="construct dir tree", command=tree)
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
