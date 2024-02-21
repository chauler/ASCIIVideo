import os
import subprocess as sp
import sys
import time
import cv2 as cv
import ctypes
import io

import numpy as np

sys.stdout = open( 1, "w", buffering = 300000 )

os.system("")

width = 384
height = 216

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

def print_array(input_ascii_array):
    os.system('cls')
    sys.stdout.write('\n'.join((''.join(row) for row in input_ascii_array)))
    sys.stdout.flush()

def convert_row_to_ascii(row):
    # 17-long
    #return tuple(#"\033[32m Testing\033[0m"#f"\u001b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    #            ORDER[np.uint16((np.uint16(rgb[0])+rgb[0]+rgb[1]+rgb[2]+rgb[2]+rgb[2])/6 / (255 / 16))]
    #            #+ f'{ColorRGB(*rgb).OFF}'
    #            for rgb in row)[::1]

    return tuple(ORDER[int(x / (255 / 16))] for x in row)[::-1]

def convert_to_ascii(input_grays):
    return tuple(convert_row_to_ascii(row) for row in input_grays)

os.system(f"mode con: cols={100} lines={100}\n")
os.system("set PROMPT= \n")

frame_rate = 27
prev = 0

cv.namedWindow("frame", cv.WINDOW_NORMAL)
#cv.setWindowProperty("frame", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

cap = cv.VideoCapture(0)

while cap.isOpened():
    time_elapsed = time.time() - prev
    res, image = cap.read()
# 
    if time_elapsed > 1./frame_rate:
    ###if True:
        prev = time.time()
# 
# 
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting.")
            break
        ###frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ###frame = cv.Canny(frame, 50, 150)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.flip(frame, 1)
        cv.imshow('frame', frame)
        frame = cv.resize(frame, (width, height))
# 
        converted = convert_to_ascii(frame)
        print_array(converted)
# 
    if cv.waitKey(1) == ord('q'):
        break
    if cv.waitKey(1) == ord('w'):
        os.system(f"mode con: cols={width} lines={height}\n")
# 
cap.release()
#out.release()
cv.destroyAllWindows()

WIDE_MAP = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}
WIDE_MAP[0x20] = 0x3000

def widen(s):
    """
    Convert all ASCII characters to their full-width counterpart.
    
    >>> print widen('test, Foo!')
    ｔｅｓｔ，　Ｆｏｏ！
    >>> 
    """
    return s.translate(WIDE_MAP)

def InitCamera():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Cannot open camera")
     
    def ReadCam():
        res, img = cap.read()
        after(16, ReadCam)

    ReadCam()
    return cap