import win32gui
import cv2 as cv
import sys
import os
import ctypes
import argparse
from WindowCapture import WindowCapture
from CameraCapture import CameraCapture

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
font.dwFontSize.X = 7
font.dwFontSize.Y = 7

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
ctypes.windll.kernel32.SetCurrentConsoleFontEx(
        handle, ctypes.c_long(False), ctypes.pointer(font))

################    Console font stuff  ########################

def print_array(input_ascii_array):
    print('\n'.join(''.join(row) for row in input_ascii_array), end="")
    print("\x1b[?25l")
    print("\033[0;0H")
    sys.stdout.flush()

def convert_row_to_ascii(row):
    return tuple(print_set[int(x / (255 / (len(print_set)-1)))] for x in row)[::-1]

def convert_to_ascii(input_grays):
    return tuple(convert_row_to_ascii(row) for row in input_grays)

os.system("set PROMPT= \n")
print("\x1b[?25l")

def Parse_Args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--window', type=str, help='optional window name')
    parser.add_argument('--input', type=str, choices=['screen', 'camera'], default='camera')
    parser.add_argument('--charset', type=int, default=16, choices=[8, 16, 32], help='optional charset to use')
    args = parser.parse_args()
    if args.input == "screen" and args.window == None:
        print("Please specify a window name if using screen input")
        sys.exit()
    return args

if __name__ == '__main__':
    charsets = {
        8: " .-+o$#8",
        16: " .',:;clxokXdO0KN",
        32: " `´¨·¸˜’:~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ",
    }
    args = Parse_Args()
    print_set = charsets[args.charset]
    names = []
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            n = win32gui.GetWindowText(hwnd)  
            if n:
                names.append(n)
    win32gui.EnumWindows(winEnumHandler, None)

    videoFeed = CameraCapture() if args.input == "camera" else WindowCapture([x for x in names if args.window in x and 'cmd' not in x][0])

    while True:
        img = videoFeed.GetLatestImage()
        if img is None:
            continue
        cols, rows = os.get_terminal_size()
        img = cv.resize(img, (cols, rows-2))
        converted = convert_to_ascii(img)
        print_array(converted)
        if cv.waitKey(1) == ord('q'):
            break