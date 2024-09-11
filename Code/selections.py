from pygame_tool_kit.constants import EVENTS_MANAGER, DISPLAY
from pygame_tool_kit.config import RESOLUTION_CENTER

from pygame_tool_kit.scenes import Scene
from pygame_tool_kit.buttons import Selection_Button, command, scene_command
from pygame_tool_kit.sources import Image, Image_Collection, Text, Paragraph, Container

from data_managers import TOPICS, CHARACTERS, DIFFICULTIES

class Character_Selection (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()
		
		self.add_containers (
			Container (Image ("/selections/character", pos = (1, -9)), Text ("AREA", pos = (-140, -72), size = 12)),
			Container (*tuple ( Text (topic, pos = (-95 + (98 * (i // 6)), 19 + (10 * (i - 6 * (i // 6)))), align = "left") for i, topic in enumerate (TOPICS) ))
		)

		self.topic_selection : int = 12
		self.character_selection : int = 0

		self.topic_selection_buttons : tuple[Selection_Button] = tuple ( 
		[
			*tuple (
				Selection_Button (
					Image_Collection (
						"buttons/topic",
						(20, 20),
						pos = (RESOLUTION_CENTER[0] - 162 + (22 * (i - 3 * (i // 3))), RESOLUTION_CENTER[1] - 48 - (22 * - (i // 3))),
						frame = i
					),
					self.main_container,
					selection = i,
					unlock = any (character.unlocked for character in CHARACTERS[i]),
					lock_image = "topic"
				) for i in range (len (TOPICS))
			),
			Selection_Button (
				Image_Collection (
					"buttons/topic",
					(20, 20),
					pos = (RESOLUTION_CENTER[0] - 140, RESOLUTION_CENTER[1] + 40),
					frame = 12
				),
				self.main_container,
				selection = 12
				)
			]
		)

		self.character_selection_containers : tuple[Container] = tuple ( Container () for i in range (len (CHARACTERS)) )

		self.character_selection_buttons : tuple[tuple[Selection_Button]] = tuple (
			tuple (
				Selection_Button (
					Image_Collection (
						"buttons/character",
						(64, 24),
						pos = (RESOLUTION_CENTER[0] + 142, RESOLUTION_CENTER[1] - 52 + (26 * j)),
						frame = i
					),
					self.character_selection_containers[i],
					selection = j,
					text = CHARACTERS[i][j].name,
					unlock = CHARACTERS[i][j].unlocked,
					lock_image = "character"
				) for j in range (len (CHARACTERS[i]))
			) for i in range (len (CHARACTERS))
		)

		self.topic_name_image_collection : Image_Collection = Image_Collection ("/backgrounds/topic_name", (198, 40), pos = (1, -76))
		self.topic_name_image_collection.set_image (self.topic_selection)
		self.topic_text : Text =  Text ("Normal", pos = (142, -78))
		self.add_sprites (self.topic_name_image_collection, self.topic_text)

		self.elements : tuple[tuple[Character_Container]] = tuple (
			tuple (
				Character_Container (i, j) for j in range (len (CHARACTERS[i]))
			) for i in range (len (CHARACTERS))
		)

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 94)),
			commands = [scene_command ("switch", "Main_Menu")],
			text = "Volver"
		)

		EVENTS_MANAGER.subscribe ("reset_selections", self.reset_selection)
		EVENTS_MANAGER.subscribe ("unlock_character", self.unlock_character)

	def unlock_character (self, topic : int, character : int) -> None:

		self.character_selection_buttons[topic][character].unlock ()
		if (hasattr (self.topic_selection_buttons[topic], "mask")):
			self.topic_selection_buttons[topic].unlock ()

	def update (self) -> None:
				
		super ().update ()

		for topic_selection_button in self.topic_selection_buttons:
			if (topic_selection_button.update (self.topic_selection)):
				if (self.topic_selection != topic_selection_button.selection):
					self.topic_selection : int = topic_selection_button.selection
					for i in range (len (CHARACTERS[self.topic_selection])):
						if (CHARACTERS[self.topic_selection][i].unlocked):
							self.character_selection : int = i
							break

					self.topic_name_image_collection.set_image (self.topic_selection)
					self.topic_text.set_text ("Normal" if (self.topic_selection == 12) else TOPICS[self.topic_selection])

		for character_selection_button in self.character_selection_buttons[self.topic_selection]:
			if (character_selection_button.update (self.character_selection)):
				if (self.character_selection == character_selection_button.selection):
					EVENTS_MANAGER.emit ("switch_scene", "Difficulty_Selection", lazy = True)
					EVENTS_MANAGER.emit ("set_topic", self.topic_selection)
					EVENTS_MANAGER.emit ("set_character", self.character_selection)

				else:
					self.character_selection : int = character_selection_button.selection

	def reset_selection (self) -> None:

		self.topic_selection : int = 12
		self.topic_name_image_collection.set_image (self.topic_selection)
		self.topic_text.set_text ("Normal")
		self.character_selection : int = 0
		self.update ()

	def draw (self) -> None:

		super ().draw ()
		self.character_selection_containers[self.topic_selection].draw (DISPLAY.surface)
		self.elements[self.topic_selection][self.character_selection].draw (DISPLAY.surface)

class Character_Container (Container):

	def __init__ (self, topic : int = 0, character : int = 0) -> None:

		super ().__init__ (
			Paragraph (CHARACTERS[topic][character].name, 136, pos = (-1, -76), align = "center", size = 12),
			Paragraph (CHARACTERS[topic][character].description, 196, pos = (-97, -53))
		)
		
		self.add_sprites (*tuple ( Text (f"{CHARACTERS[topic][character].probabilities[i]}%", pos = (98 * (i // 6), 19 + (10 * (i - 6 * (i // 6)))), align = "right") for i in range (len (TOPICS))))

class Difficulty_Selection (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()

		self.add_containers (
			Container (Image ("/selections/difficulty"), Text ("DIFICULTADES", pos = (-103, 27)))
		)

		self.difficulty_selection : int = 0
		self.difficulty_selection_buttons : tuple[Selection_Button] = tuple (
			Selection_Button (
				Image_Collection (
					"buttons/difficulty",
					(48, 20),
					pos = (RESOLUTION_CENTER[0] - 100 + (50 * i), RESOLUTION_CENTER[1] + 47),
					frame = i
				),
				self.main_container,
				selection = i,
				text = DIFFICULTIES[i].name,
				unlock = DIFFICULTIES[i].unlocked,
				lock_image = "difficulty"
			) for i in range (len (DIFFICULTIES))
		)

		self.elements : tuple[Difficulty_Container] = tuple ( Difficulty_Container (i) for i in range (len (DIFFICULTIES)) )

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 77)),
			commands = [scene_command ("switch", "Character_Selection")],
			text = "Volver"
		)

		EVENTS_MANAGER.subscribe ("reset_selections", self.reset_selection)
		EVENTS_MANAGER.subscribe ("unlock_difficulty", self.unlock_difficulty)

	def unlock_difficulty (self, difficulty : int) -> None:

		self.difficulty_selection_buttons[difficulty].unlock ()

	def update (self) -> None:
					
		super ().update ()

		for difficulty_selection_button in self.difficulty_selection_buttons:
			if (difficulty_selection_button.update (self.difficulty_selection)):
				if (self.difficulty_selection == difficulty_selection_button.selection):
					EVENTS_MANAGER.emit ("switch_scene", "Game", lazy = True)
					EVENTS_MANAGER.emit ("set_difficulty", self.difficulty_selection)
					EVENTS_MANAGER.emit ("switch_back_commands", "Pause_Menu")

				else:
					self.difficulty_selection : int = difficulty_selection_button.selection

	def reset_selection (self) -> None:

		self.difficulty_selection : int = 0
		self.update ()

	def draw (self) -> None:

		super ().draw ()
		self.elements[self.difficulty_selection].draw (DISPLAY.surface)

class Difficulty_Container (Container):

	def __init__ (self, number : int = 0) -> None:

		super ().__init__ (
			Image ("/backgrounds/difficulty", pos = (0, -23), size = (260, 72), frame = (0, number)),
			Paragraph (DIFFICULTIES[number].description, 255, pos = (-129, -58))
		)
