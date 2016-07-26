# -*- coding: utf-8 -*-
import requests
from HTMLParser import HTMLParser
import sys
import os
import urllib
import re
import threading
reload(sys)
sys.setdefaultencoding('utf8')

# 项目描述
# 爬取Python贴吧里面用户名及头像图片信息。爬取网页链接:http://tieba.baidu.com/f?kw=python&fr=ala0&tpl=5，
# 只需要爬取该贴吧链接里面的头像即可,用户名作为头像图片的名称。

## 获取tag属性值
def _attr(attrs, attrname):
    for attr in attrs:
        if attr[0] == attrname:
            return attr[1]
    return None


##step1.进入python贴吧url,获取每个帖子的链接即href的值,然后通过href值组成每个帖子的完整路径
class HrefParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_div = False
        self.in_a = False
        self.current = ''
        self.href_list = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and ((_attr(attrs, 'class') == 'threadlist_title pull_left j_th_tit  member_thread_title_frs ') or (
            _attr(attrs, 'class') == 'threadlist_title pull_left j_th_tit ')):
            self.in_div = True
        if tag == 'a' and self.in_div:
            self.in_a = True
        if self.in_a and self.in_div:
            self.current = _attr(attrs, 'href')
            self.href_list.append(self.current)

    def handle_endtag(self, tag):
        if tag == 'div':
            self.in_div = False
        if tag == 'a':
            self.in_a = False

#获取所有href
def get_href():
    url = 'http://tieba.baidu.com/f?kw=python&fr=ala0&tpl=5'
    r = requests.get(url)
    p = HrefParser()
    p.feed(r.content)
    # print p.href_list
    # print len(p.href_list)
    return p.href_list

#获取每个帖子的url
def get_tiezi_full_url(url):
    return 'http://tieba.baidu.com'+url

##step2: 打开链接中的url,获取图片src和用户名
class SrcParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_a = False
        self.in_img = False
        self.current = {}
        self.src_url_list = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and _attr(attrs, 'class') == 'p_author_face ':
            self.in_a = True
        if tag == 'img' and self.in_a:
            self.in_img = True
        if self.in_a and self.in_img:
            self.current['username'] = _attr(attrs, 'username')
            self.current['src'] = _attr(attrs, 'src')
            self.src_url_list.append(self.current)
            self.current = {}

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_a = False
        if tag == 'img':
            self.in_img = False

#获取所有图片链接src
def get_src(href_url):
    url = href_url
    r = requests.get(url)
    p = SrcParser()
    p.feed(r.content)
    return p.src_url_list

#下载图片
def download_img(username,src):
    if not os.path.isdir('images'):
        os.mkdir('images')
    fname = 'images'+'/'+username+'.jpg'
    urllib.urlretrieve(src,fname)

if __name__ == '__main__':
    s = get_href()
    # print s
    for i in range(0,len(s)):
        b = get_tiezi_full_url(s[i])
        # print b
        c = get_src(b)
        print c
        for k in c:
            print k
            download_img(k['username'],k['src'])


