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
	"""
    Create a simple 64x64 RGBA icon with a white rounded rectangle and a black outline.
    """

	image = Image.new('RGBA', (64, 64), (0, 0, 0, 0)) 	# Create a new transparent image
	image_draw = ImageDraw.Draw(image)					# Create a drawing context
	image_draw.rounded_rectangle(
		(8, 8, 56, 56),	# X,Y Coordinates (X0, Y0, X1, Y1) for the rectangle
		radius=10,		# Radius for the rounded corners
		fill='white',	# Fill color
		outline='black'	# Outline color
	)
	return image

def on_start(loop_event: threading.Event):
	"""
    Define the action to start the loop when the tray menu item is clicked.
    """

	def _on_start(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.set()		# Set the event to start the loop
		winsound.MessageBeep()	# Play a beep sound
	return _on_start

def on_stop(loop_event: threading.Event):
	"""
    Define the action to stop the loop when the tray menu item is clicked.
    """

	def _on_stop(icon: pystray.Icon, item: pystray.MenuItem):
		loop_event.clear() 	   	# Clear the event to stop the loop
		winsound.MessageBeep() 	# Play a beep sound
	return _on_stop

def on_about():
	"""
    Define the action to show an about dialog when the tray menu item is clicked.
    """

	def _on_about(icon: pystray.Icon, item: pystray.MenuItem):
		# About message details
		about_message = "Gobbler Clicker v1.0\n\n"
		about_message += "A simple AFK autoclicker for the Candy Corn Gobbler in GW2.\n"
		about_message += "The clicker simulates mouse doubleclicks every 5 seconds.\n"
		about_message += "To start the autoclicker press F9, to end it press F10.\n"
		about_message += "Keep mousepointer over gobbler while autoclicker is active.\n\n"

		# Create and configure a Tkinter window
		root = tkinter.Tk()
		root.title(" About Gobbler Clicker v1.0")
		root.geometry("600x300")

		# Set the icon if it exists
		if os.path.exists("icon/gobbler_clicker_icon.ico"):
			root.iconbitmap("icon/gobbler_clicker_icon.ico")
		
		# Create and pack a label with the about message
		label = tkinter.Label(root, text=about_message, wraplength=450)
		label.pack(padx=20, pady=20)

		# Create and pack an OK button to close the window
		ok_button = tkinter.Button(root, text="OK", command=root.destroy, width=10)
		ok_button.pack()

		root.mainloop() # Start the Tkinter main loop
	return _on_about

def on_exit(quit_event: threading.Event, loop_event: threading.Event):
	"""
    Define the action to exit the application when the tray menu item is clicked.
    """

	def _on_exit(icon: pystray.Icon, item: pystray.MenuItem):
		quit_event.set() # Set the event to quit
		loop_event.set() # Set the event to stop the loop
		icon.stop()		 # Stop the tray icon
	return _on_exit

def run_tray_icon(quit_event: threading.Event, loop_event: threading.Event):
	"""
    Run the system tray icon with a menu for start, stop, about, and exit actions.
    """

	# Check if the icon file exists and load it, otherwise create a default icon
	if os.path.exists("icon/gobbler_clicker_icon.ico"):
		image = Image.open("icon/gobbler_clicker_icon.ico")
	else:
		messagebox.showerror(title="[ERROR] File Not Found", message="[ERROR] File 'icon/gobbler_clicker_icon.ico' could not be found.\nGeneric icon used instead.")
		image = create_icon()
	
	# Define the tray menu with start, stop, about, and exit options
	menu = (
		pystray.MenuItem("Start (F9)", on_start(loop_event=loop_event)),
		pystray.MenuItem("Stop (F10)", on_stop(loop_event=loop_event)),
		pystray.MenuItem("About", on_about()),
		pystray.MenuItem("Exit", on_exit(quit_event=quit_event, loop_event=loop_event))
	)

	# Create and run the tray icon with the defined menu
	icon = pystray.Icon("Gobbler Clicker Icon", image, "Gobbler Clicker", menu)
	icon.run()

def run_keyboard_listener(quit_event: threading.Event, loop_event: threading.Event):
	"""
    Listen for F9 and F10 key presses to start and stop the clicker loop.
    """

	while not quit_event.is_set():
		if keyboard.is_pressed('F9'):
			on_start(loop_event=loop_event)(None, None) # Start the loop if F9 is pressed

		elif keyboard.is_pressed('F10'):
			on_stop(loop_event=loop_event)(None, None) 	# Stop the loop if F10 is pressed

		time.sleep(0.1) # Check keyboard input every 0.1 seconds

def run_clicker_loop(quit_event: threading.Event, loop_event: threading.Event):
	"""
    Perform double clicks every 5 seconds while the loop event is set.
    """

	while not quit_event.is_set():
		loop_event.wait() 	# Wait until the loop event is set

		if quit_event.is_set():
			return 			# Exit if the quit event is set
		
		pyautogui.doubleClick()	# Perform a double click
		time.sleep(5) 			# Wait for 5 seconds

if __name__ == "__main__":
	# Create event objects for quitting and looping
	quit_event = threading.Event()
	loop_event = threading.Event()

	# Create and start threads for tray icon, keyboard listener, and clicker loop
	tray_icon_thread = threading.Thread(target=run_tray_icon, args=(quit_event, loop_event))
	keyboard_listener_thread = threading.Thread(target=run_keyboard_listener, args=(quit_event, loop_event))
	clicker_loop_thread = threading.Thread(target=run_clicker_loop, args=(quit_event, loop_event))

	tray_icon_thread.start()
	keyboard_listener_thread.start()
	clicker_loop_thread.start()

	# Wait for all threads to complete
	tray_icon_thread.join()
	keyboard_listener_thread.join()
	clicker_loop_thread.join()