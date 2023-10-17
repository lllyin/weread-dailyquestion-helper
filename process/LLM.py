# -*- coding: utf-8 -*-
import requests
import json
tpl = """
问题：{question}
选项：{options}
你是无所不知的百科问答小助手，请根据下面问题和选项，选出正确的选项。回复不要超过10个字，不要解释，不要回复其他任何内容。"""

json_req_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


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

    def zhipu(self, question, options):
        import zhipuai
        content = tpl.format(question=question, options='   '.join(options))
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
    

    def ernie(self, question, options):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + self.ernie_token
        content = tpl.format(question=question, options='   '.join(options))
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
        func = getattr(self, self.channel)
        return func(question, options)
    