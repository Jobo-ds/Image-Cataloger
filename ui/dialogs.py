from nicegui import ui

class ErrorDialog:
	"""
	A reusable error dialog for displaying errors with adaptive light/dark mode support.
	"""
	
	def __init__(self):
		with ui.dialog().props("persistent backdrop-filter='blur(8px)'") as self.dialog:
			with ui.column().classes("w-full max-w-2xl p-0 rounded bg-slate-700 gap-0"):
				with ui.row().classes("w-full items-center bg-red-500 border-b-slate-800").style("padding: 12px 15px;"):
					ui.icon("sym_o_error").style("font-size: 30px; color: white;")
					self.error_message = ui.label().style('font-size: 16px; font-weight: bold;')
					ui.space()
					ui.icon("sym_o_close").classes("relative right-0 top-0").on("click", self.close).style("font-size: 20px; cursor: pointer;")			

				with ui.row().classes("m-5"):
					with ui.tabs() as tabs:
						troubleshoot = ui.tab('Troubleshoot')
						exception = ui.tab('Error Log')

					with ui.tab_panels(tabs, value=troubleshoot).classes('w-full bg-transparent').props('transition-prev="fade" transition-next="fade"'):
						with ui.tab_panel(troubleshoot):
							self.troubleshoot_message = ui.label().style('font-size: 14px;')
						with ui.tab_panel(exception):
							self.exception_message = ui.label().style('font-size: 12px; font-style: italic;')
				with ui.row().classes("w-full justify-end").style("padding: 12px 15px;"):
					ui.button("Close", on_click=self.close)
							

	def show(self, error, troubleshoot="No troubleshooting available for this error.", exception="No exception available."):
		"""
		Show the error dialog with dynamic content.
		"""
		self.error_message.set_text(f"Error: {error}")
		self.troubleshoot_message.set_text(troubleshoot)
		self.exception_message.set_text(exception)
		self.dialog.open()

	def close(self):
		"""Close the error dialog."""
		self.dialog.close()
		self.error_message.set_text("Error writing error.")
		self.troubleshoot_message.set_text("Oh no.")
		self.exception_message.set_text("No exception.")

	def get(self):
		"""Return the dialog instance."""
		return self.dialog
