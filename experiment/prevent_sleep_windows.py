import pyautogui
import time
import math

width, height = pyautogui.size()  # Get the size of the screen.

radius = 100  # radius of the circle
center_x = width / 2  # center of the circle (x-coordinate)
center_y = height / 2  # center of the circle (y-coordinate)

start_time = time.time()  # start time
circulation_time = 10  # time for one circulation in seconds

while True:
    elapsed_time = time.time() - start_time
    angle = 2 * math.pi * (elapsed_time % circulation_time) / circulation_time
    x = center_x + math.cos(angle) * radius
    y = center_y + math.sin(angle) * radius
    pyautogui.moveTo(x, y)
    time.sleep(4)
    print("Working")
