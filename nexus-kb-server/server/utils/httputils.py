import requests
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'

def get_webpage_text(url):
  headers = {
    'user-agent': USER_AGENT
  }
  try:
    r = requests.get(url, timeout=30, headers=headers, allow_redirects=False)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text
  except:
    return None
def get_webpage_title(url):
  text = get_webpage_text(url)
  if (text is None):
    return None
  # 使用BeautifulSoup解析HTML
  soup = BeautifulSoup(text, 'html.parser')
  # 提取<title>标签中的文本
  title_tag = soup.find('title')
  if title_tag:
    # 如果找到了<title>标签，提取其文本内容
    title = title_tag.string
    return title
  else:
    return None