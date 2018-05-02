import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import multiprocessing
import logging
from params import *


def get_sections(headers, category_url):
    """
    根据category_url获取每个章节的title和对应的url
    :param headers: 请求头 dict
    :param category_url: 目录url str
    :return: 章节列表 每一项为一个章节dict，{'title': title, 'url': url}
    """
    # 爬取网页内容
    try:
        r = requests.get(catagory_url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
    except:
        print(r.status_code)
    # 解析章节列表
    sections_url = []
    soup = BeautifulSoup(r.text, 'lxml')
    sections = soup.find_all(attrs={'rel': 'nofollow'})

    start = False
    for section in sections:
        if start_chapter in section.string.strip():
            start = True
        if start:
            sections_url.append({'title': section.string.strip(), 'url': section.attrs['href']})
    return sections_url


def save_content_to_txt(sections, fileID, headers):
    """
    从sections中获取要爬取的章节，爬取后存放到fileID指定的txt文件中
    :param sections: 章节列表 list
    :param fileID: txt文件的文件名，不包含'.txt' str
    :param headers: 请求头 dict
    :return: None
    """
    # 设置日志格式
    logging.basicConfig(format='%(asctime)s %(processName)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
    logging.info('start')
    with open('%s.txt' % fileID, 'w', encoding='utf8') as f:
        for section in sections:
            try:
                r = requests.get(section['url'], headers=headers, timeout=30)
                r.raise_for_status()
                r.encoding = r.apparent_encoding
            except:
                logging.warning(section['title'] + ' failed')
                continue
            title = section['title'].strip()
            
            soup = BeautifulSoup(r.text, 'lxml')
            # 处理章节内容
            content = []
            for c in soup.find(attrs={'id': 'content'}).contents:
                if isinstance(c, NavigableString):
                    content.append(str(c).strip())
                if isinstance(c, Tag) and c.name == 'br':
                        content.append('\n')
            content = ''.join(content)
            try:
                f.write(title + '\n\n')
                f.write(content + '\n\n\n')
            except Exception as e:
                logging.warning(e)
                logging.warning(section['title'] + ' failed')
                continue
            logging.info(title + ' completed')
    logging.info('end')


def main(category_url, headers, process_num):
    """
    主调度函数
    :param category_url: 目录url str
    :param headers: 请求头 dict
    :param process_num: 总进程数 int
    :return: None
    """
    logging.basicConfig(format='%(asctime)s %(processName)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
    logging.info('acquire categories...')
    sections = get_sections(headers, catagory_url)
    logging.info('success')
    processes = [0] * process_num
    step = int(len(sections) / process_num) + 1
    # 每个进程处理分配给自己的章节，并将其存放到单独的txt文件中
    logging.info('acquire section contents...')
    for i in range(process_num):
        start = i * step
        end = (i + 1) * step
        if end > len(sections):
            end = -1
        processes[i] = multiprocessing.Process(target=save_content_to_txt, args=(sections[start:end], str(i), headers), name=str(i))
        processes[i].start()
    for i in range(process_num):
        processes[i].join()
    logging.info('success')
    # 合并txt文件
    logging.info('merge txt...')
    with open(str(process_num) + '.txt', 'w', encoding='utf8') as f:
        for i in range(process_num):
            with open(str(i) + '.txt', 'r', encoding='utf8') as temp:
                f.write(temp.read())
    logging.info('success')


if __name__ == '__main__':
    main(catagory_url, headers, process_num)

