import speech_recognition as sr
import pyttsx3
import time


def recognize_speech():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.5  # Adjust this value as needed for pause duration
    all_recognized_text = []  # List to accumulate recognized text

    # Adjust the recognizer sensitivity to ambient noise
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please speak now... (The conversation will end after 5 seconds of silence)")

        last_speech_time = time.time()  # Track the last time speech was detected

        while True:  # Keep listening until a specific condition is met
            try:
                audio = recognizer.listen(source, timeout=5)  # Listen for up to 5 seconds

                # Ensure show_all is set to False to get only the best transcription
                text = recognizer.recognize_google(audio, show_all=False)  # Get the best transcription
                if isinstance(text, str):  # Check if the result is a string
                    all_recognized_text.append(text)  # Append recognized text to the list
                    print(f"Recognized: {text}")  # Print recognized text
                    last_speech_time = time.time()  # Update the last speech time

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                # Check for silence duration
                if time.time() - last_speech_time > 5:  # 5 seconds of silence
                    print("No speech detected for a while, finishing the conversation...")
                    break  # Exit if no speech is detected for the timeout duration

    full_conversation = ' '.join(all_recognized_text)  # Join all recognized text into a single string
    print("\n Full Conversation: \n", full_conversation, '\n')  # Print the full conversation
    return full_conversation  # Return the complete text as a single string


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    while True:
        # Recognize speech and convert it to text
        recognized_text = recognize_speech()

        # Option to input text manually
        user_input = input("Enter text to read aloud (or press Enter to use voice recognition): ")

        if user_input:
            # Convert the manually entered text to speech
            text_to_speech(user_input)
        else:
            # If text is recognized, convert it to speech
            if recognized_text:
                text_to_speech(recognized_text)

        # Optionally, break the loop if a specific command is recognized
        if recognized_text and recognized_text.lower() == "exit":
            print("Exiting...")
            break