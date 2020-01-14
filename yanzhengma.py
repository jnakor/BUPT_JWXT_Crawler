# coding=utf-8





import os,sys
import base64
import hashlib
import time
import urllib
import urllib.request

import json
import requests
import string
import importlib,sys
importlib.reload(sys)
# sys.setdefaultencoding('utf8')

FATEA_PRED_URL  = "http://pred.fateadm.com"

def LOG(log):
    # 不需要测试时，注释掉日志就可以了
    print(log)
    log = None

class TmpObj():
    def __init__(self):
        self.init   = True
        self.value  = None

class Rsp():
    def __init__(self):
        self.ret_code   = -1
        self.cust_val   = 0.0
        self.err_msg    = "succ"
        self.pred_rsp   = TmpObj()

    def ParseJsonRsp(self, rsp_data):
        if rsp_data is None:
            self.err_msg     = "http request failed, get rsp Nil data"
            return
        jrsp                = json.loads( rsp_data)
        self.ret_code       = int(jrsp["RetCode"])
        self.err_msg        = jrsp["ErrMsg"]
        self.request_id     = jrsp["RequestId"]
        if self.ret_code == 0:
            rslt_data   = jrsp["RspData"]
            if rslt_data is not None and rslt_data != "":
                jrsp_ext    = json.loads( rslt_data)
                if "cust_val" in jrsp_ext.keys():
                    data        = jrsp_ext["cust_val"]
                    self.cust_val   = float(data)
                if ("result") in jrsp_ext.keys():
                    data        = jrsp_ext["result"]
                    self.pred_rsp.value     = data

def CalcSign(pd_id, passwd, timestamp):
    md5     = hashlib.md5()
    md5.update((timestamp + passwd).encode("utf-8"))
    csign   = md5.hexdigest()

    md5     = hashlib.md5()
    md5.update((pd_id + timestamp + csign).encode("utf-8"))
    csign   = md5.hexdigest()
    return csign

def CalcCardSign(cardid, cardkey, timestamp, passwd):
    md5     = hashlib.md5()
    md5.update(passwd + timestamp + cardid + cardkey)
    return md5.hexdigest()

def HttpRequest(url, body_data):
    rsp         = Rsp()
    post_data   = urllib.parse.urlencode(body_data)
    request     = urllib.request.Request(url, post_data.encode("utf-8"))
    request.add_header( "User-Agent", "Mozilla/5.0")
    rsp_data    = urllib.request.urlopen(request).read()
    rsp.ParseJsonRsp( rsp_data)
    return rsp

def PostFile(url, data, img_data):
    rsp         = Rsp()
    files       = {'img_data':('img_data', img_data)}
    headers     = {"User-Agent": "Mozilla/5.0"}
    r           = requests.post( url, data=data, files=files, headers = headers)
    rsp.ParseJsonRsp( r.text)
    return rsp

