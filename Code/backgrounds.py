from pygame_tool_kit.constants import EVENTS_MANAGER, DELTA_TIME, DISPLAY
from pygame_tool_kit.config import RESOLUTION_SURFACE

from pygame_tool_kit.sources import Image_Collection

from data_managers import CONFIGURATION

class Scrolling_Background ():

	def __init__ (self) -> None:

		self.image_collection : Image_Collection = Image_Collection ("backgrounds/window", (RESOLUTION_SURFACE[0], RESOLUTION_SURFACE[1] + 40))
		self.image_collection.set_image (CONFIGURATION["selected_background"])

		self.y : float = 0.0
		self.relative_y : int = 0

		EVENTS_MANAGER.subscribe ("change_background", self.change)

	def move (self) -> None:

		self.relative_y : int = round (self.y) % self.image_collection.rect.height
		self.y += (52 * DELTA_TIME.delta_time)

	def display (self) -> None:

		self.move ()
		if (self.y > self.image_collection.rect.height):
			self.y : float = 0.0

		DISPLAY.surface.blit (self.image_collection.image, (0, self.relative_y - self.image_collection.rect.height))
		DISPLAY.surface.blit (self.image_collection.image, (0, self.relative_y))

	def change (self, background : int) -> None:

		self.image_collection.set_image (background)