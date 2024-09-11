from pygame_tool_kit.constants import EVENTS_MANAGER, DISPLAY

from pygame_tool_kit.scenes import Scene
from pygame_tool_kit.buttons import Button, scene_command, command
from pygame_tool_kit.sources import Image, Image_Collection, Text, Paragraph, Container

from data_managers import CHARACTERS, DIFFICULTIES, NOTES, TRIES

class Message_Frame (Scene):

	def __init__ (self, *containers : tuple[Container], button_image_collection : Image_Collection = Image_Collection ("buttons/normal", (64, 24)), button_commands : tuple[callable] = (scene_command ("remove"),), button_text : str = "Aceptar") -> None:

		super ().__init__ ()

		for container in containers:
			self.main_container.add (container.sprites ())

		self.add_button (
			button_image_collection,
			commands = button_commands,
			text = button_text
		)

class Simple_Info_Frame (Scene):

	def __init__ (self, title : str, note : str, back_scene : str, note_align : str = "left") -> None:

		super ().__init__ ()

		self.add_sprites (Image ("frames/simple_info"), Image ("/menus/title", pos = (0, -90)), Text (title, pos = (0, -52), size = 12), Paragraph (NOTES[note], 154, pos = (-77, -35) if (note_align == "left") else (0, 0), align = note_align))

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 56)),
			commands = (scene_command ("switch", back_scene),),
			text = "Volver"
		)

class Advanced_Info_Frame (Scene):

	def __init__ (self, title : str, note : str, back_scene : str, note_align : str = "left") -> None:

		super ().__init__ ()

		self.note : str = note
		self.selection : int = 0
		self.note_paragraph : Paragraph = Paragraph (NOTES[self.note][self.selection], 154, pos = (-77, -35) if (note_align == "left") else (0, 0), align = note_align)

		self.add_sprites (Image ("frames/advanced_info"), Image ("/menus/title", pos = (0, -90)), Text (title, pos = (0, -53), size = 12), self.note_paragraph)

		self.add_button (
			Image_Collection ("buttons/left_arrow", (20, 36), pos = (-92, 0)),
			commands = (self.move_left_note,)
		)

		self.add_button (
			Image_Collection ("buttons/right_arrow", (20, 36), pos = (92, 0)),
			commands = (self.move_right_note,)
		)

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 56)),
			commands = (scene_command ("switch", back_scene),),
			text = "Volver"
		)

	def move_left_note (self) -> None:

		self.selection : int = self.selection - 1 if (self.selection > 0) else len (NOTES[self.note]) - 1
		self.note_paragraph.set_text (NOTES[self.note][self.selection])

	def move_right_note (self) -> None:

		self.selection : int = self.selection + 1 if (self.selection < len (NOTES[self.note]) - 1) else 0
		self.note_paragraph.set_text (NOTES[self.note][self.selection])

class Credit_Frame (Simple_Info_Frame):

	def __init__ (self) -> None:

		super ().__init__ (
			"Creditos",
			"credit",
			"Options_Menu",
			"center"
		)

class Help_Frame (Advanced_Info_Frame):

	def __init__ (self) -> None:

		super ().__init__ (
			"Ayudas",
			"help",
			"Options_Menu"
		)

