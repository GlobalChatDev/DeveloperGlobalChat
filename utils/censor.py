from typing import *

class Censorship:
	def __init__(self, content: Union[Any, str, None] = None) -> None:
		self.content: Any = content

	def update_content(self, content: Any):
		self.content = content

	def censor(self):
		censored = ["fuck", "shit", "lmao", "lmfao", "porn", "sex", "cock", "ball"]
		for censor in censored:
			if censor in self.content:
				lenned = len(censor)
				hashes = ""
				for _ in range(lenned):
					hashes += "#"
				self.content = self.content.replace(censor, hashes)
		return self.content
