# coding: utf-8


import pyautogui
import multiprocessing
from multiprocessing import Array
import keyboard
import time
import numpy as np
import Quartz.CoreGraphics as CG
from dino import Pac

region = CG.CGRectMake(0, 0, 100, 100)
image = CG.CGWindowListCreateImage(region, 1, 0, 0)


# OS X screen capture


def get_img(x,y,w,h):
    region = CG.CGRectMake(x, y, w, h)
    image = CG.CGWindowListCreateImage(region, 1, 0, 0)

    width = CG.CGImageGetWidth(image)
    height = CG.CGImageGetHeight(image)
    bytesperrow = CG.CGImageGetBytesPerRow(image)

    pixeldata = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(image))
    image = np.frombuffer(pixeldata, dtype=np.uint8)
    image = image.reshape((height, bytesperrow // 4, 4))
    im = image[:, :width, :]
    return im


# Процесс для героя


def pac_process(game_start, game_over, environ, restart, env_len):
    pacman = Pac(game_over, environ, env_len)
    x = game_start.recv()

    print('GAME START')

    pacman.live_play(game_over, environ, restart)


# Процесс для окружения


def env_process(game_start, game_over, environ_, restart, env_len):

    t_rex, t_rex_y, w, h = pyautogui.locateOnScreen("./images/t_rex_head.png")
    print(t_rex, t_rex_y, h)
    start_round = True

    while True:

            im = get_img(t_rex + w, t_rex_y - 16, env_len, h // 2 + 17)

            c1 = im[5, 225, 0]
            c2 = im[5, 224, 0]
            # print (c1[0],c2[0])
            if c1!= c2 and (c1 == 83 or c2 == 83):
                print('GO - ', time.time())
                game_over.set()
                print('GO SENT - ', time.time())
                while not restart.poll():
                    pass
                while restart.poll():
                    _ = restart.recv()
                start = time.time()
                while time.time() - start < 1:
                    pass
                keyboard.press_and_release('up, up')
                print('RESTARTED')
            else:
                environ = [0] * env_len
                for i in range(0, env_len):
                    c = im[h // 2 + 16, i, 0]
                    if c == 83:
                        environ[i] = 1
                environ_[:] = environ[:]
            if start_round:
                game_start.send('ok')
                start_round = False


if __name__ == '__main__':
    game_start_parent, game_start_child = multiprocessing.Pipe()
    game_over = multiprocessing.Event()
    environ_parent, environ_child = multiprocessing.Pipe()
    restart_parent, restart_child = multiprocessing.Pipe()
    environment_len = 400
    environ_shared = Array('i', [0] * environment_len)
    proc1 = multiprocessing.Process(target=pac_process, args=(game_start_child,
                                                              game_over,
                                                              environ_shared,
                                                              restart_parent,
                                                              environment_len))
    proc2 = multiprocessing.Process(target=env_process, args=(game_start_parent,
                                                              game_over,
                                                              environ_shared,
                                                              restart_child,
                                                              environment_len))
    proc1.start()
    proc2.start()
    proc1.join()
    proc2.join()
    print('done')