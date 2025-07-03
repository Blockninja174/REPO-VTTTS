import speech_recognition as sr
import time
import keyboard
from pynput.keyboard import Controller as KeyboardController
import threading
import queue
import re

def split_sentences(text):
    # Split text into sentences using regex for '.', '!', '?'
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    return [s.strip() for s in sentence_endings.split(text) if s.strip()]

def listen_and_paste_sentences():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    kb = KeyboardController()
    sentence_queue = queue.Queue()
    stop_event = threading.Event()

    def listener():
        print("Adjusting for ambient noise... Please wait.")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready! Speak now.")
        while not stop_event.is_set():
            try:
                with mic as source:
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=10)
                print("Recognizing...")
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                sentences = split_sentences(text)
                for sentence in sentences:
                    sentence_queue.put(sentence)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Could not understand audio. Try again.")
                continue
            except Exception as e:
                print(f"Listener error: {e}")
                break
        print("Listener stopped.")

    def paster():
        while not stop_event.is_set():
            try:
                sentence = sentence_queue.get(timeout=0.1)
                # Paste the sentence (simulate Ctrl+V or type sentence)
                kb.type(sentence)
                time.sleep(0.05)
                # Press 'Enter' after each sentence
                kb.press('\n')
                kb.release('\n')
                time.sleep(0.2)
                sentence_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Paster error: {e}")
                break
        print("Paster stopped.")

    listener_thread = threading.Thread(target=listener, daemon=True)
    paster_thread = threading.Thread(target=paster, daemon=True)
    listener_thread.start()
    paster_thread.start()

    try:
        while listener_thread.is_alive() and paster_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting.")
        stop_event.set()
        listener_thread.join()
        paster_thread.join()

if __name__ == "__main__":
    listen_and_paste_sentences()
