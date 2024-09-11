from menus import Main_Menu, Options_Menu, Background_Menu, Exit_Menu, Pause_Menu, Back_Menu
from frames import Ranking_Frame, Credit_Frame, Help_Frame, Finish_Frame
from selections import Character_Selection, Difficulty_Selection
from main_game import Game
from backgrounds import Scrolling_Background

from pygame_tool_kit.kernel import Kernel

if (__name__ == "__main__"):
	Kernel (
		Main_Menu,
		Ranking_Frame,
		Options_Menu,
		Background_Menu,
		Help_Frame,
		Credit_Frame,
		Exit_Menu,
		Character_Selection,
		Difficulty_Selection,
		Game,
		Finish_Frame,
		Pause_Menu,
		Back_Menu,
		background = Scrolling_Background
	)

# Terminar las preguntas de Entretenimiento.

# Command to create excutable file
# pyinstaller --name "Gambo 2" --icon "Assets/GUI/icon.ico" --onefile --add-data "Assets:Assets" --add-data "Storage:Storage" --add-data "game_config.json:." --hidden-import="pygame_tool_kit" "Code/main.py"
