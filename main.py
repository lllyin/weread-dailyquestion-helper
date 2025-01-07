# -*- coding: utf-8 -*-
import json
import time
import re
import sys
import logging

from PIL import ImageChops

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
    config = getOCRConfig()

    sc = ScreenCapture()
    ocr = OCR(config["APP_ID"], config["API_KEY"], config["SECRET_KEY"])
    query = Query()

    quesImg, answImg = None, None
    tmpQuesText = ''

    while True:
        tmpQuesImg, tmpAnswImg, appImg = sc.run()

        # print(tmpQuesImg)
        # print(tmpAnswImg)

        if not isSame(quesImg, tmpQuesImg):
            quesImg, answImg, appImg = tmpQuesImg, tmpAnswImg, appImg
            ques, answ = ocr.run(quesImg, answImg)

            # 如果匹配victory｜defeat退出程序
            if re.search('victory|defeat|defert|自动匹配|排行榜|看广告', "".join(answ), flags=re.I):
                sys.exit()

            if (len(ques) > 0 and (tmpQuesText != ques)):
                tmpQuesText = ques
                
                freq, rightAnswer, hint = query.run(ques, answ)

                if(rightAnswer is not None):
                    logger.info("问题: %s", ques)
                    logger.info("\033[1;47;32m正确答案: %s\033[0m", rightAnswer)
                    freqText = ''
                    for index in range(len(freq)):
                        freqText += (answ[index] + ' :' + str(round(100 * freq[index], 1)) + '%    ')
                    logger.info('概率: %s', freqText)
                    logger.info('依据: %s', hint)
                    cc.run(appImg, answ, rightAnswer)
                    logger.info('-----------------')
                    logger.info('')

        time.sleep(0.1)
