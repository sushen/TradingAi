import speech_recognition as sr
import pyttsx3

# Initialize the speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init()

# Set the voice and rate of the text-to-speech engine
engine.setProperty('voice', 'english')
engine.setProperty('rate', 150)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    # Use the microphone as the audio source
    with sr.Microphone() as source:
        # Adjust the recognizer sensitivity to ambient noise
        r.adjust_for_ambient_noise(source)
        # Listen for the user's input
        audio = r.listen(source)

    try:
        # Use the recognition library to convert the audio to text
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        # If the audio couldn't be recognized, prompt the user to try again
        speak("I'm sorry, I didn't understand what you said. Could you repeat that?")
        return listen()
    except sr.RequestError as e:
        # If there was an error with the recognition library, print the error and exit
        print("Error: {0}".format(e))
        exit()


# Example usage
text = listen()
speak("You said: " + text)
