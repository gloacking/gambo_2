from pygame_tool_kit.constants import EVENTS_MANAGER, DISPLAY
from pygame_tool_kit.config import RESOLUTION_CENTER, RESOLUTION_SURFACE

from pygame_tool_kit.scenes import Scene
from pygame_tool_kit.buttons import Button, scene_command, command
from pygame_tool_kit.sources import Image, Image_Collection, Text, Container

from data_managers import BACKGROUNDS, CONFIGURATION

class Menu (Scene):

	def __init__ (self, title : str, buttons : tuple[tuple[str, str]] = ()) -> None:

		super ().__init__ ()

		self.add_sprites (Image ("/menus/normal"), Image ("/menus/title", pos = (0, -90)), Text (title, pos = (0, -54), size = 12))

		for i, button in enumerate (buttons):
			self.add_button (
				Image_Collection ("buttons/normal", (64, 24), pos = (0, (-25 + (24 * i)))),
				commands = (scene_command ("switch", button[0]),),
				text = button[1]
			)

class Main_Menu (Menu):

	def __init__ (self) -> None:

		super ().__init__ (
			"Menu",
			buttons = (
				("Character_Selection", "Jugar"),
				("Ranking_Frame", "Ranking"),
				("Options_Menu", "Opciones"),
				("Exit_Menu", "Salir")
			)
		)

class Options_Menu (Menu):

	def __init__ (self) -> None:

		super ().__init__ (
			"Opciones",
			buttons = (
				("Background_Menu", "Fondos"),
				("Help_Frame", "Ayudas"),
				("Credit_Frame", "Creditos")
			)
		)

		self.back_button : Button = Button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 47)),
			self.main_container,
			commands = (scene_command ("switch", "Main_Menu"),),
			text = "Volver"
		)
		self.buttons.append (self.back_button)

		EVENTS_MANAGER.subscribe ("switch_back_commands", lambda back : self.back_button.set_commands (scene_command ("switch", back)))


class Background_Menu (Scene):

	def __init__ (self) -> None:

		super ().__init__ ()

		self.selection : int = CONFIGURATION["selected_background"]
		self.background_image_collection : Image_Collection = Image_Collection ("backgrounds/selection_window", (48, 28))
		self.background_image_collection.set_image (self.selection)

		self.add_sprites (Image ("/menus/background"), Image ("/menus/title", pos = (0, -90)), Text ("Fondos", pos = (0, -54), size = 12), self.background_image_collection)

		self.lock_container : Container = Container ()
		self.lock_container.add_sprites (Image ("buttons/locks/background"))
		self.locked : bool = False

		self.add_button (
			Image_Collection ("buttons/left_arrow", (20, 36), pos = (-38, 0)),
			commands = (self.move_left_background,)
		)
		self.add_button (
			Image_Collection ("buttons/right_arrow", (20, 36), pos = (38, 0)),
			commands = (self.move_right_background,)
		)

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 47)),
			commands = (scene_command ("switch", "Options_Menu"), lambda : CONFIGURATION.save ()),
			text = "Volver"
		)

	def move_left_background (self) -> None:

		self.selection : int = self.selection - 1 if (self.selection > 0) else len (BACKGROUNDS) - 1
		self.background_image_collection.set_image (self.selection)
		if (BACKGROUNDS[self.selection]):
			EVENTS_MANAGER.emit ("change_background", self.selection)
			CONFIGURATION["selected_background"] : int = self.selection
			self.locked = False
		
		else:
			self.locked = True

	def move_right_background (self) -> None:

		self.selection : int = self.selection + 1 if (self.selection < len (BACKGROUNDS) - 1) else 0
		self.background_image_collection.set_image (self.selection)
		if (BACKGROUNDS[self.selection]):
			EVENTS_MANAGER.emit ("change_background", self.selection)
			CONFIGURATION["selected_background"] : int = self.selection
			self.locked = False
		
		else:
			self.locked = True

	def draw (self) -> None:

		super ().draw ()
		if (self.locked):
			self.lock_container.draw (DISPLAY.surface)

class Pause_Menu (Menu):

	def __init__ (self) -> None:

		super ().__init__ ("Pausa")

		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, -25)),
			commands = (scene_command ("remove"),),
			text = "Continuar"
		)
		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, -1)),
			commands = (scene_command ("switch", "Ranking_Frame"),),
			text = "Ranking"
		)
		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 23)),
			commands = (scene_command ("switch", "Options_Menu"),),
			text = "Opciones"
		)
		self.add_button (
			Image_Collection ("buttons/normal", (64, 24), pos = (0, 47)),
			commands = (scene_command ("switch", "Back_Menu"),),
			text = "Salir"
		)

class Boolean_Menu (Scene):

	def __init__ (self, message : str, yes : tuple[callable], no : tuple[callable], pos : tuple[int] = (RESOLUTION_CENTER[0], (RESOLUTION_SURFACE[1] // 3))) -> None:

		super ().__init__ (pos = pos)

		self.add_sprites (Image ("/menus/boolean"), Text (message))

		self.add_button (
			Image_Collection ("buttons/yes", (36, 20), pos = (-40, 22)),
			commands = yes,
			text = "Si"
		)
		self.add_button (
			Image_Collection ("buttons/no", (36, 20), pos = (40, 22)),
			commands = no,
			text = "No"
		)

class Exit_Menu (Boolean_Menu):

	def __init__ (self) -> None:

		super ().__init__ ("¿Desea abandonar el juego?", (scene_command ("remove"),), (scene_command ("switch", "Main_Menu"),))

class Back_Menu (Boolean_Menu):

	def __init__ (self) -> None:

		super ().__init__ ("¿Desea abandonar la partida?", (command (EVENTS_MANAGER.emit, "finish_game"), scene_command ("remove"), scene_command ("switch", "Main_Menu")), (scene_command ("switch", "Pause_Menu"),))
