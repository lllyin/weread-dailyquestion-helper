# -*- coding: utf-8 -*-
import base64
import io
from PIL import ImageGrab,Image
from base64 import b64encode
from io import BytesIO
import os
import pygetwindow as gw
import pyautogui
import time

# mode = 'JIE_TU'
mode = 'MINI_APP'

type = 'FRIEND_PK'
# type = 'SELF_PK'

class ScreenCapture:
    def __init__(self):
        if(mode == 'JIE_TU'):
            # 截图顶点调试
            self.bound = (0, 90, 414, 736 + 80)
        else:
            # 笔记本小程序顶点截图
            self.bound = (0, 40, 414, 736 + 40)
       
        # self.bound = (50, 80, 414 + 50, 736 + 80)
        self.rpx = self._rpx2px(self.bound[2] - self.bound[0])
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.join(self.current_dir, '..', 'img', 'test.png')
        self.image_path2 = os.path.join(self.current_dir, '..', 'tmp', 'test.png')

    # rpx转px
    def _rpx2px(self, base):
        ratio = base / 750
        def _rpx(rpx):
            return rpx * ratio
        return _rpx

    # 截图
    def _getCapture(self):
        img = ImageGrab.grab(self.bound)
        img.save('output/images/test.png')
        return img

    def take_screenshot_of_window(self,window_title):
        # 找到窗口
        window = gw.getWindowsWithTitle(window_title)
        if not window:
            return "窗口未找到"
        window = window[0]  # 假设只有一个窗口匹配
        window.activate()
        # 让窗口有时间激活
        time.sleep(0.5)
        # 获取窗口的屏幕坐标
        window_position = window.left, window.top, window.width, window.height

        # 屏幕截图
        screenshot = pyautogui.screenshot(region=window_position)
        # 保存截图到文件
        screenshot.save(self.image_path2)
        return screenshot

    # base64
    def base64(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_encoded_data = base64.b64encode(image_file.read())
            base64_encoded_image = base64_encoded_data.decode('utf-8')
        return f"data:image/png;base64,{base64_encoded_image}"
    
    def base64_online(self,img):
        with io.BytesIO() as buffer:
            img.save(buffer, format='PNG')
            img_binary = b64encode(buffer.getvalue())
        
        # 对二进制数据进行 base64 编码
        base64_encoded_data = base64.b64encode(img_binary)
        # 将 base64 编码的二进制数据转换为字符串
        base64_encoded_image = base64_encoded_data.decode('utf-8')

        return base64_encoded_image

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
        img = self.take_screenshot_of_window("微信读书")
        #img = self._test()
        #return self.base64(self.image_path)
        return img
        