#coding=utf8

import sys
import json
import time
import random

import requests
from bs4 import BeautifulSoup

import conf

to_int = lambda x: int(x) if x.isdigit() else 0

def crawl_result_page(url_base, pages_count):
    for page_num in xrange(1, pages_count + 1):
        print '%d / %d' % (page_num, pages_count)
        url = '%s/d%d' % (url_base, page_num)
        r = requests.get(url)
        html_doc = BeautifulSoup(r.text, 'lxml')
        xiaoqu_list = html_doc.find(id='house-lst').find_all('li')
        for xiaoqu in xiaoqu_list:
            xiaoqu_info = xiaoqu.find(class_='info-panel')
            xiaoqu_data = {
                'id': xiaoqu_info.h2.a.get('key'),
                'href': xiaoqu_info.h2.a.get('href'),
                'name': xiaoqu_info.h2.a.get('title')
            }
            x, y, _ = json.loads(
                xiaoqu_info.find(class_='col-1').find(class_='where').a.get('xiaoqu')
                           .replace("'", '"')
            )
            xiaoqu_data['coordinate'] = [x, y]
            xiaoqu_data['price'] = to_int(
                xiaoqu_info.find(class_='col-3').find(class_='price').find(class_='num').string
                           .strip('"').strip()
            )
            yield xiaoqu_data


def get_page_count(url):
    r = requests.get(url)
    html_doc = BeautifulSoup(r.text, 'lxml')
    return (to_int(html_doc.find(class_='list-head clear').h2.span.string.strip()) 
            / conf.NUM_ITEMS_PER_PAGE) + 1


def main():
    with open(sys.argv[1], 'w') as fout:
        for district1, district2, suffix in conf.DISTRICTS:
            print district2.decode('utf8')
            url = '%s/%s' % (conf.URL_PREFIX_XIAOQU, suffix)
            pages_count = get_page_count(url)
            for xiaoqu_data in crawl_result_page(url, pages_count):
                xiaoqu_data['district'] = district2.decode('utf8')
                fout.write('%s\n' % json.dumps(xiaoqu_data, ensure_ascii=False).encode('utf8'))
            time.sleep(2)

if __name__ == '__main__':
    main()