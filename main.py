import os
# silence tensorflow warnings and info
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import tensorflow as tf
from typing import Iterable, List, Set, Dict
from pynput.keyboard import Listener
from itertools import cycle

Key = str
Keys = Iterable[Key]
KeyDictionary = Dict[Key, int]
KeysDown = Set[Key]
Drawing = List[KeysDown]

class KeyTracker:
    default_valid_keys: str = 'abcdefghijklmnopqrstuvwxyz1234567890-=[]\\;\',./'

    def __init__(self, valid_keys: Keys = default_valid_keys):
        self.history: List[KeysDown] = []
        self.valid_keys = valid_keys
        self.keys_pressed: KeysDown = set()
        self.listener = Listener(self.on_press, self.on_release)
        self.listener.start()

    def str_key(self, key):
        ans = str(key)
        # cut the quotes off the end
        if (ans[0] == "'" and ans[-1] == "'") or (ans[0] == '"' and ans[-1] == '"'):
            ans = ans[1:-1]
        return ans

    def clear(self):
        self.history = []
        self.keys_pressed = set()

    def on_press(self, key):
        key: str = self.str_key(key)
        if key in self.valid_keys:
            self.keys_pressed.add(key)
            self.history.append(self.keys_pressed.copy())

    def on_release(self, key):
        try:
            # this may raise a KeyError
            self.keys_pressed.remove(self.str_key(key))
            # this should not raise any errors
            self.history.append(self.keys_pressed.copy())
        except KeyError:
            # key was pressed before the script was running or it's not a key we care about
            pass

    def __del__(self):
        self.listener.stop()

def vectorize(vector_like):
    return tf.convert_to_tensor(vector_like, dtype=tf.float32)

def batchify(vector):
    '''Make a batch out of a single example'''
    return vectorize([vector])

def keys_to_key_dictionary(keys: Keys):
    return {key: key_index for key_index, key in enumerate(keys)}

def drawing_to_vector(drawing: Drawing, key_dictionary: KeyDictionary):
    vector_length = len(key_dictionary)
    ans = []
    for keys_pressed in drawing:
        vector = [0] * vector_length
        for key in keys_pressed:
            try:
                vector_index = key_dictionary[key]
            except KeyError as e:
                raise ValueError(f"Key {repr(key)} could not be found in the key dictionary: {key_dictionary}")
            vector[vector_index] = 1

        vector = vectorize(vector)
        ans.append(vector)
    return vectorize(ans)


def get_drawing(key_tracker: KeyTracker, pause_time: float) -> Drawing:
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
                next_history_index += 1
                if not keys_pressed:
                    # TODO change this so that it's just checking while the wait period is occurring
                    sleep(pause_time)
                    if not key_tracker.history[next_history_index:]:
                        # they did not press a key in the given time
                        done = True
                        end_index = next_history_index - 1
                        # print("too slow!")
                    else:
                        pass
                        # print("saved")
            if done:
                # exit the loop
                break

    assert start_index is not None
    ans = [keys_pressed.copy() for keys_pressed in key_tracker.history[start_index:end_index]]
    return ans

if __name__ == "__main__":
    from time import sleep
    from tensorflow.keras.layers import LSTM, Input, Dense
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam

    keys_that_matter: Keys = KeyTracker.default_valid_keys
    # if the user lifts all their fingers from the keyboard, how many seconds we should wait before assuming the stroke is over
    lift_pause = 1
    keys_that_matter_dictionary = keys_to_key_dictionary(keys_that_matter)
    easy_drawing_to_vector = lambda drawing: drawing_to_vector(drawing, keys_that_matter_dictionary)
    key_tracker = KeyTracker(valid_keys=keys_that_matter)
    easy_get_drawing = lambda: get_drawing(key_tracker, lift_pause)

    number_of_good_examples = 5
    number_of_bad_examples = 5

    lstm_input = Input(shape=(None, len(keys_that_matter)))
    lstm_layer1 = LSTM(20)(lstm_input)
    lstm_output = Dense(2)(lstm_layer1)
    lstm_model = Model(inputs=lstm_input, outputs=lstm_output)

    numbers_of_examples = [number_of_good_examples, number_of_bad_examples]
    good_bad_words = ["good", "bad"]
    drawings = [[], []]

    for good_bad_index in range(2):
        for good_example_index in range(number_of_good_examples):
            print(f"Please do a {good_bad_words[good_bad_index]} example:")
            drawing = easy_get_drawing()
            drawings[good_bad_index].append(drawing)
            print(key_tracker.history)


    good_bad_vectors = [vectorize([1, 0]), vectorize([0, 1])]

    dataset = []
    for good_bad_index in range(2):
        for drawing in drawings[good_bad_index]:
            drawing_vector = easy_drawing_to_vector(drawing)
            good_bad_vector = good_bad_vectors[good_bad_index]
            dataset_example = (batchify(drawing_vector), batchify(good_bad_vector))
            dataset.append(dataset_example)

    epochs = 250
    steps_per_epoch = len(dataset)
    dataset_generator = (thing for thing in cycle(dataset))

    lstm_model.compile(Adam(), loss='mse')
    lstm_model.fit(dataset_generator, epochs=epochs, steps_per_epoch=steps_per_epoch)

    while True:
        print("Do something:")
        drawing = easy_get_drawing()
        input_vector = easy_drawing_to_vector(drawing)
        batch = batchify(input_vector)
        network_output = lstm_model.predict(batch)
        # The first number should be bigger than the second if it's the "good" drawing
        # The second number should be bigger than the first if it's the "bad" drawing
        print(network_output)
