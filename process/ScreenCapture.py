# -*- coding: utf-8 -*-
from PIL import ImageGrab
from base64 import b64encode
from io import BytesIO

# mode = 'JIE_TU'
mode = 'MINI_APP'

type = 'FRIEND_PK'
# type = 'SELF_PK'

class ScreenCapture:
    def __init__(self):
        # self.hwnd = win32gui.FindWindow(0, "微信读书")
        # if self.hwnd == 0:
        #     raise Exception("没有找到'微信读书'小程序")
        if(mode == 'JIE_TU'):
            # 截图顶点调试
            self.bound = (0, 90, 414, 736 + 80)
        else:
            # 笔记本小程序顶点截图
            self.bound = (0, 40, 414, 736 + 40)
       
        # self.bound = (50, 80, 414 + 50, 736 + 80)
        self.rpx = self._rpx2px(self.bound[2] - self.bound[0])

    # rpx转px
    def _rpx2px(self, base):
        ratio = base / 750
        def _rpx(rpx):
            return rpx * ratio
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
    
    # 切割
    def _splitCapture(self, img):
        if(type == 'FRIEND_PK'):
            # 笔记本好友pk
            quesImg = img.crop((self.rpx(85), self.rpx(460 + 120), self.rpx(670), self.rpx(590 + 120)))
            ansImg = img.crop((self.rpx(85), self.rpx(590 + 120), self.rpx(670), self.rpx(1055 + 120)))
        if(type == 'SELF_PK'):
            # 笔记本每日一答
            quesImg = img.crop((self.rpx(85), self.rpx(460 - 20), self.rpx(670), self.rpx(590 - 20)))
            ansImg = img.crop((self.rpx(85), self.rpx(590 - 20), self.rpx(670), self.rpx(1055 - 20)))

        # img.save('output/images/all.png')
        # quesImg.save('output/images/quesImg.png')
        # ansImg.save('output/images/ansImg.png')

        return quesImg, ansImg, img
    
    
    def run(self):
        img = self._getCapture()
        return self._splitCapture(img)
        