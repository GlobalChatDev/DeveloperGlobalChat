from typing import Any, Optional

import re


class Censorship:
    def __init__(self, content: str) -> None:
        self.content: str = content

    def update_content(self, content: str) -> None:
        self.content = content

    def censor(self) -> str:
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
