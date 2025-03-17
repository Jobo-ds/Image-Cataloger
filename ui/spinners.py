from nicegui import ui

class spinner():
	"""Create a spinner to indicate loading."""
	def __init__(self):
		self.spinner = ui.spinner(size="xl").classes('absolute top-1/4 left-1/2 z-10')
		self.spinner.style('display: none;')

	def show(self):
		"""Show the spinner."""
		self.spinner.style('display: block;')

	def hide(self):
		"""Hide the spinner."""
		self.spinner.style('display: none;')

	def get(self):
		"""Return the spinner."""
		return self.spinner