# -*- coding: utf-8 -*-
import time
from PIL import ImageGrab, Image
from base64 import b64encode
from io import BytesIO
import pyautogui
import os

# 屏幕DPR
DPR = 2

_region = (0, 40, 420, 750)
REGION = tuple([v * 2 for v in _region])

cwd = os.getcwd()
btnBox = os.path.join(cwd, 'img/btnBox.png')

# sc = pyautogui.screenshot(region = REGION)
# sc.show()

class Click:
    def __init__(self, offsetx: int, offsety: int):
        self.offsetx = offsetx
        self.offsety = offsety

    # 对找到的location去重
    def unify(self, locations):
        dict = {}
        for location in locations:
            top = location.top
            dict[top] = location
        
        return list(dict.values())
    
    
    def run(self, appImg, answers, rightAnswer):
        locations = pyautogui.locateAllOnScreen(btnBox, region=REGION, confidence=0.9)
        locations = [v for v in locations]

        unifyLocations = self.unify(locations)
        locationsLen = len(unifyLocations)

        rightAnswerIdx = answers.index(rightAnswer)

        try:
            if rightAnswerIdx >= 0 and locationsLen > 0 and locationsLen < 4:
                rightLocation = unifyLocations[rightAnswerIdx]
                x, y = pyautogui.center(rightLocation)

                pyautogui.click(x / DPR, y / DPR)
                time.sleep(0.05)
                pyautogui.click(x / DPR, y / DPR)
            else:
                print('--无法自动化操作--', rightAnswerIdx, unifyLocations, locations)
        except:
            print('自动化报错：', rightAnswerIdx, unifyLocations, locations)



        # return self._splitCapture(img)

# cc = Click(0, 77)

# cc.run(None, None, None)

        


        

        
        

        



