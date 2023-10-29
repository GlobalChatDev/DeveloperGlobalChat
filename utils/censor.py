from __future__ import annotations

max_columns = 5  # Set this to the maximum number of columns you expect

char_mappings = {
    "a": ("a", "@", "*", "4", "#", "%", "A", "Á", "à", "â", "ä"),
    "b": ("b", "8", "6", "B"),
    "c": ("c", "k", "s", "2", "C", "ç", "ć"),
    "d": ("d", "0", "ð", "Đ", "D"),
    "e": ("e", "*", "3", "E", "É", "È", "Ê", "Ë", "è", "é", "ë"),
    "f": ("f", "ph", "F"),
    "g": ("g", "9", "6", "G"),
    "h": ("h", "4", "H", "H"),
    "i": ("i", "*", "l", "1", "!", "¡", "I", "Í", "ì", "î", "ï"),
    "j": ("j", "ʲ", "J"),
    "k": ("k", "c", "x", "K", "k"),
    "l": ("l", "1", "L", "£", "l"),
    "m": ("m", "M", "m"),
    "n": ("n", "η", "N", "ñ", "ń"),
    "o": ("o", "*", "0", "@", "O", "Ο", "Θ", "Ó", "ò", "ô", "ö", "ø"),
    "p": ("p", "P", "ρ", "Þ", "p"),
    "q": ("q", "9", "Q", "q"),
    "r": ("r", "R", "r"),
    "s": ("s", "$", "5", "S", "ş", "š", "ś"),
    "t": ("t", "7", "+", "T", "τ", "ț", "ť"),
    "u": ("u", "*", "v", "U", "υ", "µ", "Ù", "ú", "û", "ü", "ů"),
    "v": ("v", "*", "u", "V", "v"),
    "w": ("w", "vv", "W", "w"),
    "x": ("x", "k", "X", "x"),
    "y": ("y", "υ", "γ", "Y", "ÿ", "Ÿ", "ý"),
    "z": ("z", "2", "Z", "Ζ", "ż", "ź"),
}


def generate_variations(word: str) -> list[str]:
    variations = []
    for item, value in char_mappings.items():
        for char in value:
            if char != item:
                variation = word.replace(item, char)

                if variation == word:
                    continue

                variations.append(variation)

    return variations


class Censorship:
    def __init__(self, content: str | None = None) -> None:
        self.content: str | None = content

        self.data = []
        self.profanity = []

    def censor(self):
        with open("profanity.txt", "r") as file:
            for line in file:
                line = line.strip("\n")
                new_columns = [line] if " " in line else line.split()

                new_columns += generate_variations(line)

                new_columns += [""] * (max_columns - len(new_columns))

                self.data.append(new_columns)

        self.profanity.extend([element for row in self.data for element in row if element])

        censored_words = []

        for word in self.content.split():
            censored_word = word
            for profane_word in self.profanity:
                if profane_word in word:
                    censored_word = censored_word.replace(profane_word, r"\*" * len(profane_word))
            censored_words.append(censored_word)

        return " ".join(censored_words)
