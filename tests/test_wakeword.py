from voice.wake_word import WakeWord

wake = WakeWord()

print(wake.available_wake_words())

wake.start_listening()