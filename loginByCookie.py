import re
import requests
from lxml import etree
from buptVpn import refreshCookie
import os

def getScore(CookieName,xuehao,passwd,vpn_account,vpn_passwd):
    s = requests.session()
    s.verify = False

    # 判断是否有Cookie缓存
    if not os.path.exists(CookieName):
        # 刷新缓存
        refreshCookie(CookieName,xuehao,passwd,vpn_account,vpn_passwd)

    #读取Cookie缓存文件
    cookieRead=open(CookieName,'r',encoding='utf-8')
    cookie_val=cookieRead.read().strip()
    cookieRead.close()

        
    s.headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        "Referer":"https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn/menu/s_menu.jsp",
        "Cookie":cookie_val  
    }
    response=s.get("https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn/bxqcjcxAction.do")
    html = etree.HTML(response.text)
    allSubject = html.xpath('//tr[@class="odd"]')
    new_list=[]
    for eSubject in allSubject:
        subjectName=eSubject.xpath('./td[3]/text()')[0].strip()
        subjectScore=eSubject.xpath('./td[7]/text()')[0].strip()
        if subjectScore=='':
            subjectScore='未录入'
        new_list.append(subjectName+':'+subjectScore)
    if new_list==[]:
        #缓存已过期,刷新缓存
        refreshCookie(CookieName,xuehao,passwd,vpn_account,vpn_passwd)
        getScore(CookieName,xuehao,passwd,vpn_account,vpn_passwd)


    # 在文件中打印成绩
    with open(xuehao+'score_list.txt','w',encoding='UTF-8') as score_file:
        for eSubject in new_list:
            score_file.write(eSubject+'\n')
