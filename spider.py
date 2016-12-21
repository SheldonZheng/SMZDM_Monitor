import requests
import time
import json
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def get_real_time_data():
    c_time = int(time.time())
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Host': 'www.smzdm.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    url = 'http://www.smzdm.com/json_more?timesort=' + str(c_time)
    r = requests.get(url=url, headers=headers)

    # data = r.text.encode('utf-8').decode('unicode_escape')
    data = r.text

    dataa = json.loads(data)

    resultList = []

    for string in dataa:
        title = string['article_title']
        price = string['article_price']
        link = string['article_link']
        page_url = string['article_url']
        result = {
            'title': title,
            'price': price,
            'link': link,
            'page_url': page_url
        }
        resultList.append(result)

    return resultList

def read_local_file_keys():
    with open('keys.txt','rt',encoding='utf-8') as f:
        file_data = f.read()
        return file_data.split(sep=',')

def send_mail(data):
    smtp_server = 'smtp.gmail.com'
    username = 'baiyeserver@gmail.com'
    password = 'test'
    to_addr = 'zhenghangtxdyr@gmail.com'
    msg = MIMEText(data, 'plain', 'utf-8')
    msg['From'] = 'SMZDM爬虫'
    msg['To'] = 'Target'
    msg['Subject'] = Header('SMZDM关注商品出现提示', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(username, password)
    server.sendmail(username, [to_addr], msg.as_string())
    server.quit()


if __name__ == '__main__':
    send_mail('test')
    # keys = read_local_file_keys()
    #
    # resultList = get_real_time_data()
    # for result in resultList:
    #     for key in keys:
    #         if result['title'].find(key) != -1 :
    #             print(result)


