# -*- coding: utf-8 -*-
import json
import time
import re
import sys
import logging

from PIL import ImageChops
from process.LLM import getResponse

from process.ScreenCapture import ScreenCapture
from process.OCR import OCR
from process.Query import Query
from process.Click import Click
from process.logger import logger


cc = Click(0, 40)

END_WORDS_DICT = {
  "VICTORY": True
}

def isSame(imgA, imgB):
    if imgA is None or imgB is None:
        return False
    diff = ImageChops.difference(imgA.convert('RGB'), imgB.convert('RGB'))
    if diff.getbbox():
        return False
    return True


def getOCRConfig():
    with open("./config.json", "r", encoding="utf-8") as fp:
        return json.load(fp)


if __name__ == "__main__":
    sc = ScreenCapture()
    Img = None

    while True:
        tmpImg = sc.run()
        # print(tmpQuesImg)
        # print(tmpAnswImg)

        if not isSame(Img, tmpImg):
            Img = tmpImg
            answ = getResponse(Img)

            # 如果匹配victory｜defeat退出程序
            if re.search('victory|defeat|defert|自动匹配|排行榜|看广告', "".join(answ), flags=re.I):
                sys.exit()
            
            logger.info("\033[1;47;32m正确答案: %s\033[0m", answ)
            #cc.run(appImg, answ, rightAnswer)
            logger.info('-----------------')
            logger.info('')

        time.sleep(1)
