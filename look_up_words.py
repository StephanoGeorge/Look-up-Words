import argparse
import platform
from subprocess import run, Popen, DEVNULL

from web_chi_dict import WordYouDao

p = platform.system()
no_such_word_expire_time = 3

parser = argparse.ArgumentParser()
parser.add_argument('--hot-key', default='windows+c',
                    help='Hot key to call looking up words, only for Windows, for Linux, please use system setting')
parser.add_argument('--expire-time', default=20, help='Expire time of the notification in second')
parser.add_argument('--types', default=['us', 'uk', 'tts'], action='extend',
                    help="List of pronunciation types, 'us' for USA, 'uk' for UK, 'tts' for Text-to-Speak")
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
    word = WordYouDao(word_str)
    word_name = word['query']
    if 'basic' in word.json:
        means = replace('\n'.join(word['basic']['explains']))
    elif 'web' in word.json:
        means = replace('\n'.join(word['web'][0]['value']))
    else:
        means = replace('\n'.join(word['translation']))
    pronunciation = word.get_pronunciation(args.types)
    content = f'{pronunciation}\n{means}'
    if p == 'Linux':
        Popen(['notify-send.py', '--expire-time', f'{args.expire_time * 1000}', f'{word_name}', content],
              stdout=DEVNULL)
    else:
        toaster.show_toast(word_name, content, duration=args.expire_time, threaded=True)
    word.speak(args.types)


if p == 'Windows':
    keyboard.add_hotkey(args.hot_key, look_up)
    keyboard.wait()
else:
    look_up()
