# coding: utf-8


import pyautogui
import multiprocessing
import keyboard
import time

from dino import Pac


# Процесс для героя


def pac_process(game_start, game_over, environ, restart):
    pacman = Pac(game_over, environ)
    x = game_start.recv()

    print('GAME START')

    pacman.live_play(game_over, environ, restart)


# Процесс для окружения


def env_process(game_start, game_over, environ_, restart):
    black_color = (83, 83, 83, 255)
    bg_color = (247, 247, 247, 255)
    white_color = (255, 255, 255, 255)

    t_rex, t_rex_y, w, h = pyautogui.locateOnScreen("./images/t_rex_head.png")
    print(t_rex, t_rex_y, h)
    start_round = True

    while True:

            im = pyautogui.screenshot(region=(t_rex + w, t_rex_y - 16, 320, h // 2 + 17))

            c1 = im.getpixel((225, 5))
            c2 = im.getpixel((224, 5))
            # print (c1[0],c2[0])
            if c1[0] != c2[0] and (c1[0] == 83 or c2[0] == 83):
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
                environ = [0] * 32
                for i in range(0, 320):
                    c = im.getpixel((i, h // 2 + 16))
                    if c == black_color:
                        environ[i // 10] = 1
                    i += 1
                environ_.send(environ)
            if start_round:
                game_start.send('ok')
                start_round = False


if __name__ == '__main__':
    game_start_parent, game_start_child = multiprocessing.Pipe()
    game_over = multiprocessing.Event()
    environ_parent, environ_child = multiprocessing.Pipe()
    restart_parent, restart_child = multiprocessing.Pipe()

    proc1 = multiprocessing.Process(target=pac_process, args=(game_start_child,
                                                              game_over,
                                                              environ_child,
                                                              restart_parent))
    proc2 = multiprocessing.Process(target=env_process, args=(game_start_parent,
                                                              game_over,
                                                              environ_parent,
                                                              restart_child))
    proc1.start()
    proc2.start()
    proc1.join()
    proc2.join()
    print('done')