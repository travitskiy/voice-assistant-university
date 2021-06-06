import difflib
import time
from threading import Thread

from speech_recognition import UnknownValueError

from tray import SystemTrayIconVoiceAssistant
from commands import *
import logging
import vlc


class Worker(Thread):
    def __init__(self, icon):
        super().__init__()
        self.icon = icon

    def run(self):
        recognizer = VoiceRecognizer(self.icon)
        commands = [OpenBrowserCommand(), OpenNewsCommand(), FindCommand(), RadioCommand(), CloseCommand(),
                    CloseBrowserCommand(), Exit(self.icon.app), ClosePlayerCommand()]
        commands.extend(load_commands("commands.json"))
        key_phrase = 'помощник'

        while True:
            time.sleep(1)
            try:
                self.icon.set_default()
                print("Говорите")
                data = recognizer.recognize_voice()
                print("Вы сказали: " + data.lower())
                logging.info("Вы сказали: " + data.lower())
                voice_text = data.lower()

                if len(voice_text) < len(key_phrase):
                    continue

                seq = difflib.SequenceMatcher(None, key_phrase, voice_text[0:len(key_phrase)]).ratio() * 100

                if seq < 75:
                    print('не с ключевой')
                    logging.error('ключевое слово - Помощник - не распознано: ' + data.lower())
                    self.icon.set_error()
                    continue

                command, argument = predict_command_by_name(voice_text[len(key_phrase):].strip(), commands)

                if command is not None:
                    command.run(argument if len(argument) != 0 else None)
                else:
                    logging.info("Такой команды нет: " + data.lower())
                    self.icon.set_error()
            except Exception as e:
                print(e)
                if e.__class__ == UnknownValueError:
                    continue
                self.icon.set_error()


def main():
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    icon = SystemTrayIconVoiceAssistant()
    worker = Worker(icon)
    worker.daemon = True
    worker.start()
    icon.start_processor()


if __name__ == '__main__':
    main()
