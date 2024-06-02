import keyboard
import os
import pyautogui
import pystray
import threading
import tkinter
import time
import winsound
from PIL import Image, ImageDraw
from tkinter import messagebox

def create_icon():
	image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
	image_draw = ImageDraw.Draw(image)
	image_draw.rounded_rectangle(
		(8, 8, 56, 56),	# X,Y Coordinates (X0, Y0, X1, Y1)
		radius=10,
		fill='white',
		outline='black'
	)
	return image

def on_start(loop_event: threading.Event):
	def _on_start(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.set()
		winsound.MessageBeep()
	return _on_start

def on_stop(loop_event: threading.Event):
	def _on_stop(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.clear()
		winsound.MessageBeep()
	return _on_stop

def on_about():
	def _on_about(icon: pystray.Icon, item: pystray.MenuItem):
		about_message = "Gobbler Clicker v1.0\n\n"
		about_message += "A simple AFK autoclicker for the Candy Corn Gobbler in GW2.\n"
		about_message += "The clicker simulates mouse doubleclicks every 5 seconds.\n"
		about_message += "To start the autoclicker press F9, to end it press F10.\n"
		about_message += "Keep mousepointer over gobbler while autoclicker is active.\n\n"

		root = tkinter.Tk()
		root.title(" About Gobbler Clicker v1.0")
		root.geometry("600x300")

		if os.path.exists("icon/gobbler_clicker_icon.ico"):
			root.iconbitmap("icon/gobbler_clicker_icon.ico")
		
		label = tkinter.Label(root, text=about_message, wraplength=450)
		label.pack(padx=20, pady=20)

		ok_button = tkinter.Button(root, text="OK", command=root.destroy, width=10)
		ok_button.pack()

		root.mainloop()
	return _on_about

def on_exit(quit_event: threading.Event, loop_event: threading.Event):
	def _on_exit(icon: pystray.Icon, item: pystray.MenuItem):
		quit_event.set()
		loop_event.set()
		icon.stop()
	return _on_exit

def run_tray_icon(quit_event: threading.Event, loop_event: threading.Event):
	if os.path.exists("icon/gobbler_clicker_icon.ico"):
		image = Image.open("icon/gobbler_clicker_icon.ico")
	else:
		messagebox.showerror(title="[ERROR] File Not Found", message="[ERROR] File 'icon/gobbler_clicker_icon.ico' could not be found.\nGeneric icon used instead.")
		image = create_icon()
	
	menu = (
		pystray.MenuItem("Start (F9)", on_start(loop_event=loop_event)),
		pystray.MenuItem("Stop (F10)", on_stop(loop_event=loop_event)),
		pystray.MenuItem("About", on_about()),
		pystray.MenuItem("Exit", on_exit(quit_event=quit_event, loop_event=loop_event))
	)
	icon = pystray.Icon("Gobbler Clicker Icon", image, "Gobbler Clicker", menu)
	icon.run()

def run_keyboard_listener(quit_event: threading.Event, loop_event: threading.Event):
	while not quit_event.is_set():
		if keyboard.is_pressed('F9'):
			on_start(loop_event=loop_event)(None, None)

		elif keyboard.is_pressed('F10'):
			on_stop(loop_event=loop_event)(None, None)

		time.sleep(0.1)

def run_clicker_loop(quit_event: threading.Event, loop_event: threading.Event):
	while not quit_event.is_set():
		loop_event.wait()

		if quit_event.is_set():
			return
		
		pyautogui.doubleClick()
		time.sleep(5)

if __name__ == "__main__":
	quit_event = threading.Event()
	loop_event = threading.Event()

	tray_icon_thread = threading.Thread(target=run_tray_icon, args=(quit_event, loop_event))
	keyboard_listener_thread = threading.Thread(target=run_keyboard_listener, args=(quit_event, loop_event))
	clicker_loop_thread = threading.Thread(target=run_clicker_loop, args=(quit_event, loop_event))

	tray_icon_thread.start()
	keyboard_listener_thread.start()
	clicker_loop_thread.start()

	tray_icon_thread.join()
	keyboard_listener_thread.join()
	clicker_loop_thread.join()