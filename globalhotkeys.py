from pynput import keyboard
import time
from collections import deque

MAX_QUEUE_SIZE = 4

def key_to_str(key):
	try:
		return str(key.char)
	except:
		return str(key)

class GlobalHotKeys():
	key_mapping = {}
	last_keys = deque()

	def __init__(self):
		listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
		listener.start()

	def _on_press(self, key):
		pass
	def _on_release(self, key):
		self.last_keys.appendleft(key)
		if len(self.last_keys) > MAX_QUEUE_SIZE:
			self.last_keys.pop()
		key = key_to_str(key)
		try:
			match = self.key_mapping[key]
			match[1]()
		except KeyError:
			pass

	def get_next_key(self):
		time.sleep(0.1)
		self.last_keys.pop()
		curr_len = len(self.last_keys)
		while len(self.last_keys) <= curr_len:
			time.sleep(0.1)
		return self.last_keys[0]

	def register(self, key, modifier=0, func=None):
		print("Registering {}".format(key))
		self.key_mapping[str(key)] = (modifier, func)

	def unregister(self, key):
		del self.key_mapping[str(key)]

