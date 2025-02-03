# -*- coding: utf-8 -*-
import base64
import io
import json
import os
import time
import re
import sys
import logging
from PIL import Image, ImageChops
from process.LLM import getResponse
from process.ScreenCapture import ScreenCapture
from process.Click import Click
from process.logger import logger
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, 'tmp', 'test.png')
threshold = 90

END_WORDS_DICT = {
  "VICTORY": True
}

def isSame(imgA, imgB):
    if imgA is None or imgB is None:
        return False
    diff = ImageChops.difference(imgA.convert('RGB'), imgB.convert('RGB'))
    diff_array = np.array(diff)
    # 计算非零像素的数量
    non_zero_pixels = np.sum(diff_array)   
    # 计算图像的总像素数量
    total_pixels = imgA.size[0] * imgA.size[1]
    # 计算相似度百分比
    similarity_percentage = ((total_pixels - non_zero_pixels) / total_pixels) * 100
    print(f"相似度: {similarity_percentage:.2f}%")
    
    if similarity_percentage >= threshold:
        return True
    else:
        return False


def getOCRConfig():
    with open("./config.json", "r", encoding="utf-8") as fp:
        return json.load(fp)

def test_base64(base64_string):
   
    # 将 base64 字符串解码为二进制数据
    image_binary = base64.b64decode(base64_string)
    # 使用 BytesIO 将二进制数据转换为图像对象
    buffered = io.BytesIO(image_binary)
    image = Image.open(buffered)
    # 保存还原的图像
    image.save("restored_image.jpg")
    # 显示还原的图像
    image.show()

if __name__ == "__main__":
    sc = ScreenCapture()
    Img = None

    while True:
        tmpImg = sc.run()
        # print(tmpQuesImg)
        # print(tmpAnswImg)

        if not isSame(Img, tmpImg):
            Img = tmpImg
            print("new pic")
            Imgb64 = sc.base64(image_path)
            #test_base64(Imgb64)
            answ = getResponse(Imgb64)

            # 如果匹配victory｜defeat退出程序
            if answ==None or re.search('victory|defeat|defert|自动匹配|排行榜|看广告', "".join(answ), flags=re.I):
                sys.exit()
            
            logger.info("\033[1;47;32m正确答案: %s\033[0m", answ)
            #cc.run(appImg, answ, rightAnswer)
            logger.info('-----------------')
            logger.info('')
        else:
            print("no new pic, wait 2 sec...")

        time.sleep(2)
        
