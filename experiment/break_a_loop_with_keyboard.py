import keyboard

for i in range(10000):
    for i in range(1000):
        # your loop code here
        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)

        print()
        print()
        print()
        print()

        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)
        print(100000 * 10000)

        print()
        print()
        print()
        print()
        print("Loop fully end.")
    # end of loop code

    # check for "q" key press
    if keyboard.is_pressed('q'):
        break

# code to execute after the loop
print("Loop finished")