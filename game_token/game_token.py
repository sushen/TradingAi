"""
My Idea is to Reword Toke when Someone makes right prediction
"""
import random

# Create a dictionary to store the game tokens for each player
tokens = {}

while True:
  # Create a list of the three numbers
  numbers = [-100, 0, 100]

  # Generate a random number from the list
  number = random.choice(numbers)
  print(number)
  # Prompt the user to enter their name
  name = input("Enter your name: ")
  # name = "Sushen Biswas"

  # Prompt the user to guess the number
  guess = int(input("Guess the number: "))

  # Check if the user's guess is correct
  if guess == number:
    # If the guess is correct, award the user a game token
    if name in tokens:
      tokens[name] += 1
    else:
      tokens[name] = 1
    print("Congratulations, you guessed the correct number! You have received a game token.")
  else:
    # If the guess is incorrect, print a message indicating that the guess was incorrect and what the correct number was
    print("Sorry, that is not the correct number. The correct number was", number)

  print(tokens)

