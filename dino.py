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
    def __init__(self, game_over, environ):
        self.alive = True
        self.speed = 0
        self.mem = [[0]*64+[0]]
        self.X = []
        self.y = []
        self.w = []
        self.jump_time = 0
        self.first_game = True

        self.model = Sequential()
        self.model.add(Dense(64, input_dim=64, activation="relu", kernel_initializer="he_uniform"))
        self.model.add(Dense(64, activation="relu", kernel_initializer="he_uniform"))
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
        # Переписать
        if len(self.mem) > 3:
            for row in self.mem[:-3]:
                self.X.append(row[:-1])
                self.y.append([row[-1]])
                self.w.append(1)
                print(''.join((str(l) for l in self.X[-1])), self.y[-1])
            print('')
            for row in self.mem[-3:]:
                self.X.append(row[:-1])
                self.y.append([int(not row[-1])])
                self.w.append(0.5)
                print(''.join((str(l) for l in self.X[-1])), self.y[-1])

        else:
            print('low')
            for row in self.mem:
                self.X.append(row[:-1])
                self.y.append([int(not row[-1])])
                self.w.append(0.5)
                print(''.join((str(l) for l in self.X[-1])), self.y[-1])

        with open('data_2.sav', 'w+') as d_file:
            for i in range(len(self.X)):
                d_file.write(str(self.X[i]))
                d_file.write(',')
                d_file.write(str(self.y[i]))
                d_file.write(',')
                d_file.write(str(self.w[i]))
                d_file.write('\n')
        self.mem = [[0]*64+[0]]

        print('X:', np.shape(self.X), 'Classes:', len(np.unique(self.y)))

        if len(np.unique(self.y)) > 1:

            if np.shape(self.X)[0] < 100:
                MAX_EPOCHS = 10
            else:
                MAX_EPOCHS = 1

            with self.graph.as_default():
                self.model.fit(np.array(self.X), np.array(self.y), sample_weight=np.array(self.w), epochs=MAX_EPOCHS,
                               verbose=0)
                self.model.save('dino_2.model')
            self.first_game = False

    def live_play(self, game_over, environ, restart):

        empty = [0] * 32
        g_start = time.time()

        while self.alive:

            self.speed = int(time.time() - g_start)

            if game_over.is_set():
                print ("GAME OVER")
                self.think()
                keyboard.press_and_release('up, up')
                while environ.poll():
                    print('+')
                    _ = environ.recv()

                g_start = time.time()
                print('RESTART')
                game_over.clear()
                restart.send('restart')

            elif environ.poll():
                cur_env = environ.recv()

                if cur_env != empty and (time.time() - self.jump_time) > 0.35:
                    with self.graph.as_default():
                        p = self.model.predict(np.array([self.mem[-1][32:-1] + cur_env]))[0][0]
                        if self.first_game:
                            x = np.random.choice([0, 1], p=[0.5, 0.5])
                        else:
                            x = np.random.choice([0, 1], p=[1 - p, p])

                        if x == 1:
                            self.dino_jump()

                        self.mem.append(self.mem[-1][32:-1] + cur_env + [x])

        #except (KeyboardInterrupt, SystemExit):
        #    self.alive = False
        #    print('exit')



