import re
from typing import *


class Censorship:
    def __init__(self, content: Union[Any, str, None] = None) -> None:
        self.content: str = content

    def update_content(self, content: Any):
        self.content = content

    def censor(self):
        censored = ["fuck", "shit", "lmao", "lmfao", "porn", "sex", "cock", "ball"]
        for censor in censored:
            if censor in self.content:
                lenned = len(censor)
                hashes = "#" * lenned
                self.content = self.content.replace(censor, hashes)
        self.content = re.sub(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "[url omitted]",
            self.content,
        )
        return self.content