class FateadmApi():
    # API接口调用类
    # 参数（appID，appKey，pdID，pdKey）
    def __init__(self, app_id, app_key, pd_id, pd_key):
        self.app_id     = app_id
        if app_id is None:
            self.app_id = ""
        self.app_key    = app_key
        self.pd_id     = pd_id
        self.pd_key    = pd_key
        self.host       = FATEA_PRED_URL

    def SetHost(self, url):
        self.host       = url
    #
    # 查询余额
    # 参数：无
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.cust_val：用户余额
    #   rsp.err_msg：异常时返回异常详情
    #
    def QueryBalc(self):
        tm      = str( int(time.time()))
        sign    = CalcSign( self.pd_id, self.pd_key, tm)
        param   = {
                "user_id": self.pd_id,
                "timestamp": tm,
                "sign": sign
                }
        url     = self.host + "/api/custval"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("query succ ret: {} cust_val: {} rsp: {} pred: {}".format( rsp.ret_code, rsp.cust_val, rsp.err_msg, rsp.pred_rsp.value))
        else:
            LOG("query failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 查询网络延迟
    # 参数：pred_type:识别类型
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.request_id：唯一的订单号
    #   rsp.err_msg： 异常时返回异常详情
    #
    def QueryTTS(self, pred_type):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp": tm,
                "sign": sign,
                "predict_type": pred_type,
                }
        if self.app_id != "":
            #
            asign       = CalcSign(self.app_id, self.app_key, tm)
            param["appid"]     = self.app_id
            param["asign"]      = asign
        url     = self.host + "/api/qcrtt"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("query rtt succ ret: {} request_id: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.err_msg))
        else:
            LOG("predict failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 识别验证码
    # 参数：pred_type:识别类型  img_data:图片的数据
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.request_id：唯一订单号
    #   rsp.pred_rsp.value：识别结果
    #   rsp.err_msg：异常时返回异常详情
    #
    def Predict(self, pred_type, img_data):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp": tm,
                "sign": sign,
                "predict_type": pred_type,
                "up_type": "mt"
                }
        if self.app_id != "":
            #
            asign       = CalcSign(self.app_id, self.app_key, tm)
            param["appid"]     = self.app_id
            param["asign"]      = asign
        url     = self.host + "/api/capreg"
        files = img_data
        rsp = PostFile(url,param,files)
        if rsp.ret_code == 0:
            LOG("predict succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("predict failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
            if rsp.ret_code == 4003:
                #lack of money
                LOG("cust_val <= 0 lack of money, please charge immediately")
        return rsp

    #
    # 从文件进行验证码识别
    # 参数：pred_type;识别类型  file_name:文件名
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.request_id：唯一订单号
    #   rsp.pred_rsp.value：识别结果
    #   rsp.err_msg：异常时返回异常详情
    #
    def PredictFromFile( self, pred_type, file_name):
        with open(file_name, "rb") as f:
            data = f.read()
        return self.Predict(pred_type,data)


    #
    # 识别失败，进行退款请求
    # 参数：request_id：需要退款的订单号
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.err_msg：异常时返回异常详情
    #
    # 注意:
    #    Predict识别接口，仅在ret_code == 0时才会进行扣款，才需要进行退款请求，否则无需进行退款操作
    # 注意2:
    #   退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
    #
    def Justice(self, request_id):
        if request_id == "":
            #
            return
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign,
                "request_id":request_id
                }
        url     = self.host + "/api/capjust"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("justice succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("justice failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 充值接口
    # 参数：cardid：充值卡号  cardkey：充值卡签名串
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.err_msg：异常时返回异常详情
    #
    def Charge(self, cardid, cardkey):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        csign       = CalcCardSign(cardid, cardkey, tm, self.pd_key)
        param       = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign,
                'cardid':cardid,
                'csign':csign
                }
        url     = self.host + "/api/charge"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("charge succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("charge failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    ##
    # 充值，只返回是否成功
    # 参数：cardid：充值卡号  cardkey：充值卡签名串
    # 返回值： 充值成功时返回0
    ##
    def ChargeExtend(self, cardid, cardkey):
        return self.Charge(cardid,cardkey).ret_code

    ##
    # 调用退款，只返回是否成功
    # 参数： request_id：需要退款的订单号
    # 返回值： 退款成功时返回0
    #
    # 注意:
    #    Predict识别接口，仅在ret_code == 0时才会进行扣款，才需要进行退款请求，否则无需进行退款操作
    # 注意2:
    #   退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
    ##
    def JusticeExtend(self, request_id):
        return self.Justice(request_id).ret_code

    ##
    # 查询余额，只返回余额
    # 参数：无
    # 返回值：rsp.cust_val：余额
    ##
    def QueryBalcExtend(self):
        rsp = self.QueryBalc()
        return rsp.cust_val

    ##
    # 从文件识别验证码，只返回识别结果
    # 参数：pred_type;识别类型  file_name:文件名
    # 返回值： rsp.pred_rsp.value：识别的结果
    ##
    def PredictFromFileExtend( self, pred_type, file_name):
        rsp = self.PredictFromFile(pred_type,file_name)
        return rsp.pred_rsp.value

    ##
    # 识别接口，只返回识别结果
    # 参数：pred_type:识别类型  img_data:图片的数据
    # 返回值： rsp.pred_rsp.value：识别的结果
    ##
    def PredictExtend(self,pred_type, img_data):
        rsp = self.Predict(pred_type,img_data)

        return rsp.pred_rsp.value



def shibie(pic_name):
    # pd账号秘钥，请在用户中心页获取
    pd_id           = "119695"
    pd_key          = "NTYqslMPAIn5AZmOItN2Tq80KXc5GHbI"
    app_id			= "100001"
    app_key 		= "123456"
    # 具体类型可以查看官方网站的价格页选择具体的类型，不清楚类型的，可以咨询客服
    pred_type       = "30400"
    # 初始化api接口
    api             = FateadmApi(app_id, app_key, pd_id, pd_key)
    #查询余额接口
    balance 		=  api.QueryBalcExtend()   # 直接返余额
    # api.QueryBalc()

    #通过文件识别验证码
    #通过文件进行验证码识别,请使用自己的图片文件替换
    # 如果是通过url直接获取内存图片，这直接调用 Predict接口就好
    file_name =pic_name
    res =  api.PredictFromFileExtend(pred_type,file_name)  	# 直接返回识别结果
    return res
    # # 多网站类型时，需要增加src_url参数，具体请参考api文档: http://docs.fateadm.com/web/#/1?page_id=6
    # # rsp             = api.PredictFromFile(pred_type, file_name) # 返回识别结果的详细信息
    # '''
    # # 如果不是通过文件识别，则调用Predict接口：
    # # res =  api.PredictExtend(pred_type,data)  	# 直接返回识别结果
    # rsp             = api.Predict(pred_type,data) 	# 返回识别结果的详细信息
    # '''

    # just_flag    = False
    # if just_flag :
    #     if rsp.ret_code == 0:
    #         # 识别的结果如果与预期不符，可以调用这个接口将预期不符的订单退款
    #         # 退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
    #         api.Justice( rsp.request_id)

    # LOG("print in testfunc")

if __name__ == "__main__":
    TestFunc('bdbutton.png')


