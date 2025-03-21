from nicegui import ui

class StatusIcon:
	def __init__(self, txt="", icon="sym_o_undo", color="purple-500", classes=""):
		self.visible = False
		with ui.icon(icon).classes(f'text-{color} {classes} z-50 text-2xl transition-opacity duration-500 opacity-0 pointer-events-none hidden') as icon_element:
			ui.tooltip(txt).classes(f'text-base border-{color} border').props('transition-show="fade" transition-hide="fade" transition-duration="800"')
		self.icon = icon_element
		
	def show(self):
		"""Fade in and enable tooltip."""
		if not self.visible:
			self.icon.classes(remove='hidden opacity-0 pointer-events-none')
			self.icon.classes(add='opacity-100')
			self.visible = True

	def hide(self):
		"""Fade out and disable tooltip."""
		if self.visible:
			self.icon.classes(remove='opacity-100')
			self.icon.classes(add='opacity-0 pointer-events-none')
			# Delay adding 'hidden' until after transition ends
			ui.timer(0.5, lambda: self.icon.classes(add='hidden'), once=True)
			self.visible = False