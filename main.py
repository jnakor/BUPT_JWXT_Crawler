from loginByCookie import getScore
import os
import sys
xuehao=sys.argv[1]
vpn_account=xuehao
passwd=sys.argv[2]
vpn_passwd=sys.argv[3]
print(xuehao)
print(passwd)
print(vpn_account)
print(vpn_passwd)
def getPersonScore(xuehao,passwd,vpn_account,vpn_passwd):
    tp_state=getScore(xuehao+'cookie.txt',xuehao,passwd,vpn_account,vpn_passwd)

getScore(xuehao+'cookie.txt',xuehao,passwd,vpn_account,vpn_passwd)