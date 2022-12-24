import pyttsx3

engine = pyttsx3.init()

# Set the voice and rate of the text-to-speech engine
engine.setProperty('voice', 'english')
engine.setProperty('rate', 150)


def speak(text):
    engine.say(text)
    engine.runAndWait()


speak("Keep in mind that these are just a few of the many steps involved in creating a new game. It can be a complex process, and you may need to iterate and make changes as you go. However, with hard work and persistence, you can create a game that is both fun and engaging for players. Is there anything specific you would like to know about the process of creating a new game?")
