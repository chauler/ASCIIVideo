import numpy as np
import cv2 as cv
from threading import Thread

class CameraCapture:
    def __init__(self):
        self.__newestImage = np.array(np.zeros((100,100,1), dtype=np.uint8))
        self.cam = cv.VideoCapture(0)
        t1 = Thread(target=self.__doWork)
        t1.daemon = True
        t1.start()

    def __doWork(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                print("Error getting webcam image")
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            self.__newestImage = frame

    def GetLatestImage(self):
        return self.__newestImage