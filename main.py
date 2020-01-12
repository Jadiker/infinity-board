import tensorflow as tf
from typing import Iterable, List, Set
from pynput.keyboard import Listener

Key = str
KeysDown = Set[Key]

class KeyTracker:
    default_valid_keys: str = 'abcdefghijklmnopqrstuvwxyz1234567890-=[]\\;\',./'

    def __init__(self, valid_keys: Iterable[Key] = default_valid_keys):
        self.history: List[KeysDown] = []
        self.valid_keys = valid_keys
        self.keys_pressed: KeysDown = set()
        self.listener = Listener(self.on_press, self.on_release)
        self.listener.start()

    def clear(self):
        self.history = []
        self.keys_pressed = set()

    def on_press(self, key):
        str_key = str(key)
        # cut the quotes off the end
        if (str_key[0] == "'" and str_key[-1] == "'") or (str_key[0] == '"' and str_key[-1] == '"'):
            str_key = str_key[1:-1]
        if str_key in self.valid_keys:
            self.keys_pressed.add(str(key))
            self.history.append(self.keys_pressed.copy())

    def on_release(self, key):
        try:
            # this may raise a KeyError
            self.keys_pressed.remove(str(key))
            # this should not raise any errors
            self.history.append(self.keys_pressed.copy())
        except KeyError:
            # key was pressed before the script was running or it's not a key we care about
            pass

    def __del__(self):
        self.listener.stop()

def vectorize(vector_like):
    return tf.convert_to_tensor(vector_like, dtype=tf.float32)

def get_example_to_vector(key_list: Iterable[Key]):
    key_dictionary = {key: key_index for key_index, key in enumerate(key_list)}
    def example_to_vector(keys_pressed: KeysDown):
        length = len(key_dictionary)
        ans = [0] * length
        for key in keys_pressed:
            try:
                vector_index = key_dictionary[key]
            except KeyError as e:
                raise ValueError(f"Key {repr(key)} could not be found in the key dictionary: {key_dictionary}")
            ans[vector_index] = 1

        ans = vectorize(ans)
        return ans

    return example_to_vector


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
    from time import sleep
    # from tensorflow.keras.layers import LSTM, Input
    # from tensorflow.keras.models import Model
    #
    # lstm_input = Input(shape=INPUT_SHAPE)
    # lstm_output = LSTM(20, return_sequences=True)(lstm_input)
    # lstm_model = Model(inputs=lstm_input, outputs=lstm_output)

    keys_that_matter = "tyufghjvbn"
    example_to_vector = get_example_to_vector(keys_that_matter)
    print(example_to_vector(set(["t", "u"])))

    key_tracker = KeyTracker(valid_keys=keys_that_matter)

    number_of_good_examples = 1
    number_of_bad_examples = 1

    # if the user lifts all their fingers from the keyboard, how many seconds we should wait before assuming the stroke is over
    lift_pause = 1

    numbers_of_examples = [number_of_good_examples, number_of_bad_examples]
    good_or_bad_words = ["good", "bad"]
    examples = [[], []]

    for good_or_bad_index in range(2):
        for good_example_index in range(number_of_good_examples):
            print(f"Please do a {good_or_bad_words[good_or_bad_index]} example:")
            key_tracker.clear()
            next_history_index = 0
            started = False
            start_index = None
            end_index = None
            while True:
                if started is False:
                    for index, keys_pressed in enumerate(key_tracker.history[next_history_index:]):
                        next_history_index += 1
                        if keys_pressed:
                            started = True
                            start_index = next_history_index - 1
                            break

                if started is True:
                    done = False
                    for index, keys_pressed in enumerate(key_tracker.history[next_history_index:]):
                        print(index)
                        next_history_index += 1
                        if not keys_pressed:
                            sleep(lift_pause)
                            if not key_tracker.history[next_history_index:]:
                                # they did not press a key in the given time
                                done = True
                                end_index = next_history_index - 1
                                print("too slow!")
                            else:
                                print("saved")
                    if done:
                        # exit the loop
                        break

            assert start_index is not None
            print(start_index, end_index)
            example = [keys_pressed.copy() for keys_pressed in key_tracker.history[start_index:end_index]]
            examples[good_or_bad_index].append(example)
            print(key_tracker.history)

    print("Examples:")
    print(examples)
