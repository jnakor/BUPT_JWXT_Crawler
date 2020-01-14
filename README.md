# bupt_jwxt_check
北京邮电大学校外查成绩python脚本，不需要自己挂vpn，内嵌了requests对web vpn页面的模拟登录。
由于jwxt登录需要识别验证码，已经提供了现成可用的验证码api，但总共只有10000次使用，建议自行寻找其他验证码api。
在buptVpn.py的第66行为验证码api调用（shibie（）），自行替换即可。

# 调用示例：
python main.py 学号 教务系统密码 vpn密码

python main.py 2017211666 hdusiahdi fhuihfudf
