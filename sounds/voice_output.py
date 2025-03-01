import speech_recognition as sr
import pyttsx3

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    # Option to input text manually
    user_input = input("Enter text to read aloud (or press Enter to use voice recognition): ")
    
    if user_input:
        # Convert the manually entered text to speech
        text_to_speech(user_input)
    else:
        # Recognize speech and convert it to text
        recognized_text = recognize_speech()
        
        # If text is recognized, convert it to speech
        if recognized_text:
            text_to_speech(recognized_text)