suffixes = {
    "s": "Siege",  # collides # TODO: Find out if siege has a team condition.
                   # Yes, and it is always 1tdm

    "b": "Soccer",  # collides # or football
    "d": "Domination",  # collides
    "g": "Grudgeball",  # collides
    "a": "Assault",  # collides           
    "m": "Mothership",  # collides
    "t": "Tag",
    "p": "Pandemic"  # collides
}

prefixes = {
    "m": "Maze",  # collides
    "o": "Open",
    "p": "Portal",  # collides # unused
    "a": "Arms_Race",  # collides
    "g": "Growth",  # collides
    "r": "Rock", # new

    # team types that dont require a team condition
    "f": "FFA",
    "s": "Squads",  # collides
    "d": "Duos",  # collides
    "c": "Clan_Wars",  
}  

all_keys = [*prefixes, *suffixes]

extra_word_count_map = {
    letter: i for i, letter in enumerate("abcd", start=10)
}

DEFAULT_MESSAGE = "Missing expected node."
class NodeExhauster[T]:
    def __init__(self, seq: list[T]) -> None:
        self.seq = seq
    
    def __call__(self, message: str = DEFAULT_MESSAGE) -> T:
        try:
            return self.seq.pop(0)
        except IndexError:
            raise ValueError(message) from None

def intable(s: str) -> bool:
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True
    
def tryint(s: str, exc: Exception) -> int:
    try:
        return int(s)
    except ValueError:
        raise exc from None

def parse(gamemode: str) -> list[str]:
    """
    Convert the mode's notation (usually shown bottom right of the screen) 
    to a list of strings of the parts, this is also the 3rd part of a save code,
    the output is **unformatted** and in **raw** form

    examples::

        def parse(gamemode: "e9tetromino4") -> ["tetromino", "4tdm"]: ...
        def parse(gamemode: "eaovergrowth") -> ["overgrowth"]: ...
        def parse(gamemode: "gaw39graveyards5magicm") -> ["Growth", "Arms Race", "graveyard", "magic", "Maze"]: ...

    raises:
    ValueError - incorrect notation syntax, may come in many forms
    """
    team_condition: bool = False
    nodes = list(gamemode)
    output = list[str]()
    new = NodeExhauster(nodes)

    while nodes:
        node = new()

        # Expecting a single custom word
        if node == "e":
            spaces_node = new("Expected letter count integer after \"e\".")

            if intable(spaces_node):
                space_count = int(spaces_node)
                if not (0 < space_count < 10):
                    raise ValueError(
                        f"The acceptable integer range for letter count is [1-9] not {space_count}."
                        " Use abcd, for 10, 11, 12, and 13 letters."
                    )
            else:
                if spaces_node not in extra_word_count_map:
                    raise ValueError(f"Unknown letter count symbol {spaces_node!r}.")
                space_count = extra_word_count_map[spaces_node]

            word = []

            temp = space_count

            while space_count:                  
                word.append(new(
                    f"Expected continuation of word," 
                    f"expected {temp} letters, got {space_count}."
                ))
                                    
                space_count -= 1

            output.append("".join(word))

        # Expecting multiple custom words
        elif node in ("w", "x"):
            part_count = tryint(
                new("Expected a part count integer after \"w\"."),
                ValueError("Part count is supposed to be an integer after \"w\".")
            )

            if part_count % 2 != 1:
                raise ValueError("Part count integer is supposed to be odd.")
            
            word_count = int((part_count + 1) / 2)

            letter_count = tryint(
                new(f"Expected a letter count integer after \"w{part_count}\"."),
                ValueError(f"Letter count is supposed to be an integer after \"w{part_count}\".")
            )

            while True:
                word = []
                temp = letter_count
                while letter_count:
                    word.append(
                        new(
                        f"Expected continuation of word," 
                        f"expected {temp} letters, got {letter_count}."
                    ))
                    letter_count -= 1

                output.append("".join(word))

                word_count -= 1
                if not word_count:
                    break

                sep = new(f"Expected seperator after {word!r}.")
                if sep != "s":
                    raise ValueError(f"Incorrect seperator character {sep!r} after {word!r}.")
                
                letter_node = new(f"Expected a letter count integer after \"s\".")
                if intable(letter_node):
                    letter_count = int(letter_node)
                    if not (0 < letter_count < 10):
                        raise ValueError(
                            f"The acceptable integer range for letter count is [1-9] not {letter_count}."
                            " Use abcd, for 10, 11, 12, and 13 letters."
                        )
                else:
                    if letter_node not in extra_word_count_map:
                        raise ValueError(f"Unknown letter count symbol {node!r}.")

                    letter_count = extra_word_count_map[letter_node]

        # TDM integer
        elif intable(node):
            if int(node) not in range(2, 5):
                raise ValueError(f"Team integer {node!r} is not in the TDM range of [2-4].")
            
            if team_condition:
                raise ValueError(f"Team condition found twice ({node=}).")
            
            output.append(node + "tdm")
            team_condition = True

        else:
            if node not in all_keys:
                raise ValueError(f"Unexpected token {node!r}.")  

            if team_condition:
                # 4tdm-
                if node not in suffixes:
                    # 4tdm-portal
                    raise ValueError(f"Cannot add prefix after team condition ({node=}).")
                
                # 4tdm-mothership
                output.append(suffixes[node])
                
            else:
                # arms race-
                if node not in prefixes:
                    # arms race-domination
                    raise ValueError(f"Cannot add suffix before team condition ({node=}).")
                
                # arms race-growth
                output.append(prefixes[node])   

    return output