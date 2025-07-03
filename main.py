import speech_recognition as sr
import time
import keyboard
from pynput.keyboard import Controller as KeyboardController
import threading
import queue

def listen_and_type():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    kb = KeyboardController()
    word_queue = queue.Queue()
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
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=7)
                print("Recognizing...")
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                words = text.split()
                for word in words:
                    word_queue.put(word)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Could not understand audio. Try again.")
                continue
            except Exception as e:
                print(f"Listener error: {e}")
                break
        print("Listener stopped.")

    def typer():
        while not stop_event.is_set():
            try:
                word = word_queue.get(timeout=0.1)
                # Press 't'
                kb.type('t')
                time.sleep(0.05)
                # Type the word
                kb.type(word)
                time.sleep(0.05)
                # Press 'Enter'
                kb.press('\n')
                kb.release('\n')
                time.sleep(0.2)
                word_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Typer error: {e}")
                break
        print("Typer stopped.")

    listener_thread = threading.Thread(target=listener, daemon=True)
    typer_thread = threading.Thread(target=typer, daemon=True)
    listener_thread.start()
    typer_thread.start()

    try:
        while listener_thread.is_alive() and typer_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting.")
        stop_event.set()
        listener_thread.join()
        typer_thread.join()

if __name__ == "__main__":
    listen_and_type()
