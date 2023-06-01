import os
import openai
import pyttsx3

engine = pyttsx3.init()

# Set the voice and rate of the text-to-speech engine
engine.setProperty('voice', 'english')
engine.setProperty('rate', 150)
from prompt_toolkit.shortcuts import prompt

openai.api_key = os.environ.get("binance_open_ai_chat_bot")
# print(api_key)
#
def speak(text):
    engine.say(text)
    engine.runAndWait()

while True:
    prompt = input("Ask OpenAi Anything ?\n:")
    completions = openai.Completion.create(prompt=prompt,
                                          engine="text-davinci-002",
                                          max_tokens=100)
    completion = completions.choices[0].text
    print(completion)

    speak(completion)