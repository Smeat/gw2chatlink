#/usr/bin/env python3
import base64
from globalhotkeys import GlobalHotKeys
import signal
import time

from pynput import keyboard
import pyperclip

ghk = GlobalHotKeys()
running = True

data_dict = {
		"LI/LD" : {"Legendary Insight": "[&AgH2LQEA]", "Legendary Divination": "[&AgGlWQEA]"},
		"Wings" : {
			"W1" : {"Vale Guardian" : "[&AgGJLwEA]", "Gorseval" : "[&AgG3LwEA]", "Sabetha": "[&AgGgLwEA]"},
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
	
def select_item(data) -> str:
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
			user_input = int(input("Input amount for {} (1-255):".format(key)))
			if user_input < 1 or user_input > 255:
				print("Invalid amount!")
				next_options = current_options
			
			chat_link = modify_chat_link(next_options, user_input)
			save_to_clipboard(chat_link)
			return chat_link
		current_options = next_options

def assign_hotkey(string: str):
	print("Press hotkey to assign this action to (Enter to skip)")
	user_confirmed = False
	while not user_confirmed:
		print("Waiting for key...")
		key = ghk.get_next_key()
		if key == keyboard.Key.enter:
			input() # flush the input
			return
		user_input = input("Using {} as the key. Is this correct? [Y/n]".format(key))
		if user_input == 0 or user_input[-1] == "y":
			user_confirmed = True
	ghk.register(key, func=lambda: save_to_clipboard(string))

if __name__ == "__main__":
	
	while running:
		selected_link = select_item(data_dict)
		if selected_link is not None:
			assign_hotkey(selected_link)
			time.sleep(0.1)
