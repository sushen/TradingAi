import requests
import sounddevice as sd
import numpy as np
import pyttsx3
import openai

# OpenAI API Key
open_ai_secret_key = "sk-YOUR-OPENAI-SECRET-KEY"
openai.api_key = open_ai_secret_key

# DeepSeek API Configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/speech-to-text"  # Replace with the actual DeepSeek endpoint
DEEPSEEK_API_KEY = "sk-055cab154f0141a4b7248789e6a3d373"  # Replace with your DeepSeek API key


def record_audio(duration=5, sample_rate=16000):
    """
    Record audio from the microphone using sounddevice for the given duration.
    :param duration: Duration in seconds for audio recording.
    :param sample_rate: Sampling rate for the recorded audio.
    :return: Numpy array containing audio data.
    """
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()  # Wait until the recording is finished
    return audio_data


def send_to_deepseek(audio_data, sample_rate=16000):
    """
    Send raw audio data to the DeepSeek API for speech-to-text conversion.
    :param audio_data: Numpy array containing audio data.
    :param sample_rate: Sampling rate of the audio.
    :return: Transcribed text (string) from the audio.
    """
    try:
        print("Sending audio to DeepSeek for recognition...")

        # Convert audio data to bytes
        audio_bytes = audio_data.tobytes()

        # Set up API request headers and data
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/octet-stream"  # Or the format required by DeepSeek
        }
        params = {
            "sample_rate": sample_rate
        }

        # Make the request
        response = requests.post(DEEPSEEK_API_URL, headers=headers, params=params, data=audio_bytes)
        response.raise_for_status()  # Raise an error if the request fails

        # Extract the transcription from the response
        transcription = response.json().get("text", "")
        print(f"Recognized text: {transcription}")
        return transcription

    except Exception as e:
        print(f"Error during DeepSeek API call: {e}")
        return ""


def send_to_openai(prompt):
    """
    Send the conversation text to OpenAI's GPT and return the generated response.
    """
    try:
        # OpenAI ChatCompletion API call
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the desired GPT model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and return the response content
        reply = response['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return f"An error occurred while communicating with OpenAI: {e}"


def text_to_speech(text):
    """
    Convert text to speech using pyttsx3 library.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    while True:
        # Step 1: Record audio
        audio = record_audio(duration=5)

        # Step 2: Use DeepSeek for speech recognition
        recognized_text = send_to_deepseek(audio)

        # Step 3: If transcription is available, send it to OpenAI
        if recognized_text:
            print("Sending conversation to OpenAI...")
            openai_response = send_to_openai(recognized_text)
            print("\nOpenAI Response:\n", openai_response)

            # Step 4: Use TTS to read the OpenAI response
            text_to_speech(openai_response)

        # Optional input for user to send custom text
        user_input = input("Enter text to send to OpenAI (or press Enter to speak again): ")
        if user_input:
            openai_response = send_to_openai(user_input)
            print("\nOpenAI Response:\n", openai_response)
            text_to_speech(openai_response)

        # Exit the loop if "exit" is recognized
        if recognized_text and recognized_text.lower() == "exit":
            print("Exiting...")
            break
