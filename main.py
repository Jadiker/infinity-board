from typing import Iterable
from pynput.keyboard import Key, Listener

class KeyTracker:
    default_valid_keys: str = 'abcdefghijklmnopqrstuvwxyz1234567890-=[]\\;\',./'

    def __init__(self, valid_keys: Iterable[str] = default_valid_keys):
        self.valid_keys = valid_keys
        self.keys_pressed = set()
        self.listener = Listener(self.on_press, self.on_release)
        self.listener.start()

    def on_press(self, key):
        str_key = str(key)
        assert (str_key[0] == "'" and str_key[-1] == "'") or (str_key[0] == '"' and str_key[-1] == '"'), str_key
        str_key = str_key[1:-1]
        if str_key in self.valid_keys:
            self.keys_pressed.add(str(key))
        print(self.keys_pressed)

    def on_release(self, key):
        try:
            self.keys_pressed.remove(str(key))
        except KeyError:
            # key was pressed before the script was running or it's not a key we care about
            pass
        print(self.keys_pressed)

    def __del__(self):
        self.listener.stop()


#
# def on_press(key):
#     print('{0} pressed'.format(
#         key))
#
# def on_release(key):
#     print('{0} release'.format(
#         key))
#     if key == Key.esc:
#         # Stop listener
#         return False
#
# # Collect events until released
# with Listener(
#         on_press=on_press,
#         on_release=on_release) as listener:
#     listener.join()

if __name__ == "__main__":
    kt = KeyTracker()
    print(kt.valid_keys)
    print(len(kt.valid_keys))
    import time
    time.sleep(10)
