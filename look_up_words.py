import argparse
import platform
import re
from subprocess import run, Popen, DEVNULL

from math import sqrt
from web_chi_dict import WordYouDao

p = platform.system()

parser = argparse.ArgumentParser()
parser.add_argument('--hot-key', default='windows+c',
                    help='Hot key to call looking up words, only for Windows, for Linux, please use system setting')
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
        # keyboard.send('ctrl+c')
        # time.sleep(0.1)  # Or can not get the least copied word
        word_str = pyperclip.paste()
    # word = re.sub(r'[^a-zA-Z0-9]', '', word)
    word_str = word_str.strip()
    word = WordYouDao(word_str)
    word_name = word['query']
    if word.has_word:
        if 'basic' in word.json:
            means = replace('\n'.join(word['basic']['explains']))
        elif 'web' in word.json:
            means = replace('\n'.join(word['web'][0]['value']))
        else:
            means = replace('\n'.join(word['translation']))
    else:
        means = 'No Such Word'
    pronunciation = word.get_pronunciation(args.types)
    content = f'{pronunciation}\n{means}'
    content_length = len(re.findall(r'[\u4e00-\u9fa5]', content))
    expire_time = int(sqrt(content_length)) + 2
    if p == 'Linux':
        Popen(['notify-send', '--expire-time', f'{expire_time * 1000}', f'{word_name}', content],
              stdout=DEVNULL)
    else:
        toaster.show_toast(word_name, content, duration=expire_time, threaded=True)
    word.speak(args.types)


if p == 'Windows':
    keyboard.add_hotkey(args.hot_key, look_up)
    keyboard.wait()
else:
    look_up()
