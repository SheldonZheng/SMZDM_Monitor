import requests
import time
import json
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import hashlib
import pymysql

database_ip_and_port = '???'
database_name = '???'
database_username = '???'
database_password = '???'

smtp_server_ip = '???'
mail_username = '???'
mail_password = '???'

target_mail_address = '???'

keys_file_path = '???'
SOCK = '???'

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
        price = ''
        if 'article_price' in string.keys():
            price = string['article_price']
        link = ''
        if 'article_link' in string.keys():
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
    with open(keys_file_path,'rt',encoding='utf-8') as f:
        file_data = f.read()
        return file_data.split(sep=',')

def send_mail(data,key,title):
    smtp_server = smtp_server_ip
    username = mail_username
    password = mail_password
    to_addr = target_mail_address
    msg = MIMEText(data, 'plain', 'utf-8')
    msg['From'] = 'SMZDM爬虫'
    msg['To'] = 'Target'
    msg['Subject'] = Header('SMZDM关注关键字;key: '+ key + ',title:' + title + '出现提示', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 587)
    server.set_debuglevel(1)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, [to_addr], msg.as_string())
    server.quit()

def md5(str):
    print(str)
    m = hashlib.md5()
    m.update(str.encode(encoding='utf-8'))
    return m.hexdigest()


def is_data_existed(result):
    db = pymysql.connect(database_ip_and_port, database_username, database_password, database_name)
    cursor = db.cursor()
    tempResult = sorted(result.items(), key=lambda result: result[0])
    sql = "SELECT * FROM smzdm_record where md5 = '%s'" % \
          md5(str(tempResult))

    print(md5(str(tempResult)))
    try:
        cursor.execute(sql)
        print(cursor.rowcount)
        if cursor.rowcount > 0 :
            return False
        else:
            return True
    except:
        db.rollback()

    db.close()

def insert_data(result):
    db = pymysql.connect(database_ip_and_port, database_username, database_password, database_name)
    db.set_charset('utf8')
    cursor = db.cursor()
    tempResult = sorted(result.items(), key=lambda result: result[0])
    sql = "INSERT INTO smzdm_record(title,price,link,page_url,md5) VALUES ('%s','%s','%s','%s','%s')" % \
          (result['title'],result['price'],result['link'],result['page_url'],md5(str(tempResult)))

    try:
        cursor.execute(sql)
        db.commit()
        if cursor.rowcount > 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        db.rollback()

    db.close()

def push_wechat(data,key,title):
    url = 'https://sc.ftqq.com/%s.send' % SOCK
    payload = {'text' : 'SMZDM_Spider,key:%s,title:%s' % (key,title),'desp':data}
    requests.post(url,data=payload,verify=False) 
    
if __name__ == '__main__':

        keys = read_local_file_keys()
        resultList = get_real_time_data()
        print(resultList)
        for result in resultList:
            for key in keys:
                if result['title'].find(key) != -1:
                    if is_data_existed(result):
                        send_mail(str(result), key, result['title'])
                        push_wechat(str(result),key,result['title'])
                        insert_data(result)

