from nicegui import ui, Client
from utils.state import state

def resize_all_textareas() -> None:
	"""Ensure all three metadata textareas resize properly on all connected clients."""
	for client in Client.instances.values():
		if not client.has_socket_connection:
			continue
		with client:
			for textarea in [state.meta_textarea_input, state.meta_textarea_xmp, state.meta_textarea_exif]:
				ui.run_javascript(f'''
					const el = document.querySelector("#{textarea.id} textarea");
					if (el) {{
						el.style.height = "auto";
						el.style.height = el.scrollHeight + "px";
						console.log(el.value);
					}} else {{
						console.error("Textarea not found:", "#{textarea.id} textarea");
					}}
				''')