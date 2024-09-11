from random import choices, sample, randint

from pygame_tool_kit.constants import EVENTS_MANAGER, DISPLAY

from pygame_tool_kit.scenes import Scene
from pygame_tool_kit.buttons import Button, Hover, command, scene_command
from pygame_tool_kit.sources import Image, Image_Collection, Text, Paragraph, Container
from frames import Message_Frame

from data_managers import TOPICS, CHARACTERS, DIFFICULTIES, QUESTIONS, BACKGROUNDS

class Game (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()

		self.health : int = 3
		self.max_streak : int = 0
		self.streak : int = 0
		self.score : int = 0

		self.topic : int = 0
		self.character : int = 0
		self.difficulty : int = 0

		self.asking : bool = False

		self.answered_questions : tuple[dict[str, int]] = tuple ( {"answered" : 0, "correctly_answered" : 0} for topic in TOPICS )

		self.add_sprites (Image ("game/game"))

		self.health_container : Container = Container (pos = (self.main_container.pos[0] - 155, self.main_container.pos[1] - 98))
		self.update_health (0)

		streak_container : Container = Container (pos = (self.main_container.pos[0] - 180, self.main_container.pos[1] - 98))

		self.streak_image_collection : Image_Collection = Image_Collection ("backgrounds/streak", (16, 12))
		streak_container.add_sprites (self.streak_image_collection)

		self.streak_text : Text = Text (self.streak)
		streak_container.add_sprites (self.streak_text)

		self.add_containers (streak_container)

		self.score_text : Text = Text (self.score, pos = (-142, -87), align = "right")
		self.add_sprites (self.score_text)

		self.topic_image_collection : Image_Collection = Image_Collection ("backgrounds/topic_face", (12, 12), pos = (-182, 80))
		self.character_name_image_collection : Image_Collection = Image_Collection ("backgrounds/character_name", (56, 16), pos = (-162, 98))
		self.character_name_text : Paragraph = Paragraph ("", 55, pos = (-162, 98), align = "center")

		self.difficulty_image_collection : Image_Collection = Image_Collection ("backgrounds/difficulty_name", (38, 12), pos = (-153, 80))
		self.difficulty_text : Text = Text ("", pos = (-153, 80))

		self.add_sprites (self.topic_image_collection, self.character_name_image_collection, self.character_name_text, self.difficulty_image_collection, self.difficulty_text)

		self.probability_texts : tuple[Text] = tuple (
			Text (f"{CHARACTERS[self.topic][self.character].probabilities[i]}%") for i in range (len (TOPICS))
		)
		self.hit_texts : tuple[Text] = tuple (
			Text (f"{self.answered_questions[i]['correctly_answered']}/{self.answered_questions[i]['answered']}", pos = (33, -2), align = "right") for i in range (len (TOPICS))
		)

		self.hovers : tuple[Hover] = tuple (
			Hover (
				Image ("hovers/topics/hover", size = (20, 16), frame = (i, 0), pos = (-120 + (20 * i), 102)),
				Image ("hovers/topics/dropdown", size = (72, 24), frame = (i, 0), pos = (-96 + (20 * i), 82)),
				self.main_container,
				hover_text = self.probability_texts[i],
				dropdown_texts = (
					Text ("Aciertos", pos = (-32, -2), align = "left"),
					self.hit_texts[i]
				)
			) for i in range (len (TOPICS))
		)

		self.game_topic : int = 0
		self.game_topic_image_collection : Image_Collection = Image_Collection ("backgrounds/topic", (284, 128), pos = (16, -10))

		self.game_topic_text : Text = Text ("", pos = (-58, -66), size = 12)
		self.game_question_paragraph : Paragraph = Paragraph ("", 266, pos = (16, -36), align = "center")

		self.add_sprites (self.game_topic_image_collection, self.game_topic_text, self.game_question_paragraph)

		self.answer_buttons : tuple[Button] = (
			Button (
				Image_Collection ("buttons/answer", (136, 28), pos = (-54, 6)),
				self.main_container
			),
			Button (
				Image_Collection ("buttons/answer", (136, 28), pos = (86, 6)),
				self.main_container
			),
			Button (
				Image_Collection ("buttons/answer", (136, 28), pos = (-54, 36)),
				self.main_container
			),
			Button (
				Image_Collection ("buttons/answer", (136, 28), pos = (86, 36)),
				self.main_container
			)
		)

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (158, -94)),
			commands = (scene_command ("overlay", "Pause_Menu"),),
			text = "Pausa"
		)

		self.next_button_container : Container = Container ()
		self.next_button : Button = Button (
			Image_Collection ("buttons/next", (52, 16), pos = (132, 62)),
			self.next_button_container,
			commands = (self.ask,),
			text = "Siguiente"
		)

		EVENTS_MANAGER.subscribe ("set_topic", self.set_topic)
		EVENTS_MANAGER.subscribe ("set_character", self.set_character)
		EVENTS_MANAGER.subscribe ("set_difficulty", self.set_difficulty)
		EVENTS_MANAGER.subscribe ("finish_game", self.finish_game)
		EVENTS_MANAGER.subscribe ("wait_next_question", self.process_answer_buttons)

	def update_health (self, health : int = 1) -> None:

		self.health : int = max (0, min (8, self.health + health))
		self.remove_containers (self.health_container)
		self.health_container.empty ()

		if (self.health == 1):
			self.health_container.add_sprites (*tuple ( Image ("game/health", size = (22, 8), pos = (22 * i, 0), frame = (0, 0)) for i in range (self.health)))

		elif (self.health < 4):
			self.health_container.add_sprites (*tuple ( Image ("game/health", size = (22, 8), pos = (22 * i, 0), frame = (0, 1)) for i in range (self.health)))

		elif (self.health < 7):
			self.health_container.add_sprites (*tuple ( Image ("game/health", size = (22, 8), pos = (22 * i, 0), frame = (0, 2)) for i in range (self.health)))

		elif (self.health < 9):
			self.health_container.add_sprites (*tuple ( Image ("game/health", size = (22, 8), pos = (22 * i, 0), frame = (0, 3)) for i in range (self.health)))

		self.add_containers (self.health_container)

	def reset_streak (self) -> None:

		if (self.streak > self.max_streak):
			self.max_streak : int = self.streak

		self.streak : int = 0
		self.streak_image_collection.set_image (0)
		self.streak_text.set_text (self.streak)

	def increase_streak (self) -> None:

		self.streak += 1
		self.streak_image_collection.set_image (min (self.streak // 10, 3))
		self.streak_text.set_text (self.streak)

	def increase_score (self, score : int = 1) -> None:

		self.score += score
		self.score_text.set_text (self.score)

	def finish_game (self) -> None:

		self.health : int = 3
		self.update_health (0)

		self.reset_streak ()

		self.score : int = 0
		self.increase_score (0)

		self.answered_questions : tuple[dict[str, int]] = tuple ( {"answered" : 0, "correctly_answered" : 0} for topic in TOPICS )
		for i in range (len (self.hit_texts)):
			self.hit_texts[i].set_text (f"{self.answered_questions[i]['correctly_answered']}/{self.answered_questions[i]['answered']}")
		
		for questions in QUESTIONS[self.difficulty]:
			for question in questions:
				question.answered : bool = False

		EVENTS_MANAGER.emit ("reset_selections")
		EVENTS_MANAGER.emit ("switch_back_commands", "Main_Menu")

	def set_topic (self, topic : int) -> None:

		self.topic : int = topic
		self.topic_image_collection.set_image (self.topic)
		self.character_name_image_collection.set_image (self.topic)

	def set_character (self, character : int) -> None:

		self.character : int = character
		self.character_name_text.set_text (CHARACTERS[self.topic][self.character].name)

		for i in range (len (self.probability_texts)):
			self.probability_texts[i].set_text (f"{CHARACTERS[self.topic][self.character].probabilities[i]}%")

	def set_difficulty (self, difficulty : int) -> None:

		self.difficulty : int = difficulty
		self.difficulty_image_collection.set_image (self.difficulty)
		self.difficulty_text.set_text (DIFFICULTIES[self.difficulty].name)

		self.ask ()

	def ask (self) -> None:

		if (self.health == 0):
			EVENTS_MANAGER.emit ("append_try", {"topic" : self.topic, "character" : self.character, "difficulty" : self.difficulty, "max_streak" : self.max_streak, "score" : self.score})
			EVENTS_MANAGER.emit ("lose_game", self.difficulty)
			EVENTS_MANAGER.emit ("overlay_scene", "Finish_Frame", lazy = True)

		if (sum (answered_question["answered"] for answered_question in self.answered_questions) < sum (len (questions) for questions in QUESTIONS[self.difficulty])):
			self.asking : bool = True

			available_topics : tuple[int] = tuple (i for i in range (len (TOPICS)) if any (not question.answered for question in QUESTIONS[self.difficulty][i]))

			probabilities : list[int] = [CHARACTERS[self.topic][self.character].probabilities[i] for i in available_topics]

			total_prob : float = sum (probabilities)
			if (total_prob < 100):
				prob_to_distribute : float = 100 - total_prob

				for i in range (len (probabilities)):
					probabilities[i] += prob_to_distribute / len (probabilities)

			probabilities_sum : int = sum (probabilities)
			normalized_probabilities : tuple[float] = tuple (probability / probabilities_sum for probability in probabilities)
			self.game_topic : int = choices (available_topics, normalized_probabilities)[0]

			unanswered_questions : tuple[int] = tuple (
				i for i, question in enumerate (QUESTIONS[self.difficulty][self.game_topic]) if (not question.answered)
			)
			question : int = unanswered_questions[randint (0, len (unanswered_questions) - 1)]

			QUESTIONS[self.difficulty][self.game_topic][question].answered : bool = True
			self.game_topic_image_collection.set_image (self.game_topic)
			self.game_topic_text.set_text (TOPICS[self.game_topic])
			self.game_question_paragraph.set_text (QUESTIONS[self.difficulty][self.game_topic][question].question)

			answers : tuple[int] = tuple (sample (range (4), 4))

			for i, answer_button in enumerate (self.answer_buttons):
				answer_button.set_text (QUESTIONS[self.difficulty][self.game_topic][question].answers[answers[i]])
				if (answers[i] == 0):
					answer_button.set_commands (self.guess)

				else:
					answer_button.set_commands (self.miss)

		else:
			EVENTS_MANAGER.emit ("append_try", {"topic" : self.topic, "character" : self.character, "difficulty" : self.difficulty, "max_streak" : self.max_streak, "score" : self.score})
			EVENTS_MANAGER.emit ("win_game", self.difficulty)
			EVENTS_MANAGER.emit ("overlay_scene", "Finish_Frame", lazy = True)

			if (self.difficulty < len (DIFFICULTIES) - 1):
				if (not DIFFICULTIES[self.difficulty + 1].unlocked):
					EVENTS_MANAGER.emit ("unlock_difficulty", self.difficulty + 1)
					EVENTS_MANAGER.emit (
						"print_scene",
						Message_Frame (
							Container (
								Image ("/messages/difficulty"),
								Image ("/backgrounds/difficulty_name", size = (38, 12), frame = (0, self.difficulty + 1)),
								Text ("¡Dificultad Desbloqueada!", pos = (0, -29)),
								Text (DIFFICULTIES[self.difficulty + 1].name)
							),
							button_image_collection = Image_Collection ("buttons/normal", (64, 24), pos = (0, 32))
						),
						lazy = True
					)

	def guess (self):

		self.answered_questions[self.game_topic]["answered"] += 1
		self.answered_questions[self.game_topic]["correctly_answered"] += 1

		self.hit_texts[self.game_topic].set_text (f"{self.answered_questions[self.game_topic]['correctly_answered']}/{self.answered_questions[self.game_topic]['answered']}")

		self.increase_streak ()

		if (self.streak % 5 == 0):
			self.update_health (1)

		self.increase_score (self.difficulty + 1)

		EVENTS_MANAGER.emit ("wait_next_question", lazy = True)
		if (self.answered_questions[self.game_topic]["correctly_answered"] == len (QUESTIONS[self.difficulty][self.game_topic])):
			if (len (CHARACTERS[self.game_topic]) - 1 >= self.difficulty):
				if (not CHARACTERS[self.game_topic][self.difficulty].unlocked):
					EVENTS_MANAGER.emit ("unlock_character", self.game_topic, self.difficulty)
					EVENTS_MANAGER.emit (
						"print_scene",
						Message_Frame (
							Container (
								Image ("/messages/character"),
								Image ("/backgrounds/topic_face", size = (12, 12), pos = (-34, 0), frame = (0, self.game_topic)),
								Image ("/backgrounds/character_name", size = (56, 16), pos = (16, 0), frame = (0, self.game_topic)),
								Paragraph ("¡Personaje Desbloqueado!", 106, pos = (0, -30), align = "center"),
								Paragraph (CHARACTERS[self.game_topic][self.difficulty].name, 54, pos = (16, 0), align = "center")
							),
							button_image_collection = Image_Collection ("buttons/normal", (64, 24), pos = (0, 32))
						),
						lazy = True
					)
					self.next_button.update ()

			if ((self.difficulty == len (DIFFICULTIES) - 1) and (self.topic == len (TOPICS))):
				if (not BACKGROUNDS[self.game_topic + 1]):
					EVENTS_MANAGER.emit ("unlock_background", self.game_topic + 1)
					EVENTS_MANAGER.emit (
						"print_scene",
						Message_Frame (
							Container (
								Image ("/messages/background"),
								Image ("/backgrounds/selection_window", size = (48, 28), pos = (0, 2), frame = (0, self.game_topic + 1)),
								Text ("¡Fondo Desbloqueado!", pos = (0, -29))
							),
							button_image_collection = Image_Collection ("buttons/normal", (64, 24), pos = (0, 32))
						),
						lazy = True
					)
					self.next_button.update ()

	def miss (self):

		self.answered_questions[self.game_topic]["answered"] += 1

		self.hit_texts[self.game_topic].set_text (f"{self.answered_questions[self.game_topic]['correctly_answered']}/{self.answered_questions[self.game_topic]['answered']}")

		self.reset_streak ()

		self.update_health (-1)

		EVENTS_MANAGER.emit ("wait_next_question", lazy = True)

	def process_answer_buttons (self) -> None:

		for answer_button in self.answer_buttons:
			if (answer_button.state == 2):
				answer_button.image_collection.set_image (4)
				break

		for answer_button in self.answer_buttons:
			if (self.guess in answer_button.commands):
				answer_button.image_collection.set_image (3)
				break
		
		self.asking : bool = False

	def update (self) -> None:

		super ().update ()

		if (self.asking):
			for answer_button in self.answer_buttons:
				answer_button.update ()

		else:
			self.next_button.update ()

		for hover in self.hovers:
			hover.update ()

	def draw (self) -> None:

		super ().draw ()

		if (not self.asking):
			self.next_button_container.draw (DISPLAY.surface)

		for hover in self.hovers:
			hover.draw ()
