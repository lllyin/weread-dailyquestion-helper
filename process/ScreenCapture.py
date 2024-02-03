# -*- coding: utf-8 -*-
from PIL import ImageGrab, Image
from base64 import b64encode
from io import BytesIO

# 小程序窗口屏幕坐标：左侧，顶部，宽度，高度
box_bound = (0, 0, 622, 1170)

# 好友PK：左侧比率，右侧比率，问题顶部比率，问题底部比率，答案底部比率
pk_rates = (0.1, 0.909, 0.414, 0.537, 0.824)
# 每日一答：左侧比率，右侧比率，问题顶部比率，问题底部比率，答案底部比率
yida_rates = (0.1, 0.909, 0.312, 0.404, 0.734)
# yida_rates = (0.1, 0.909, 0.313, 0.408, 0.735)

class ScreenCapture:
    def __init__(self, config: dict):
        self.mode = config.get('capture_mode') or 'MINI_APP'  # MINI_APP  JIE_TU
        self.type = config.get('game_type') or 'SELF_PK'  # SELF_PK   FRIEND_PK
        if(self.mode == 'JIE_TU'):
            # 截图顶点调试
            self.bound = (0, 90, 414, 736 + 80)
        else:
            # 笔记本小程序顶点截图
            self.bound = box_bound
       
        # self.bound = (50, 80, 414 + 50, 736 + 80)
        self.rpx = self._rpx2px(self.bound)

    # rpx转px
    def _rpx2px(self, box):
        width = box[2] - box[0]
        height = box[3] - box[1]
        def _rpx(left, right, top, bottom):
            return (left * width, top * height, right * width, bottom * height)
        return _rpx

    # 截图
    def _getCapture(self):
        img = ImageGrab.grab(self.bound)
        # img = Image.open('output/images/ques.png')
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
        if(self.type == 'FRIEND_PK'):
            # 笔记本好友pk
            quesImg = img.crop(self.rpx(*pk_rates[:3], pk_rates[-1]))
            # ansImg = img.crop(self.rpx(*pk_rates[:2], *pk_rates[-2:]))
        if(self.type == 'SELF_PK'):
            # 笔记本每日一答
            quesImg = img.crop(self.rpx(*yida_rates[:3], yida_rates[-1]))
            # ansImg = img.crop(self.rpx(*yida_rates[:2], *yida_rates[-2:]))

        # img.save('output/images/all.png')
        # quesImg.save('output/images/quesImg.png')
        # ansImg.save('output/images/ansImg.png')

        return quesImg, img
    
    
    def run(self):
        img = self._getCapture()
        return self._splitCapture(img)
        