class Ranking_Frame (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()

		self.selection : int = 0

		self.load_tries ()

		self.page_text : Text = Text (f"{self.selection + 1} / {len (self.page_containers) if (len (self.page_containers) != 0) else 1}", pos = (0, 58))

		self.add_sprites (Image ("frames/ranking"), Text ("Ranking", pos = (0, -83), size = 12), self.page_text)

		self.add_button (
			Image_Collection ("buttons/left_arrow", (20, 36), pos = (-55, 0)),
			commands = (self.move_left_note,)
		)

		self.add_button (
			Image_Collection ("buttons/right_arrow", (20, 36), pos = (55, 0)),
			commands = (self.move_right_note,)
		)

		self.back_button : Button = Button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 78)),
			self.main_container,
			commands = (scene_command ("switch", "Main_Menu"),),
			text = "Volver"
		)
		self.buttons.append (self.back_button)

		EVENTS_MANAGER.subscribe ("append_try", self.load_tries)
		EVENTS_MANAGER.subscribe ("switch_back_commands", lambda back : self.back_button.set_commands (scene_command ("switch", back)))
	
	def load_tries (self, *args : tuple) -> None:

		self.page_containers : tuple[Container] = tuple (Container () for i in range (max (0, 4 - (12 - len (TRIES)) // 3)))

		for i, container in enumerate (self.page_containers):
			container.add (Ranking_Try_Container (try_data, (self.main_container.pos[0], self.main_container.pos[1] - 49 + (j * 40))).sprites () for j, try_data in enumerate (TRIES[i * 3 : i * 3 + 3]))

	def move_left_note (self) -> None:

		self.selection : int = self.selection - 1 if (self.selection > 0) else len (self.page_containers) - 1
		self.page_text.set_text (f"{self.selection + 1} / {len (self.page_containers) if (len (self.page_containers) != 0) else 1}")

	def move_right_note (self) -> None:

		self.selection : int = self.selection + 1 if (self.selection < len (self.page_containers) - 1) else 0
		self.page_text.set_text (f"{self.selection + 1} / {len (self.page_containers) if (len (self.page_containers) != 0) else 1}")

	def draw (self) -> None:

		super ().draw ()
		if (len (self.page_containers) != 0):
			self.page_containers[self.selection].draw (DISPLAY.surface)

class Ranking_Try_Container (Container):

	def __init__ (self, try_data : dict, pos : tuple[int, int]) -> None:

		super ().__init__ (
			Image ("backgrounds/ranking_try"),
			Image ("backgrounds/topic_face", size = (12, 12), pos = (-29, -7), frame = (0, try_data["topic"])),
			Image ("backgrounds/character_name", size = (56, 16), pos = (9, -7), frame = (0, try_data["topic"])),
			Image ("backgrounds/difficulty_name", size = (38, 12), pos = (-18, 9), frame = (0, try_data["difficulty"])),
			Image ("backgrounds/streak", size = (16, 12), pos = (11, 9), frame = (0, min (try_data["max_streak"] // 10, 3))),
			Paragraph (CHARACTERS[try_data["topic"]][try_data["character"]].name, 54, pos = (9, -7), align = "center"),
			Text (DIFFICULTIES[try_data["difficulty"]].name, pos = (-18, 9)),
			Text (try_data["max_streak"], pos = (11, 9)),
			Text (try_data["score"], pos = (29, 9)),
			pos = pos
		)

class Finish_Frame (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()

		self.main_image_collection : Image_Collection = Image_Collection ("frames/finish", (240, 144))
		self.title_text : Text = Text ("", pos = (0, -43), size = 12)
		self.main_paragraph : Paragraph = Paragraph ("", 214, pos = (-107, -15))

		self.add_sprites (self.main_image_collection, self.title_text, self.main_paragraph)

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 56)),
			commands = (command (EVENTS_MANAGER.emit, "finish_game"), scene_command ("remove"), scene_command ("switch", "Main_Menu")),
			text = "Aceptar"
		)

		EVENTS_MANAGER.subscribe ("win_game", self.win_game)
		EVENTS_MANAGER.subscribe ("lose_game", self.lose_game)
	
	def win_game (self, difficulty : int) -> None:

		self.main_image_collection.set_image (0)
		self.title_text.set_text ("¡Has Ganado!")
		self.main_paragraph.set_text (NOTES["win"][difficulty])
		self.update ()

	def lose_game (self, difficulty : int) -> None:

		self.main_image_collection.set_image (1)
		self.title_text.set_text ("¡Has Perdido!")
		self.main_paragraph.set_text (NOTES["lose"][difficulty])
		self.update ()