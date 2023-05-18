import threading
import time

def func1():
    print("Function 1 called")
    # Add the code for function 1 here

def func2():
    print("Function 2 called")
    # Add the code for function 2 here

def func3():
    print("Function 3 called")
    # Add the code for function 3 here

def func4():
    print("Function 4 called")
    # Add the code for function 4 here

def func5():
    print("Function 5 called")
    # Add the code for function 5 here

def schedule_function(func, interval, start_event):
    start_event.wait()
    while True:
        func()
        time.sleep(interval)

# Create start event to synchronize the start of the functions
start_event = threading.Event()

# Create and start threads for each function
thread1 = threading.Thread(target=schedule_function, args=(func1, 6, start_event))   # 1 minute
thread2 = threading.Thread(target=schedule_function, args=(func2, 18, start_event))  # 3 minutes
thread3 = threading.Thread(target=schedule_function, args=(func3, 30, start_event))  # 5 minutes
thread4 = threading.Thread(target=schedule_function, args=(func4, 90, start_event))  # 15 minutes
thread5 = threading.Thread(target=schedule_function, args=(func5, 180, start_event)) # 30 minutes

# Start all the threads simultaneously
for thread in [thread1, thread2, thread3, thread4, thread5]:
    thread.start()

# Signal the start event to start all the functions simultaneously
start_event.set()

# Wait for a keyboard interrupt (e.g., Ctrl+C) to stop the program
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

# Wait for all threads to complete
for thread in [thread1, thread2, thread3, thread4, thread5]:
    thread.join()

print("Program stopped.")
