# -*- coding: utf-8 -*-
import time
from PIL import ImageGrab, Image
from base64 import b64encode
from io import BytesIO
from pymouse import PyMouse

m = PyMouse()

# 屏幕DPR
DPR = 1

# 好友pk
type = 'FRIEND_PK'
# 每日一答
# type = 'SELF_PK'

# 题目开始x,y
QUESTION_START_POS = (85, 770)
# 题目高度
QUESTION_HEIGT = 110
# 题目间距
QUESTION_MT = 20


class Click:
    def __init__(self, offsetx: int, offsety: int):
        self.bound = (0, 0, 414, 736)
        self.rpx = self._rpx2px(self.bound[2] - self.bound[0])
        self.offsetx = offsetx
        self.offsety = offsety

    # rpx转px
    def _rpx2px(self, base):
        ratio = base / 750
        def _rpx(rpx):
            return rpx * ratio / DPR
        return _rpx

    # 截图
    def _getCapture(self):
        img = ImageGrab.grab(self.bound)
        return img


    # base64
    def base64(self, img):
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img.close()

        b64_str = b64encode(buffer.getvalue())

        return b64_str

    # 获取答案在图片上的box位置
    def getPicBounds(self):
        list = []
        for index in range(0, 3):
            list.append((
                QUESTION_START_POS[0], 
                QUESTION_START_POS[1] + QUESTION_HEIGT * index + QUESTION_MT * index, 
                670, 
                QUESTION_START_POS[1] + QUESTION_HEIGT * (index + 1) + QUESTION_MT * index
            ))
        return list

    # 获取答案在机器上的box位置
    def getAnswerPostions(self, list):
        bounds = []
        positions = []
        for bound in list:
            s_bound = (
                self.rpx(bound[0]) + self.offsetx,
                self.rpx(bound[1]) + self.offsety,
                self.rpx(bound[2]) + self.offsetx,
                self.rpx(bound[3]) + self.offsety,
            )
            bounds.append(s_bound)
            positions.append(((s_bound[2] - s_bound[0]) / 2 + s_bound[0], (s_bound[3] - s_bound[1]) / 2 + s_bound[1]))
        
        return positions

    # 切割
    def _splitCapture(self, img):
        if(type == 'FRIEND_PK'):
            # 笔记本好友pk
            quesImg = img.crop((self.rpx(85), self.rpx(460 + 120), self.rpx(670), self.rpx(590 + 120)))
            ansImg = img.crop((self.rpx(85), self.rpx(750), self.rpx(670), self.rpx(1055 + 120)))
            
            # index = 1
            # for answerBox in self.getPicBounds():
            #     ansImgItem = img.crop((self.rpx(answerBox[0]), self.rpx(answerBox[1]), self.rpx(answerBox[2]), self.rpx(answerBox[3])))
            #     ansImgItem.save('output/images/ansImgItem{}.png'.format(index))
            #     index += 1


        if(type == 'SELF_PK'):
            # 笔记本每日一答
            quesImg = img.crop((self.rpx(85), self.rpx(460 - 20), self.rpx(670), self.rpx(590 - 20)))
            ansImg = img.crop((self.rpx(85), self.rpx(590 - 20), self.rpx(670), self.rpx(1055 - 20)))

        # img.save('output/images/all.png')
        # quesImg.save('output/images/quesImg.png')
        # ansImg.save('output/images/ansImg.png')

        return quesImg, ansImg
    
    
    def run(self, appImg, answers, rightAnswer):
        # img = self._getCapture()
        # img = Image.open('img/screenshot.png')
        img = appImg
        self.bound = (0, 0, img.size[0], img.size[1])
        self.rpx = self._rpx2px(self.bound[2] - self.bound[0])
        
        # print('imgSize', img.size)
        posList = self.getAnswerPostions(self.getPicBounds())

        rightAnswerIdx = answers.index(rightAnswer)

        if(rightAnswerIdx >= 0):
            rightPos = posList[rightAnswerIdx]
            m.move(rightPos[0], rightPos[1])
            m.click(rightPos[0], rightPos[1])
            # print('rightAnswerIdx: rightPos', rightAnswerIdx, rightPos)


        # return self._splitCapture(img)

cc = Click(0, 77)

# cc.run(None, None, None)

        


        

        
        

        



