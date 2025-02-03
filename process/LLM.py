import base64
import json  
from openai import OpenAI

client = OpenAI(
    api_key="您的 APIKEY", # 从https://cloud.siliconflow.cn/account/ak获取
    base_url="https://api.siliconflow.cn/v1"
)
def getResponse(base64img):
    response = client.chat.completions.create(
            model="Qwen/Qwen2-VL-72B-Instruct",
            messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64img}",
                            "detail":"low"
                        }
                    },
                    {
                        "type": "text",
                        "text": "首先请识别图中文字。如果该图片的内容为问答题，则根据图中问题及所给选项，选择并只输出正确的答案选项，无需输出其他额外信息；否则请输出识别的图中文字即可"

                    }
                ]
            }],
            stream=True
    )

    strdata = ""
    for chunk in response:
        chunk_message = chunk.choices[0].delta.content
        strdata = strdata + " " + chunk_message
        #print(chunk_message, end='', flush=True)
    print("strdata")
    
    return strdata
