#/usr/bin/env python3
import base64
from globalhotkeys import GlobalHotKeys, key_to_str
import signal
import time
import subprocess

from pynput import keyboard
import pyperclip

from typing import List

ghk = GlobalHotKeys()
running = True
item_buf = []

class Item:
	name: str
	link: str

	def __init__(self, name, link):
		self.name = name
		self.link = link
	
	def get_amount(self):
		clean_link = self.link[2:-1]
		decoded_data = base64.b64decode(clean_link)
		return decoded_data[1]

	def set_amount(self, amount:int):
		clean_link = self.link[2:-1]
		decoded_data = base64.b64decode(clean_link)
		modified_data = decoded_data[:1] + amount.to_bytes(1, "little") + decoded_data[2:]
		new_link = base64.b64encode(modified_data)
		self.link = "[&{}]".format(new_link.decode("utf-8"))

data_dict = {
		"LI/LD" : {"Legendary Insight": "[&AgH2LQEA]", "Legendary Divination": "[&AgGlWQEA]"},
		"Wings" : {
			"W1" : {"Vale Guardian": "[&AgGJLwEA]", "Gorseval": "[&AgG3LwEA]", "Sabetha": "[&AgGgLwEA]"},
			"W2" : {"Slothasor": "[&AgGKLwEA]",  "Matthias": "[&AgFvLwEA]"},
			"W3" : {"Escort" : "[&AgFtNAEA]", "Keep Construct" : "[&AgE2NAEA]", "Xera": "[&AgFeNAEA]"},
			"W4" : {"Cairn": "[&AgHvOgEA]", "Mursaat Overseer": "[&AgGNOQEA]", "Samarog": "[&AgHXOAEA]", "Deimos": "[&AgGeOgEA]"},
			"W5" : {"Soulless Horror": "[&AgHpTwEA]", "River of Souls": "[&AgEZTwEA]", "Statues of Grenth": "[&AgEoTwEA]", "Voice in the Void": "[&AgGBTgEA]"},
			"W6" : {"Conjured Amalgamate": "[&AgHfWQEA]",
				"Twin Largos" : {"Twin Largos": "[&AgEcWwEA]", "Bronze Twin Largos": "[&AgE8WgEA]", "Silver Twin Largos": "[&AgEQWgEA]", "Gold Twin Largos": "[&AgHuWQEA]"},
				"Qadim": "[&AgFFWgEA]"},
			"W7" : {"Cardinal Sabir's": "[&AgGGZAEA]", "Cardinal Adina": "[&AgFuZAEA]", "Ether Djinn": "[&AgEnZAEA]"}
			},
		"Fractals": "[&AgFPPwEA]",
		}

# https://wiki.guildwars2.com/wiki/Chat_link_format
def modify_chat_link(link: str, amount: int):
	clean_link = link[2:-1]
	decoded_data = base64.b64decode(clean_link)
	modified_data = decoded_data[:1] + amount.to_bytes(1, "little") + decoded_data[2:]
	new_link = base64.b64encode(modified_data)
	return "[&{}]".format(new_link.decode("utf-8"))


def save_to_clipboard(string: str):
	print("Saving '{}' to clipboard".format(string))
	pyperclip.copy(string)
	
def select_item(data) -> Item:
	current_options = data
	while current_options is not None:
		key_map = {}
		i = 1
		for option in current_options.keys():
			key_map[i] = option
			print("{} ({}) ".format(option, i), end="")
			i += 1
		print("\n'q' to quit")
		user_input = input()
		if user_input == "q":
			return None
		key = key_map[int(user_input)]
		next_options = current_options[key]
		if type(next_options) is not dict:
# TODO: enable/disable continous mode
#			continous_mode = False
#			user_input = input("Activate continous mode? [Y/n]")
#			print(str(user_input))
#			if user_input == "" or user_input[-1] == "y":
#				user_input = 0

			user_input = int(input("Input amount for {} (0-255). 0 enables you to type the amount before pressing the hotkey:".format(key)))
			if user_input < 0 or user_input > 255:
				print("Invalid amount!")
				next_options = current_options
			
			item = Item(key, next_options)
			item.set_amount(user_input)
			save_to_clipboard(item.link)
			return item
		current_options = next_options

def send_notification(title: str, text: str):
	subprocess.Popen(["notify-send", title, text])

def copy_items(items: List):
	clipboard_str = ""
	notify_str = ""
	for item in items:
		clipboard_str += item.link
		notify_str += "{} of {}\n".format(item.get_amount(), item.name)


	save_to_clipboard(clipboard_str)
	send_notification("GW2 Item", notify_str)

def assign_hotkey(item_param: Item):
	print("Press hotkey to assign this action to (Enter to skip)")
	user_confirmed = False
	while not user_confirmed:
		print("Waiting for key...")
		key = ghk.get_next_key()
		print("Pressed {}".format(key))
		if key == keyboard.Key.enter:
			input() # flush the input
			return
		user_input = input("Using {} as the key. Is this correct? [Y/n]".format(key))
		if user_input == "" or user_input[-1] == "y":
			user_confirmed = True

	def on_hotkey(key_hist):
		# TODO: proper copy?
		item = Item(item_param.name, item_param.link)
		if item.get_amount() == 0:
			prev_num = 0
			for i in range(1,4):
				key_str = key_to_str(key_hist[i])
				if not key_str.isdigit():
					break
				prev_num += int(key_str)*10**(i-1)
			item.set_amount(prev_num)
		item_buf.append(item)
		copy_items(item_buf)
	ghk.register(key, func=on_hotkey)

if __name__ == "__main__":
	def esc_event(key_hist):
		item_buf.clear()
		send_notification("GW2 Item", "Buffer cleared")

	ghk.register(keyboard.Key.esc, func = esc_event)
	while running:
		selected_link = select_item(data_dict)
		if selected_link is not None:
			assign_hotkey(selected_link)
			time.sleep(0.1)
