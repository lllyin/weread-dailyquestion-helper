import ssl
from urllib import request, parse
from bs4 import BeautifulSoup
from util import getOCRConfig

ssl._create_default_https_context = ssl._create_unverified_context

config = getOCRConfig()

httpproxy_handler = request.ProxyHandler({
  'http': '127.0.0.1:1082',
  'https': '127.0.0.1:1082',
})
opener = request.build_opener(httpproxy_handler)

def search(wd):
  url = 'https://www.google.com/search?q={}'.format(parse.quote(wd))
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
      'host': 'www.google.com',
  }
  req = request.Request(url, headers=headers)
  # response = request.urlopen(req)
  response = opener.open(req)
  content = response.read().decode('utf-8')

  html_file = open('output/g_result.html', 'w')
  html_file.write('' + content)
  html_file.close()

  soup = BeautifulSoup(content, 'html.parser')
  html_text = soup.get_text()

  text_file = open('output/g_result.txt', 'w')
  text_file.write('' + html_text)
  text_file.close()


# search('在传真机中,识别图像和文字的小装置是?')
search('谁是第一个进入BA打球的中国人?')
# search('万_穿心')


