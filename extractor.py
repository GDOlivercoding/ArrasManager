from tkinter import *  # type: ignore[wildcard]
from tkinter import ttk, messagebox as mbox

from init import GamemodeType, RegionType, format_score, regions
from typing import Literal


def match_region(server: str) -> RegionType:
    region = "Unknown"

    for k, v in regions.items():
        if server[1] == k:
            region = v

    return region  # type: ignore


def match_gamemode(server_name: str) -> GamemodeType:
    """return the gamemode based on its name"""

    gamemode = "Normal"

    for name, mode in {"old": "Olddreads", "forge": "Newdreads"}.items():
        if name in server_name:
            gamemode = mode

    for tag, mode in {"g": "Grownth", "a": "Arms Race"}.items():
        if server_name.startswith(tag):
            gamemode = mode

    # can only return the given Literal yet still screams
    return gamemode  # type: ignore[ReturnType]


def input_code():
    global text, entry
    code = text.get()
    if not code:
        return
    elif len(code.split(":")) < 10:
        mbox.showerror("Invalid code", "Input code is invalid")
    else:
        entry.delete(1, END)
        data = get_analytics(code)
        display_widget(data)


DataTupleType = tuple[
    str,
    str,  # code, server tag
    Literal["Normal", "Olddreads", "Newdreads", "Grownth", "Arms Race"],  # gamemode
    str,
    str,
    str,
    str,  # region, class, build, score
    float,
    int,  # runtime in hours, minutes
    int,
    int,
    int,  # kills, assists, boss kills/assists
    float,
    float,
    float,  # score per kill, kill per minute, kill per assist
]


def get_analytics(code: str) -> DataTupleType:
    parts = code.split(":")
    # sample code
    # (6f0cb12f:#eo:e5forge:Arbitrator-Astronomic:0/2/6/10/10/10/10/12/0/0:7148698:20683:71:13:4:5017:62:1710762682:JDo5u44GPYop3lwZ)
    (
        _,
        server_tag,
        server_name,
        tank_class,
        build,
        score,
        runtime,
        kills,
        assists,
        boss_kills,
        *__,
    ) = parts
    del _, __

    kills, assists, boss_kills = int(kills), int(assists), int(boss_kills)

    gamemode = match_gamemode(server_name)
    region = match_region(server_tag)

    i_score = int(score)
    score = format_score(i_score)

    runtime = int(runtime)
    runtime_mins = runtime // 60
    runtime_hours = float(f"{runtime / 3600:.1f}")

    # kills
    kills_score = i_score // kills  # amount of score between each kill
    kills_mins = runtime_mins / kills  # average amount of time takes to get a kill
    kills_assists = kills / assists  # amount of kills per assist

    # regular information
    return (
        code,
        server_tag,
        gamemode,  # server_name readable
        region,
        tank_class,
        build,
        score,
        runtime_hours,
        runtime_mins,
        kills,
        assists,
        boss_kills,
        kills_score,
        kills_mins,
        kills_assists,
    )


def display_widget(data: DataTupleType) -> None:
    wdg = Tk()
    wdg.title(f"{data[4]}: {data[6]}")
    wdg.geometry("1000x400")
    wdg.resizable(False, False)

    scroll = Scrollbar(wdg)
    scroll.pack(side=RIGHT, fill=Y)

    main_text = Text(wdg, yscrollcommand=scroll.set)

    for item, line in zip(
        [
            "code",
            "server tag",
            "gamemode",
            "region",
            "class",
            "build",
            "score",
            "runtime in hours",
            "runtime in minutes",
            "kills",
            "assists",
            "boss kills/assists",
            "kill per score",
            "kill per minute",
            "kills per assist",
        ],
        data,
    ):
        main_text.insert(END, f"{item}: {line}\n")

    main_text.config(state=DISABLED)
    main_text.pack(anchor="nw", expand=True, fill=BOTH)

    scroll.config(command=main_text.yview)


wind = Tk()
wind.title("Extract code data - Independant app")
wind.geometry("600x400")
wind.resizable(*(False, False))

header = ttk.Label(
    wind, text="Extract various data from a code", font=("great vibes", 20)
)
header.pack(anchor="center")

frame = ttk.Frame(wind)
frame.pack(anchor="center")

entry = Entry(frame, textvariable=(text := StringVar()), font=("great vibes", 20))
entry.pack(side="left")

button = Button(
    frame, text="Create Widget", font=("great vibes", 20), command=input_code
)
button.pack(side="left", pady=120)

wind.tk.mainloop()
