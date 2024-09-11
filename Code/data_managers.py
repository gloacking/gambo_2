from pygame_tool_kit.constants import EVENTS_MANAGER, STORAGE_MANAGER

class Character ():

	def __init__ (self, name : str, description : str, probabilities : tuple[int]) -> None:

		self.name : str = name
		self.description : str = description
		self.probabilities : tuple[int] = probabilities
		self.unlocked : bool = False

class Difficulty ():

	def __init__ (self, name : str, description : str) -> None:

		self.name : str = name
		self.description : str = description
		self.unlocked : bool = False

class Question ():

	def __init__ (self, question : str, answers : tuple[str]) -> None:

		self.question : str = question
		self.answers : tuple[str] = answers
		self.answered : bool = False

class Characters ():

	def __init__ (self) -> None:

		self.characters : tuple[tuple[Character]] = tuple (
			tuple (
				Character (character["name"], character["description"], tuple (character["probabilities"])) for character in characters
			) for characters in STORAGE_MANAGER.load ("characters")
		)

		for i, unlocked_characters in enumerate (STORAGE_MANAGER.load ("unlocked_characters", static = False)):
			for j, unlocked_character in enumerate (unlocked_characters):
				self.characters[i][j].unlocked : bool = unlocked_character

		EVENTS_MANAGER.subscribe ("unlock_character", self.unlock)

	def __getitem__ (self, index : int) -> tuple[Character]:

		return self.characters[index]

	def __len__ (self) -> int:

		return len (self.characters)

	def unlock (self, topic : int, character : int) -> None:

		self.characters[topic][character].unlocked : bool = True

		characters : dict = STORAGE_MANAGER.load ("unlocked_characters", static = False)
		characters[topic][character] : bool = True

		STORAGE_MANAGER.save ("unlocked_characters", characters)

class Difficulties ():

	def __init__ (self) -> None:

		self.difficulties : tuple[Difficulty] = tuple (
			Difficulty (difficulty["name"], difficulty["description"]) for difficulty in STORAGE_MANAGER.load ("difficulties")
		)

		for i, unlocked_difficulty in enumerate (STORAGE_MANAGER.load ("unlocked_difficulties", static = False)):
			self.difficulties[i].unlocked : bool = unlocked_difficulty

		EVENTS_MANAGER.subscribe ("unlock_difficulty", self.unlock)

	def __getitem__ (self, index : int) -> Difficulty:

		return self.difficulties[index]

	def __len__ (self) -> int:

		return len (self.difficulties)

	def unlock (self, difficulty : int) -> None:

		self.difficulties[difficulty].unlocked : bool = True

		difficulties : dict = STORAGE_MANAGER.load ("unlocked_difficulties", static = False)
		difficulties[difficulty] : bool = True

		STORAGE_MANAGER.save ("unlocked_difficulties", difficulties)

class Questions ():

	def __init__ (self) -> None:

		self.questions : tuple[tuple[tuple[Question]]] = tuple (
			tuple (
				tuple (
					Question (question["question"], tuple (question["answers"])) for question in topic_questions
				) for topic_questions in difficulty_questions
			) for difficulty_questions in STORAGE_MANAGER.load ("questions")
		)

	def __getitem__ (self, index : int) -> tuple[tuple[Question]]:

		return self.questions[index]

	def __len__ (self) -> int:

		return len (self.questions)

class Notes ():

	def __init__ (self) -> None:

		self.notes : dict[tuple[str]] = {name : (tuple (notes) if (type (notes) == list) else (notes)) for (name, notes) in STORAGE_MANAGER.load ("notes").items ()}

	def __getitem__ (self, index : str) -> any:

		return self.notes[index]

	def __len__ (self) -> int:

		return len (self.notes)

class Configuration ():

	def __init__ (self) -> None:

		self.configuration : int = STORAGE_MANAGER.load ("configuration", static = False)

	def __getitem__ (self, index : str) -> any:

		return self.configuration[index]

	def __setitem__ (self, index : str, value : any) -> None:

		self.configuration[index] : any = value

	def save (self) -> None:

		STORAGE_MANAGER.save ("configuration", self.configuration)

class Tries ():

	def __init__ (self) -> None:

		self.tries : int = STORAGE_MANAGER.load ("tries", static = False)

		EVENTS_MANAGER.subscribe ("append_try", self.append_try)

	def __getitem__ (self, index : int) -> dict:

		return self.tries[index]

	def __len__ (self) -> int:

		return len (self.tries)

	def append_try (self, try_data : dict) -> None:

		if (len (self.tries) < 12):
			self.tries.append (try_data)
			self.tries.sort (key = lambda try_data : try_data["score"], reverse = True)

		else:
			if (try_data["score"] > self.tries[-1]["score"]):
				self.tries.pop (-1)
				self.tries.append (try_data)
				self.tries.sort (key = lambda try_data : try_data["score"], reverse = True)

		self.save ()

	def save (self) -> None:

		STORAGE_MANAGER.save ("tries", self.tries)

TOPICS : tuple[str] = tuple (STORAGE_MANAGER.load ("topics"))
CHARACTERS : Characters = Characters ()
DIFFICULTIES : Difficulties = Difficulties ()
QUESTIONS : Questions = Questions ()
NOTES : Notes = Notes ()
CONFIGURATION : Configuration = Configuration ()
TRIES : Tries = Tries ()

BACKGROUNDS : tuple[str] = STORAGE_MANAGER.load ("unlocked_backgrounds", static = False)

def unlock_background (background : int) -> None:

	BACKGROUNDS[background] : bool = True

	backgrounds : dict = STORAGE_MANAGER.load ("unlocked_backgrounds", static = False)
	backgrounds[background] : bool = True

	STORAGE_MANAGER.save ("unlocked_backgrounds", backgrounds)

EVENTS_MANAGER.subscribe ("unlock_background", unlock_background)
