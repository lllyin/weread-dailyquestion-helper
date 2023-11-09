# -*- coding: utf-8 -*-
import json
import time
import re
import sys

from PIL import ImageChops

from process.ScreenCapture import ScreenCapture
from process.OCR import OCR
from process.Query import Query
from process.Click import Click
from process.LLM import LLM

cc = Click(0, 40)

END_WORDS_DICT = {
  "VICTORY": True
}

re_exit = re.compile(r'victory|defeat|defert|自动匹配|排行榜|邀请好友|积分商城|体验卡|续命卡|再来一局|炫耀一下|看广告', flags=re.I)

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


def run_main():
    config = getOCRConfig()

    sc = ScreenCapture(config)
    ocr = OCR(config["APP_ID"], config["API_KEY"], config["SECRET_KEY"])
    # query = Query()
    llm = LLM(config)

    quesImg, answImg = None, None
    tmpQuesText = ''

    while True:
        tmpQuesImg, appImg = sc.run()

        # print(tmpQuesImg)
        # print(tmpAnswImg)

        if not isSame(quesImg, tmpQuesImg):
            print('发现新图片，OCR识别文字...')
            quesImg, appImg = tmpQuesImg, appImg
            ques, options = ocr.run(quesImg)

            # 如果匹配victory｜defeat退出程序
            if re_exit.search("".join(options)):
                print('问答结束，退出...')
                sys.exit()

            if (len(ques) > 0 and (tmpQuesText != ques)):
                tmpQuesText = ques
                print("问题: {}选项：{}".format(ques, options))
                
                result = llm.run(ques, options)

                print('-----------------')
                print(f'AI回答: {result}')
                # cc.run(appImg, answ, rightAnswer)
                print('-----------------')
                print()

        time.sleep(0.3)


def test_ai():
    config = getOCRConfig()
    llm = LLM(config)
    ques = '朝露  至'
    options = ['磕', '堪']
    result = llm.run(ques, options)
    print(ques, options)
    print(result)


if __name__ == "__main__":
    run_main()
    # test_ai()
