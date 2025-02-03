# 微信读书每日一答辅助

## 功能描述
简单的说就是每隔一段时间截张图，然后输入到ai多模态模型中进行结果获取。

如果用Qwen2-VL-72B-Instruct大约每日答题单轮次(12道题)耗费约0.05 rmb左右浮动，或者使用其他可以图片理解的模型；当然也可以用自己本地部署，不过这样得稍微改一下LLM.py文件

## 配置环境
- Python 3.8.x
- 微信windows版  
- [硅基流动](https://cloud.siliconflow.cn/)

## 原理
1. 截图
2. 扔给AI识别并回答
3. (可选)自动寻找答案位置并作答
5. 循环执行1，2，3

## 使用方法

1. 登陆硅基流动，并生成复制API Key
```shell
#windows cmd
setx API_SILICON_KEY "your_value"
```
2. 配置conda环境
```shell
conda env create -f environment.yml
pip install -r requirements.txt
```
3. 用**电脑**打开微信读书小程序，并**保持在最前**，且不要被遮挡
4. 运行根目录下的main.py
5. 进入每日一答页面开始答题，隔2s控制台就会输出结果,觉得太长可以改短


---

仅供学习参考，这玩意正确率目测80-90%，也不是标准答案，不能保证完全正确。

## 致谢
[@maotoumao](https://github.com/maotoumao)
[@lllyin](https://github.com/lllyin)