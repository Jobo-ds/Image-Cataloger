from nicegui import ui

class PremadeSpinner:
	def __init__(self, containers, size="xl", classes=""):
		self.spinners = []
		for container in containers:
			with container:
				spinner = ui.spinner(size=size).classes(f'{classes} hidden z-50')
				self.spinners.append(spinner)

	def show(self):
		"""Show the spinner."""
		for spinner in self.spinners:
			spinner.classes(remove='hidden')

	def hide(self):
		"""Hide the spinner."""
		for spinner in self.spinners:
			spinner.classes(add='hidden')