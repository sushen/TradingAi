import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone(device_index=1) as source:
    r.adjust_for_ambient_noise(source)
    # Listen for the user's input
    audio = r.listen(source)

    text = r.recognize_google(audio)
    print(text)

