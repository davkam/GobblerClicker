import keyboard
import pyautogui
import pystray
import threading
import time
import winsound
from PIL import Image
from tkinter import messagebox

def on_start(loop_event: threading.Event):
	def _on_start(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.set()
		winsound.Beep(1000, 150)
	return _on_start

def on_stop(loop_event: threading.Event):
	def _on_stop(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.clear()
		winsound.Beep(800, 150)
	return _on_stop

def on_about():
	def _on_about(icon: pystray.Icon, item: pystray.MenuItem):
		about_message = "Gobbler Clicker\n"
		about_message += "A simple AFK autoclicker for the Candy Corn Gobbler.\n"
		about_message += "Press F9 to start the autoclicker while the mousepointer is on the gobbler,"
		about_message += " end the autoclicker by pressing F10."
		messagebox.showinfo("About", about_message)
	return _on_about

def on_exit(quit_event: threading.Event, loop_event: threading.Event):
	def _on_exit(icon: pystray.Icon, item: pystray.MenuItem):
		quit_event.set()
		loop_event.set()
		icon.stop()
	return _on_exit

def run_tray_icon(quit_event: threading.Event, loop_event: threading.Event):
	image = Image.open("icon/gobbler_clicker_icon.png")
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