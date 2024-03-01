import numpy as np
import win32con
import win32gui
import win32ui
import cv2 as cv
import copy
import time
from threading import Thread, Lock
from pywinauto import Desktop
import sys
import os
import ctypes

class WindowCapture:
    # constructor
    def __init__(self, window_name):
        self.__lock = Lock()
        self.__newestImage = np.array(np.zeros((100,100,3), dtype=np.uint8))
        self.__intermediaryImage = np.array(np.zeros((100,100,3), dtype=np.uint8))

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
        return cv.cvtColor(img, cv.COLOR_BGRA2BGR)

    def __doWork(self):
        loop_time = 0
        while True:
            try:
                fps = 1 / (time.time() - loop_time)
            except:
                pass
            if fps > 60:
                continue
            #print(f'Raw FPS {fps}', flush=True)
            loop_time = time.time()
            try:
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



cols = 384#288 #192 #384
rows = 216#162 #108 #216

sys.stdout = open( 1, "w", buffering = 999999 )
os.system("")

################    Console font stuff  ########################

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * LF_FACESIZE)]
    
font = CONSOLE_FONT_INFOEX()
font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
font.nFont = 12
font.dwFontSize.X = 5
font.dwFontSize.Y = 5

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
ctypes.windll.kernel32.SetCurrentConsoleFontEx(
        handle, ctypes.c_long(False), ctypes.pointer(font))

################    Console font stuff  ########################

ORDER = (' ', '.', "'", ',', ':', ';', 'c', 'l',
             'x', 'o', 'k', 'X', 'd', 'O', '0', 'K', 'N')
ASCII_GRADIENT_8 = " .-+o$#8"
ASCII_GRADIENT_32 = " `´¨·¸˜’:~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ"

print_set = ORDER

def print_array(input_ascii_array):
    #os.system('cls')
    #sys.stdout.write('\n'.join((''.join(row) for row in input_ascii_array)))
    print('\n'.join(''.join(" .',:;clxokXdO0KN"[c//(16)] for c in row) for row in input_ascii_array), end="")
    #sys.stdout.flush()

def convert_row_to_ascii(row):
    # 17-long
    #return tuple(#"\033[32m Testing\033[0m"#f"\u001b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    #            ORDER[np.uint16((np.uint16(rgb[0])+rgb[0]+rgb[1]+rgb[2]+rgb[2]+rgb[2])/6 / (255 / 16))]
    #            #+ f'{ColorRGB(*rgb).OFF}'
    #            for rgb in row)[::1]

    return tuple(ORDER[int(x / (255 / 16))] for x in row)[::-1]

def convert_to_ascii(input_grays):
    return tuple(convert_row_to_ascii(row) for row in input_grays)

os.system(f"mode con: cols={cols} lines={rows+1}\n")
os.system("set PROMPT= \n")
print("\x1b[?25l")






if __name__ == '__main__':
    names = []
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            n = win32gui.GetWindowText(hwnd)  
            if n:
                names.append(n)
    win32gui.EnumWindows(winEnumHandler, None)
    #print(names)

    cv.namedWindow("frame", cv.WINDOW_NORMAL)
    windowCap = WindowCapture([x for x in names if "Firefox" in x][0])

    while True:
        img = windowCap.GetLatestImage()
        if img is None:
            continue

        cv.imshow('frame', img)
        img = cv.resize(img, (cols, rows))
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        #img = cv.flip(img, 1)
        #converted = convert_to_ascii(img)
        #print_array(converted)
        print_array(img)
        print("\033[0;0H")
        sys.stdout.flush()

        if cv.waitKey(1) == ord('q'):
            break
