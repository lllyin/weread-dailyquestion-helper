# -*- coding: utf-8 -*-
import io
import base64
import logging
from typing import *
from io import StringIO
from aip import AipOcr
from huaweicloudsdkcore.exceptions.exceptions import ConnectionException, RequestTimeoutException, \
    ServiceResponseException, ClientRequestException
from huaweicloudsdkocr.v1.region.ocr_region import OcrRegion
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkocr.v1 import OcrClient


class OCR:

    def __init__(self, config):
        self.config = config
        self.channel = config.get('ocr_channel') or 'baidu'
        self.client = None
        self.ques_end_rate = 0.261
        # 问题底部结束位置占整个图片的比率
        self.ques_end = 0

    def _pil2bin(self, pilObj):
        bin = io.BytesIO()
        pilObj.save(bin, format='PNG')
        return bin.getvalue()

    def _baidu(self, img):
        if not self.client:
            self.client = AipOcr(self.config["APP_ID"], self.config["API_KEY"], self.config["SECRET_KEY"])
        rsp = self.client.general(img, dict(recognize_granularity='small'))
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
    
    def _volc(self, img):
        action = 'OCRNormal'
        if not self.client:
            import os
            os.environ['VOLC_ACCESSKEY'] = self.config["API_KEY"]
            os.environ['VOLC_SECRETKEY'] = self.config["SECRET_KEY"]
            from volcengine.visual.VisualService import VisualService
            self.client = VisualService()
            self.client.set_api_info(action, '2020-08-26')
        bodys = dict(image_base64=str(base64.b64encode(img), encoding='utf-8'))
        response = self.client.ocr_api(action, bodys)
        if response.get('code') != 10000:
            raise ValueError(f'volc ocr fail: {response}')
        rsp_data = response['data']
        if not rsp_data:
            raise ValueError(f'volc ocr empty: {response}')
        ques_bd = StringIO()
        options = []  # 记录所有选项
        vert_top, horz_end = 0, 0
        blocks = rsp_data.get('line_texts')
        polygons = rsp_data['polygons']
        for i, text in enumerate(blocks):
            box = polygons[i]  # [左上, 右上, 右下, 左下]
            coords = [p for p in sort_box(box)]
            if coords[0][1] > self.ques_end:
                # 达到了选项部分
                options.append(text)
                continue
            vert_top, horz_end = self._update_ocr_block(ques_bd, coords, text, vert_top, horz_end)
        ques_bd.write('\n')
        return ques_bd.getvalue(), options

    def _update_ocr_block(self, ques_bd: StringIO, coords: List[List], text: str, vert_top, horz_end):
        top = (coords[0][1] + coords[1][1]) / 2
        left = (coords[0][0] + coords[3][0]) / 2
        width = (coords[1][0] + coords[2][0] - coords[0][0] - coords[3][0]) / 2
        height = (coords[2][1] + coords[3][1] - coords[0][1] - coords[1][1]) / 2
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
        return vert_top, horz_end

    def _huawei(self, img):
        if not self.client:
            credentials = BasicCredentials(self.config["API_KEY"], self.config["SECRET_KEY"])
            self.client = OcrClient.new_builder(OcrClient).with_credentials(credentials).with_region(OcrRegion.CN_NORTH_4).build()
        from huaweicloudsdkocr.v1 import RecognizeGeneralTextRequest, GeneralTextRequestBody
        req_paras = dict(
            detect_direction=True,
            image=str(base64.b64encode(img), encoding='utf-8')
        )
        request = RecognizeGeneralTextRequest()
        request.body = GeneralTextRequestBody(**req_paras)
        try:
            response = self.client.recognize_general_text(request)
        except (ConnectionException, RequestTimeoutException, AttributeError) as e:
            err_msg = str(e)
            if isinstance(e, AttributeError) and err_msg.find('ProtocolError') < 0:
                # 连接中断异常表现为AttributeError: 'ProtocolError' object has no attribute 'reason'
                raise e
            logging.warning(f'{self.name} error: {self.img_dfs} {e}')
            return '', []
        except ServiceResponseException as e:
            logging.error(f'{self.name} service error: {self.img_dfs} {e}')
            return '', []
        if not response:
            return '', []
        if hasattr(response, 'error_code'):
            logging.exception(f'{self.name}: {self.img_dfs} ocr error: {response}')
            return '', []
        rsp_data = response.result
        if not rsp_data:
            return '', []
        return self._parse_huawei(rsp_data)
    
    def _parse_huawei(self, rsp):
        # 华为能识别旋转角度，但返回的坐标都是基于原始图片的。
        if not rsp.words_block_list:
            return '', []
        ques_bd = StringIO()
        options = []  # 记录所有选项
        vert_top, horz_end = 0, 0
        for item in rsp.words_block_list:
            coords = [p for p in sort_box(item.location)]
            text = item.words
            if coords[0][1] > self.ques_end:
                # 达到了选项部分
                options.append(text)
                continue
            vert_top, horz_end = self._update_ocr_block(ques_bd, coords, text, vert_top, horz_end)
        ques_bd.write('\n')
        return ques_bd.getvalue(), options

    def run(self, img):
        self.ques_end = img.height * self.ques_end_rate
        imgBin = self._pil2bin(img)
        if self.channel == 'baidu':
            return self._baidu(imgBin)
        elif self.channel == 'huawei':
            return self._huawei(imgBin)
        elif self.channel == 'volc':
            return self._volc(imgBin)
        else:
            raise ValueError(f'invalid ocr channel: {self.channel}')


def sort_box(pts: List[Tuple[float, float]]):
    '''
    对四点坐标排序，按左上，右上，右下，左下的顺序返回
    :param pts: [(x, y), (x, y)]
    :return:
    '''
    # sort the points based on their x-coordinates
    xpts = sorted(pts, key=lambda x: x[0])

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    left_pts, right_pts = xpts[:2], xpts[2:]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    (tl, bl) = sorted(left_pts, key=lambda x: x[1])

    (tr, br) = sorted(right_pts, key=lambda x: x[1])

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return [tl, tr, br, bl]
