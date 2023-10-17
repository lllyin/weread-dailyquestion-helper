# -*- coding: utf-8 -*-
from aip import AipOcr
import io

class OCR:

    def __init__(self, appId, apiKey, secretKey):
        self.client = AipOcr(appId, apiKey, secretKey)
        self.ques_end_rate = 0.261
        # 问题底部结束位置占整个图片的比率
        self.ques_end = 0

    def _pil2bin(self, pilObj):
        bin = io.BytesIO()
        pilObj.save(bin, format='PNG')
        return bin.getvalue()

    def _ocr(self, img):
        self.ques_end = img.height * self.ques_end_rate
        imgBin = self._pil2bin(img)
        return self.client.general(imgBin, dict(recognize_granularity='small'))

    def run(self, quesImg):
        rsp = self._ocr(quesImg)
        # print(ques)
        # answ = self._ocr(answImg)
        return self.get_ques_text(rsp)

    def get_ques_text(self, rsp: dict):
        from io import StringIO
        ques_bd = StringIO()
        options = []  # 记录所有选项
        vert_top, horz_end = 0, 0
        for item in rsp['words_result']:
            if item['location']['top'] > self.ques_end:
                # 达到了选项部分
                options.append(item['words'])
                continue
            for c in item['chars']:
                text = c['char']
                if not text.strip():
                    continue
                loc = c['location']
                top, left, width, height = loc['top'], loc['left'], loc['width'], loc['height']
                if vert_top > 0 and top - vert_top > height * 0.8:
                    ques_bd.write('\n')
                    horz_end = -1
                if horz_end > 0:
                    blank_num = (left - horz_end) / width > 0.8
                    if blank_num:
                        ques_bd.write('  ' * blank_num)
                ques_bd.write(text)
                vert_top = top
                horz_end = left + width
            ques_bd.write('\n')
        return ques_bd.getvalue(), options
