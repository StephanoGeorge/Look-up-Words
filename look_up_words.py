import argparse
import platform
from subprocess import run, Popen, DEVNULL

from iciba_word import Word

p = platform.system()
no_such_word_expire_time = 3

parser = argparse.ArgumentParser()
parser.add_argument('--hot-key', default='windows+c',
                    help='Hot key to call looking up words, only for Windows, for Linux, please use system setting')
parser.add_argument('--expire-time', default=20, help='Expire time of the notification in second')
parser.add_argument('--pronunciation-type', default='am',
                    help="'am' for American, 'en' for English, 'tts' for Text-to-Speak")
args = parser.parse_args()

if p == 'Linux':
    pass
elif p == 'Windows':
    import keyboard
    import pyperclip
    from win10toast import ToastNotifier

    toaster = ToastNotifier()
else:
    print(f'Not supported: {platform}')
    exit(1)


def replace(s: str):
    replaces = (('，', ','), ('。', '.'), ('、', ','), ('（', '('), ('）', ')'), ('：', ':'), ('；', ';'))
    for rep in replaces:
        s = s.replace(*rep)
    return s


def look_up():
    if p == 'Linux':
        word_str = run(['xclip', '-selection', 'primary', '-o'], capture_output=True).stdout.decode()
    else:
        keyboard.send('ctrl+c')
        word_str = pyperclip.paste()
    word_str = word_str.lower()  # Or iciba can not recognize
    # word = re.sub(r'[^a-zA-Z0-9]', '', word)
    word_str = word_str.strip()
    word = Word(word_str)
    word_name = word['word_name'] if word.has_word else f'No such word: {word_str}'
    pronunciation = word['symbols'][0][f'ph_{args.pronunciation_type}'] if word.has_word else ''
    means = replace('\n'.join(
        [f"{part['part']}: {','.join(part['means'])}" for part in word['symbols'][0]['parts']]
    )) if word.has_word else ''
    if p == 'Linux':
        if word.has_word:
            Popen(['notify-send.py', '--expire-time', f'{args.expire_time * 1000}', f'{word_name}',
                   f'{pronunciation}\n{means}'], stdout=DEVNULL)
            word.pronounce(speak=True)
        else:
            Popen(['notify-send.py', '--expire-time', f'{no_such_word_expire_time * 1000}', f'{word_name}', ''],
                  stdout=DEVNULL)
    else:
        if word.has_word:
            toaster.show_toast(word_name, f'{pronunciation}\n{means}', duration=args.expire_time)
            word.pronounce(speak=True)
        else:
            toaster.show_toast(word_name, '', duration=no_such_word_expire_time)


if p == 'Windows':
    keyboard.add_hotkey(args.hot_key, look_up)
    keyboard.wait()
else:
    look_up()
