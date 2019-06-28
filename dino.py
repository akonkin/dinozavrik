# coding: utf-8

import time
import numpy as np
import keyboard

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import Dense
from keras.models import load_model
import tensorflow as tf


class Pac:
    def __init__(self, game_over, environ, env_len=32):
        self.alive = True
        self.mem = [([0] * env_len * 2, 0)]
        self.X = []
        self.y = []
        self.w = []
        self.env_len = env_len
        self.jump_time = 0
        self.first_game = True

        self.model = Sequential()
        self.model.add(Dense(env_len*2, input_dim=64, activation="relu", kernel_initializer="he_uniform"))
        self.model.add(Dense(env_len*2, activation="relu", kernel_initializer="he_uniform"))
        self.model.add(Dense(1))
        self.model.add(Activation("sigmoid"))
        self.model.compile(loss="binary_crossentropy", optimizer='adam',
                           metrics=["accuracy"])
        self.graph = tf.get_default_graph()

        try:
            self.model = load_model('dino_2.model')
            print('Model loaded')
        except:
            print('New model')

    def dino_jump(self):
        keyboard.press_and_release('up')
        self.jump_time = time.time()

    def think(self):
        print('THINKING')
        mem_len = len(self.mem)
        for i in range(mem_len):
            if i < mem_len - 3:
                y_ = self.mem[i][1]
                w_ = 1
            else:
                y_ = int(not self.mem[i][1])
                w_ = 0.5

            self.X.append(self.mem[i][0])
            self.y.append([y_])
            self.w.append(w_)

            print(''.join((str(l) for l in self.X[-1])), self.y[-1], self.w[-1])

        with open('data_2.sav', 'w+') as d_file:
            for i in range(len(self.X)):
                d_file.write('{},{},{}\n'.format(self.X[i], self.y[i], self.w[i]))

        self.mem = [([0] * self.env_len * 2, 0)]

        print('X:', np.shape(self.X), 'Classes:', len(np.unique(self.y)))

        if len(np.unique(self.y)) > 1:

            if np.shape(self.X)[0] < 100:
                epochs = 10
            else:
                epochs = 1

            with self.graph.as_default():
                self.model.fit(np.array(self.X), np.array(self.y), sample_weight=np.array(self.w), epochs=epochs,
                               verbose=0)
                self.model.save('dino_2.model')
            self.first_game = False

    def live_play(self, game_over, environ, restart):

        empty = [0] * self.env_len

        while self.alive:

            if game_over.is_set():
                print ("GAME OVER")
                self.think()
                keyboard.press_and_release('up, up')
                while environ.poll():
                    print('+')
                    _ = environ.recv()

                print('RESTART')
                game_over.clear()
                restart.send('restart')

            elif environ.poll():
                cur_env = environ.recv()

                if cur_env != empty and (time.time() - self.jump_time) > 0.35:
                    with self.graph.as_default():
                        view = last_env + cur_env
                        p = self.model.predict(np.array([view]))[0][0]
                        if p > 0.95:
                            p = 1
                        elif p < 0.05:
                            p = 0
                        if self.first_game:
                            x = np.random.choice([0, 1], p=[0.5, 0.5])
                        else:
                            x = np.random.choice([0, 1], p=[1 - p, p])

                        if x == 1:
                            self.dino_jump()

                        self.mem.append((view, x))
                last_env = cur_env[:]
