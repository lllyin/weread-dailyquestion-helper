# -*- coding: utf-8 -*-
from aip import AipOcr
import io

class OCR:

    def __init__(self, appId, apiKey, secretKey):
        self.client = AipOcr(appId, apiKey, secretKey)

    def _pil2bin(self, pilObj):
        bin = io.BytesIO()
        pilObj.save(bin, format='PNG')
        return bin.getvalue()

    def _ocr(self, img):
        imgBin = self._pil2bin(img)
        return self.client.general(imgBin, dict(recognize_granularity='small'))

    def run(self, quesImg):
        ques = self._ocr(quesImg)
        # print(ques)
        # answ = self._ocr(answImg)
        ques = self.get_ques_text(ques)
        # answ = [item['words'] for item in answ['words_result']]

        return ques

    def get_ques_text(self, rsp: dict):
        from io import StringIO
        builder = StringIO()
        vert_top, horz_end = 0, 0
        for item in rsp['words_result']:
            for c in item['chars']:
                text = c['char']
                if not text.strip():
                    continue
                loc = c['location']
                top, left, width, height = loc['top'], loc['left'], loc['width'], loc['height']
                if vert_top > 0 and top - vert_top > height * 0.8:
                    builder.write('\n')
                    horz_end = -1
                if horz_end > 0:
                    blank_num = (left - horz_end) / width > 0.8
                    if blank_num:
                        builder.write('  ' * blank_num)
                builder.write(text)
                vert_top = top
                horz_end = left + width
            builder.write('\n')
        return builder.getvalue()
