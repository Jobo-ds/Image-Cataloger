# utils/exiftool_wrapper.py

import subprocess
import json
import shlex
import os
import threading

class PatchedExifTool:
	"""
	A patched version of ExifToolHelper that correctly handles UTF-8 filenames
	and metadata values, using a persistent ExifTool process.
	"""

	def __init__(self, executable="exiftool", common_args=None):
		self.executable = executable
		self.common_args = common_args or ["-stay_open", "True", "-@", "-"]
		self.process = None
		self.stdin = None
		self.stdout = None
		self.lock = threading.Lock()  # Protect shared process

	def start(self):
		"""Start the persistent ExifTool process with proper UTF-8 pipes."""
		if self.process is not None:
			return  # Already running

		env = os.environ.copy()
		env["LANG"] = "en_US.UTF-8"  # Force UTF-8 subprocess environment

		self.process = subprocess.Popen(
			[self.executable] + self.common_args,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,  # This enforces UTF-8 encoding in and out
			encoding="utf-8",
			env=env
		)
		self.stdin = self.process.stdin
		self.stdout = self.process.stdout

	def stop(self):
		"""Stop the persistent process."""
		if self.process:
			try:
				self.stdin.write("-stay_open\nFalse\n")
				self.stdin.flush()
				self.process.wait(timeout=5)
			except Exception:
				self.process.kill()
		self.process = None

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.stop()

	def _read_output(self):
		"""Read ExifTool's JSON output until the `{ready}` line."""
		out_lines = []
		while True:
			line = self.stdout.readline()
			if line.strip() == "{ready}":
				break
			out_lines.append(line)
		return "".join(out_lines)

	def get_tags(self, filepath, tags):
		with self.lock:
			self.start()

			args = [f"-{tag}" for tag in tags]
			cmd = args + ["-j", str(filepath), "-execute\n"]

			self.stdin.write("\n".join(cmd))
			self.stdin.flush()

			raw_output = self._read_output()
			return json.loads(raw_output)

	def set_tags(self, filepath, tags_dict, extra_args=None):
		with self.lock:
			self.start()

			cmd = []
			for tag, value in tags_dict.items():
				cmd.append(f"-{tag}={value}")
			cmd.append(str(filepath))
			if extra_args:
				cmd.extend(extra_args)

			cmd.append("-execute\n")

			self.stdin.write("\n".join(cmd))
			self.stdin.flush()

			raw_output = self._read_output()
			# Optional: parse output for success/failure
			return True
