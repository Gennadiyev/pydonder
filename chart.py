import enum
from dataclasses import dataclass
import rich.box as box
from rich.panel import Panel
from rich.text import Text
from rich import print
from rich.console import Group

class Difficulty(enum.Enum):
    """Difficulty of the song"""
    EASY = 1
    NORMAL = 2
    HARD = 3
    ONI = 4
    URA = 5

class Genre(enum.Enum):
    """Genre of the song"""
    POP = 1
    ANIME = 2
    KIDS = 3
    VOCALOID = 4
    GAME = 5
    ORIGINAL = 6
    VARIETY = 7
    CLASSICAL = 8


def _difficulty_to_symbol(difficulty: Difficulty) -> str:
    if difficulty == Difficulty.EASY:
        return "🌸"
    elif difficulty == Difficulty.NORMAL:
        return "🎍"
    elif difficulty == Difficulty.HARD:
        return "🌲"
    elif difficulty == Difficulty.ONI:
        return "💀"
    elif difficulty == Difficulty.URA:
        return "☢️"
    else:
        raise ValueError("Invalid difficulty: {}".format(difficulty))

def _genre_to_color(genre: Genre) -> str:
    if genre == Genre.POP:
        return "#21a1ba"
    elif genre == Genre.ANIME:
        return "#ff5386"
    elif genre == Genre.KIDS:
        return "#ff9900"
    elif genre == Genre.VOCALOID:
        return "#abb4bf"
    elif genre == Genre.GAME:
        return "#9d76bf"
    elif genre == Genre.ORIGINAL:
        return "#ff5b14"
    elif genre == Genre.VARIETY:
        return "#8fd41f"
    elif genre == Genre.CLASSICAL:
        return "#d1a314"
    else:
        raise ValueError("Invalid genre")

@dataclass
class Chart:
    id: int
    name: str
    level: Difficulty
    genre: Genre
    def __post_init__(self):
        if isinstance(self.level, int):
            self.level = Difficulty(self.level)
        if isinstance(self.genre, int):
            self.genre = Genre(self.genre)

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "genre": self.genre.value
        }

    def __repr__(self):
        return f"Chart(id={self.id}, name={self.name}, level={self.level}, genre={self.genre})"
    
    def display(self):
        print(Panel(
            Group(
                Text(),
                Text(_difficulty_to_symbol(self.level), end="  "),
                Text(self.name, "bold white"),
            ),
            style=_genre_to_color(self.genre),
            box=box.HEAVY_EDGE,
            title=self.genre.name,
            title_align="left",
            subtitle="#{}".format(self.id),
            subtitle_align="right",
            width=36,
            height=5
        ))
    
