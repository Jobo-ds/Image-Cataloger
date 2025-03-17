from nicegui import ui

class ErrorDialog:
	"""
	A reusable error dialog for displaying errors with adaptive light/dark mode support.
	"""
	
	def __init__(self):
		with ui.dialog().props("persistent backdrop-filter='blur(8px)'") as self.dialog:
			with ui.column().classes("w-full max-w-2xl").style('''
				background-color: var(--bg-1);
				color: var(--nicegui-text);
				padding: 20px;
				border-radius: 10px;
			'''):
				ui.label("⚠️ Error").style('''
					font-size: 20px;
					font-weight: bold;
					color: var(--nicegui-error);
				''')
				ui.separator()
				self.error_message = ui.label().style('font-size: 16px; font-weight: bold;')
				self.error_advice = ui.label().style('font-size: 14px; color: var(--nicegui-text-light);')
				self.exception_message = ui.label().style('font-size: 12px; font-style: italic; color: var(--nicegui-text-dark);')
				
				with ui.row().style('margin-top: 15px; justify-content: flex-end;'):
					ui.button("Close", on_click=self.dialog.close)

	def show(self, message="", advice="", exception=""):
		"""
		Show the error dialog with dynamic content.
		"""
		self.error_message.set_text(message)
		self.error_advice.set_text(advice)
		self.exception_message.set_text(exception)
		self.dialog.open()

	def close(self):
		"""Close the error dialog."""
		self.dialog.close()
		self.error_message.set_text("Error writing error.")
		self.error_advice.set_text("Oh no.")
		self.exception_message.set_text("No exception.")		

	def get(self):
		"""Return the dialog instance."""
		return self.dialog
