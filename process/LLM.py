# -*- coding: utf-8 -*-
import requests
import json
import re
chengyu_tpl = """
你精通中国古典成语和典故，请根据下面的问题和选项，选出正确的选项。回复不要超过10个字，不要解释，不要回复其他任何内容。
问题：{question}
{options}"""
tpl = """
问题：{question}
{options}
你是无所不知的问答助手，请根据上面的问题和选项，选出正确的选项。回复不要超过10个字，不要解释，不要回复其他任何内容。"""

json_req_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

reg_chi = re.compile(r'[\u4e00-\u9fa5]+')


def get_chr_nums(text: str):
    chi_num = sum(len(mat.group()) for mat in reg_chi.finditer(text))
    return chi_num


class LLM:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.channel = config.get('llm_channel') or 'ernie'
        if self.channel == 'ernie':
            self.ernie_token = None
            self.init_ernie()
        elif self.channel == 'zhipu':
            import zhipuai
            zhipuai.api_key = config['zhipu_key']

    def zhipu(self, content):
        import zhipuai
        res = zhipuai.model_api.invoke(
            model="chatglm_pro",
            prompt=[
                {"role": "user", "content": content},
            ]
        )
        if res['code'] != 200:
            return f'失败：{res["msg"]}'
        return '   '.join([item['content'] for item in res['data']['choices']])
    
    def init_ernie(self):
        api_key, api_secret = self.config['ernie_key'], self.config['ernie_secret']
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={api_secret}"
        
        response = requests.request("POST", url, headers=json_req_headers, data='')
        rsp_data = response.json()
        # print(rsp_data)
        self.ernie_token = rsp_data['access_token']
        if not self.ernie_token:
            raise ValueError(f'init ernie fail: {rsp_data}')
    

    def ernie(self, content):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + self.ernie_token
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        })
        response = requests.request("POST", url, headers=json_req_headers, data=payload)
        rsp_data = response.json()
        res_text = rsp_data.get('result')
        if not res_text:
            raise ValueError(f"文心接口错误：{rsp_data}")
        return res_text


    def run(self, question, options):
        ques_num = get_chr_nums(question)
        opt_nums = [get_chr_nums(t) for t in options]
        cur_tpl = tpl
        if ques_num == 3 and all(n == 1 for n in opt_nums):
            question = f'成语  {question}'
            cur_tpl = chengyu_tpl
        opt_text = '\n'.join(f'选项{i+1}: {t}' for i, t in enumerate(options))
        content = cur_tpl.format(question=question, options=opt_text)
        func = getattr(self, self.channel)
        return func(content)
    