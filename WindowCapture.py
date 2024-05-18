import copy
import win32gui
import win32ui
import win32con
import cv2 as cv
import numpy as np
from threading import Thread, Lock

class WindowCapture:
    # constructor
    def __init__(self, window_name):
        self.__lock = Lock()
        self.__newestImage = np.array(np.zeros((100,100,1), dtype=np.uint8))
        self.__intermediaryImage = np.array(np.zeros((100,100,1), dtype=np.uint8))

        # find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        self.window_name = window_name
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        #print(f"self.w: {self.w}; self.h: {self.h}")

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        #self.w = self.w - (border_pixels * 2)
        #self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

        t1 = Thread(target=self.__doWork)
        t1.daemon = True
        t1.start()

    def get_screenshot(self):
        hwnd = win32gui.FindWindow(None, self.window_name)
        wndc = win32gui.GetWindowDC(self.hwnd)
        imdc = win32ui.CreateDCFromHandle(wndc)
        # create a memory based device context
        memdc = imdc.CreateCompatibleDC()
        # create a bitmap object
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(imdc, self.w, self.h)
        oldbmp = memdc.SelectObject(screenshot)
        # copy the screen into our memory device context
        memdc.BitBlt((0, 0), (self.w, self.h), imdc, (0, 0), win32con.SRCCOPY)
        memdc.SelectObject(oldbmp)
        bmpstr = screenshot.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        win32gui.DeleteObject(screenshot.GetHandle())
        imdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, wndc)
        memdc.DeleteDC()
        img.shape = (self.h, self.w, 4)
        img = cv.flip(img, 1)
        return cv.cvtColor(img, cv.COLOR_BGRA2GRAY)

    def __doWork(self):
        while True:
            try:
                window_rect = win32gui.GetWindowRect(self.hwnd)
                self.w = window_rect[2] - window_rect[0]
                self.h = window_rect[3] - window_rect[1]
                self.__intermediaryImage = self.get_screenshot()
                self.__lock.acquire()
                self.__newestImage = self.__intermediaryImage
                self.__lock.release()
            except Exception as ex:
                print(ex, flush=True)
                continue

    def GetLatestImage(self):
        self.__lock.acquire()
        copyImage = copy.copy(self.__newestImage)
        self.__lock.release()
        return copyImage