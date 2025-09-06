# main.py

import multiprocessing as mp
import time
import sys
import signal
import cv2

from utils import change_window
import window
from window import BaseWindow
import grabscreen
from log import log
from actions import ActionExecutor
from pynput.keyboard import Listener, Key
import os

# Event to control running state
running_event = mp.Event()


def signal_handler(sig, frame):
    log.debug("Gracefully exiting...")
    running_event.clear()
    sys.exit(0)

def wait_for_game_window():
    while True: 
        frame = grabscreen.grab_screen()
        if frame is not None and window.set_windows_offset(frame):
            log.debug("Game window detected and offsets set!")
            return True
        time.sleep(1)
    return False

# 动作结束时的回调函数
def on_action_finished():
    log.debug("动作执行完毕")

def main_loop(): 
    if not wait_for_game_window():
        log.debug("Failed to detect game window.")
        return

    # 初始化动作执行器
    executor = ActionExecutor('./config/actions_conf.yaml')

    while True: 
        log.info('main loop running')
        '''
        frame = grabscreen.grab_screen()
        log.info('frame captured and will update all window')
        BaseWindow.set_frame(frame)
        BaseWindow.update_all()
        '''

        # 执行动作
        executor.take_action('EXP_1', action_finished_callback=on_action_finished)

        # 轮询检查是否在执行中
        while executor.is_running(): 
            log.debug("...")
            time.sleep(1)

        log.info('main loop end one epoch')


def on_press(key):
    print('on_press key: ', key)
    try:
        if key == Key.esc: 
            log.info('The user presses Esc in the game, will terminate.')
            os._exit(0)

    except Exception as e:
        print(e)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    listener = Listener(on_press=on_press)
    listener.start()
    log.info('keyboard listener setup. press Esc to exit')

    # Initialize camera
    grabscreen.init_camera(target_fps=6)

    change_window.correction_window()

    if change_window.check_window_resolution_same(window.game_width, window.game_height) == False:
        raise ValueError(
            f"游戏分辨率和配置game_width({window.game_width}), game_height({window.game_height})不一致，请到window.py中修改"
        )
    
    main_loop()


if __name__ == '__main__':
    main()
