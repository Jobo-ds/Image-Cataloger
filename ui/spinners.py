from nicegui import ui

class PremadeSpinner:
    def __init__(self, size="base", classes=""):
        self.spinner = ui.spinner(size=size).classes(f'{classes} hidden z-50')

    def show(self):
        """Show the spinner."""
        self.spinner.classes(remove='hidden')

    def hide(self):
        """Hide the spinner."""
        self.spinner.classes(add='hidden')
