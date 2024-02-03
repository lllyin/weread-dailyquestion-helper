# -*- coding: utf-8 -*-
import time
import ssl
from functools import reduce
from urllib import request, parse
from bs4 import BeautifulSoup
from process.util import getOCRConfig

ssl._create_default_https_context = ssl._create_unverified_context

config = getOCRConfig()
SEARCH_ENGINE = config['search_engine']

if(SEARCH_ENGINE == 'GOOGLE' and config.get('proxy')):
    httpproxy_handler = request.ProxyHandler(config['proxy'])
    opener = request.build_opener(httpproxy_handler)


def del_useless_elts(root, del_ptns):
    for ptn in del_ptns:
        elts = root.select(ptn)
        if not elts:
            continue
        for elt in elts:
            elt.decompose()


class Query:

    def _getKnowledge(self, question):
        if(SEARCH_ENGINE == 'GOOGLE'):
            url = 'https://www.google.com/search?q={}'.format(parse.quote(question))
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'host': 'www.google.com',
            }
            del_ptns = ['.yp1CPe', '.lhLbod', '.TbwUpd.ojE3Fb', '.oIk2Cb', '.ULSxyf > .MjjYud > .EyBRub', '#rhs', '.YB4h9']
        else:   
            url = 'https://www.baidu.com/s?wd={}'.format(parse.quote(question))
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'host': 'www.baidu.com',
                'Cookie': config['BAIDU_COOKIE'],
            }
            del_ptns = ['.cos-row', 'div.tts', '.new-pmd .c-gap-top-xsmall', '.new-pmd .c-gap-top-mini', '.new-pmd .c-color-gray2', 'a.c']
        req = request.Request(url, headers=headers)
        start = time.time()
        response = opener.open(req) if SEARCH_ENGINE == 'GOOGLE' else (request.urlopen(req))
        content = response.read().decode('utf-8')
        cost = time.time() - start
        # print(f'query cost: {cost:.3}s')
        root = BeautifulSoup(content, 'html.parser')
        # 先删除无关的部分，优化显示文本
        del_useless_elts(root, del_ptns)
        # 只保留两个结果：第一个搜索结果，以及高亮部分占比最多的结果
        if SEARCH_ENGINE == 'GOOGLE':
            first_res = root.select_one('.ULSxyf > .MjjYud .EyBRub')
            first_res = first_res.text if first_res else None
            items = root.select('.MjjYud')
        else:
            items = root.select('#content_left .c-container')
            first_res = items[0].text if items else None
            items = items[1:]
        matches = []
        result = []
        for item in items:
            em_list = item.select('em')
            if not em_list:
                continue
            result.append(item.text)
            if not first_res:
                first_res = item.text
                continue
            em_len = sum(len(em.text) for em in em_list)
            item_text = item.text
            matches.append((item_text, em_len / len(item_text)))
        matches = sorted(matches, key=lambda x: x[1], reverse=True)
        if first_res:
            print(first_res.strip())
            print('-' * 70)
        if matches:
            print(matches[0][0].strip())
            print('-' * 70)
        if not result:
            with open('D:/weread_query.html', 'w', encoding='utf-8') as file:
                file.write(content)
            print('没有搜索结果，请检查D:/weread_query.html')
        return '\n\n'.join(result)

    def _query(self, knowledge, answers):
        freq = [knowledge.count(item) + 1 for item in answers]
        rightAnswer = None
        hint = None

        if freq.count(1) == len(answers):
            freqDict = {}
            for item in answers:
                for char in item:
                    if char not in freqDict:
                        freqDict[char] = knowledge.count(item)
            for index in range(len(answers)):
                for char in answers[index]:
                    freq[index] += freqDict[char]
            rightAnswer = answers[freq.index(max(freq))]
        else:
            rightAnswer = answers[freq.index(max(freq))]
            threshold = 50 # 前后50字符
            hintIndex = max(knowledge.index(rightAnswer), threshold)
            hint = ''.join(knowledge[hintIndex - threshold : hintIndex + threshold].split())
        
        sum = reduce(lambda a,b : a+b, freq)
        return [f / sum for f in freq], rightAnswer, hint


    def run(self, question, answers):
        if(len(answers) <= 0):
            return [], None, None
        knowledge = None
        while(knowledge is None):
            knowledge = self._getKnowledge(question)
        try:
            freq, rightAnswer, hint = self._query(knowledge, answers)
        except Exception as e:
            print('出现异常', e)
            freq, rightAnswer, hint = [], None, None
        return freq, rightAnswer, hint

        
