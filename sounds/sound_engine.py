import vlc
import os
import time

class SoundEngine:
    """
    SOUND ENGINE (MP3/WAV)
    ---------------------
    • MP3 + WAV supported
    • Files must be in SAME folder as this file
    • Windows CMD safe
    • Standalone test included
    """

    def __init__(self):
        print("🔊 Initializing SoundEngine...", flush=True)

        # Absolute path of THIS file's folder
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self._played = set()
        self._player = vlc.MediaPlayer()

        # ✅ INIT TTS ONCE
        import pyttsx3
        self._tts = pyttsx3.init()

        print(f"📁 Sound base path set to: {self.base_path}", flush=True)

    def _play(self, filename: str, key: str = None):
        print(f"🎵 Request to play sound: {filename}", flush=True)

        if key:
            print(f"🔑 Sound key: {key}", flush=True)

        if key and key in self._played:
            print(f"⏭️ Sound already played for key: {key} (skipping)", flush=True)
            return

        path = os.path.join(self.base_path, filename)

        if not os.path.isfile(path):
            print(f"🔇 Sound missing: {path}", flush=True)
            return

        print(f"▶ Playing sound file: {path}", flush=True)

        media = vlc.Media(path)
        self._player.set_media(media)
        self._player.play()

        if key:
            self._played.add(key)
            print(f"✅ Sound marked as played for key: {key}", flush=True)

    def reset(self, key: str):
        print(f"🔄 Resetting sound key: {key}", flush=True)
        self._played.discard(key)

    # ========== EVENTS ==========

    def bullish(self):
        print("📈 Bullish sound triggered", flush=True)
        self._play("Bullish.wav")

    def bearish(self):
        print("📉 Bearish sound triggered", flush=True)
        self._play("Bearish.wav")

    def binance_init_failed(self):
        print("❌ Binance init failed sound triggered", flush=True)
        self._play("Binance_init_failed.mp3", "BINANCE_INIT_FAILED")

    def futures_connection_reset(self):
        print("🔁 Futures connection reset sound triggered", flush=True)
        self._play(
            "Futures_connection_reset_Reconnecting_Binance_client.mp3",
            "FUTURES_RESET"
        )

    def internet_down(self):
        print("🌐 Internet down sound triggered", flush=True)
        self._play("InternetDown.mp3", "INTERNET_DOWN")

    def safeentry_price_failed(self):
        print("⚠ SafeEntry price fetch failed sound triggered", flush=True)
        self._play(
            "SafeEntry_price_fetch_failed_All_public_endpoints_failed.mp3",
            "SAFEENTRY_PRICE_FAIL"
        )

    def ip_not_whitelisted(self):
        print("🔐 IP not whitelisted sound triggered", flush=True)
        self._play(
            "Your IP is NOT whitelisted. Please add it to the whitelist..mp3",
            "IP_NOT_WHITELISTED"
        )

    def beep(self, repeat=1, delay=0.1):
        """
        Reliable beep using beep.wav
        """
        for _ in range(repeat):
            self._play("beep.wav")
            time.sleep(delay)

    def voice_alert(self, text):
        self._tts.say(text)
        self._tts.runAndWait()


# ==================================================
# STANDALONE MODE (TEST ALL SOUNDS)
# ==================================================
if __name__ == "__main__":
    print("🧪 SoundEngine STANDALONE TEST STARTED\n", flush=True)

    sound = SoundEngine()
    tests = [
        ("beep", lambda:sound.beep(2,1)),
        ("🗣 Text Alert", lambda: sound.voice_alert(
            "Binance connection failed. Switch to manual trading."
        )),
        ("📈 Bullish", sound.bullish),
        ("📉 Bearish", sound.bearish),
        ("❌ Binance init failed", sound.binance_init_failed),
        ("🔁 Futures connection reset", sound.futures_connection_reset),
        ("🌐 Internet down", sound.internet_down),
        ("⚠ SafeEntry price fetch failed", sound.safeentry_price_failed),
        ("🔐 IP not whitelisted", sound.ip_not_whitelisted),

    ]



    for label, fn in tests:
        print(f"\n▶ TEST: {label}", flush=True)
        fn()
        time.sleep(4)  # let sound play fully

    print("\n✅ Standalone sound test completed", flush=True)
