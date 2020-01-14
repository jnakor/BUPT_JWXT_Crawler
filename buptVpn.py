
import requests
from PIL import Image
from io import BytesIO
from yanzhengma import shibie
def refreshCookie(CookieName,xuehao,passwd,vpn_account,vpn_passwd):
    s = requests.session()
    s.verify = False
    init_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        "Referer":"https://vpn.bupt.edu.cn/",
        'content-type': 'charset=utf8',
    }
    # https://vpn.bupt.edu.cn/global-protect/login.esp
    response=s.get("https://vpn.bupt.edu.cn/global-protect/login.esp",headers=init_headers)
    PHPSESSID=response.headers['Set-Cookie'].split(';')[0]

    login_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        "Referer":"https://vpn.bupt.edu.cn/global-protect/login.esp",
        'Content-Type':'application/x-www-form-urlencoded',
        'Origin': 'https://vpn.bupt.edu.cn',
        'Cookie':PHPSESSID
    }

    post_data={
        'prot':'https:',
        'server':'vpn.bupt.edu.cn',
        'inputStr':'',
        'action':'getsoftware',
        'user':vpn_account,
        'passwd':vpn_passwd,
        'ok':'Log In'
    }

    response=s.post('https://vpn.bupt.edu.cn/global-protect/login.esp',post_data,headers=login_headers)
    GP_SESSION_CK=response.headers['Set-Cookie'].split(';')[0]

    jwxt_headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        # "Referer":"https://vpn.bupt.edu.cn/global-protect/login.esp",
        # 'Content-Type':'application/x-www-form-urlencoded',
        # 'Origin': 'https://vpn.bupt.edu.cn',
        'Cookie':PHPSESSID+';'+GP_SESSION_CK
    }

    response=s.get('https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn',headers=jwxt_headers)
    PAN_GP_CK_VER=response.headers['Set-Cookie'].split(',')[0].split(';')[0].strip()
    PAN_GP_CACHE_LOCAL_VER_ON_SERVER=response.headers['Set-Cookie'].split(',')[1].split(';')[0].strip()

    yzm_headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        "Referer":"https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn",
        'Cookie':PHPSESSID+';'+GP_SESSION_CK+';'+PAN_GP_CK_VER+';'+PAN_GP_CACHE_LOCAL_VER_ON_SERVER
    }

    response=s.get("https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn/validateCodeAction.do?gp-1&random=",headers=yzm_headers)
    image=Image.open(BytesIO(response.content))
    image.save('yzm.png')
    zjh=xuehao
    mm=passwd
    v_yzm=shibie('yzm.png')
    post_data={
        'type':'sso',
        'zjh':zjh,
        'mm':mm,
        'v_yzm':v_yzm
    }
    print(v_yzm)
    login_headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Host": "vpn.bupt.edu.cn",
        "Referer":"https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn",
        "Origin": "https://vpn.bupt.edu.cn",
        "Cookie":PHPSESSID+';'+GP_SESSION_CK+';'+PAN_GP_CK_VER+';'+PAN_GP_CACHE_LOCAL_VER_ON_SERVER,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response=s.post('https://vpn.bupt.edu.cn/https/jwxt.bupt.edu.cn/jwLoginAction.do?',post_data,headers=login_headers)
    with open(CookieName,'w',encoding='utf-8') as cookieStore:
        cookieStore.write(PHPSESSID+';'+GP_SESSION_CK+';'+PAN_GP_CK_VER+';'+PAN_GP_CACHE_LOCAL_VER_ON_SERVER)
    return "OK"