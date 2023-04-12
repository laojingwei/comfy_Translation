import json

import requests

from nodes import CLIPTextEncode

# 定义一个装饰器
# Define a decorator
def CLIPTextEncodeDec(func):
    def wrapper(*args, **kwargs):
        if kwargs and kwargs['text']:
            # ZH_CN2EN1 ZH_AUTO1 --> open log
            # ZH_CN2EN ZH_AUTO --> close log
            if 'ZH_CN2EN1' in kwargs['text'] or 'ZH_AUTO1' in kwargs['text'] :
                isShowLog = True
            else:
                isShowLog = False

            if 'ZH_CN2EN' in kwargs['text'] or 'ZH_CN2EN1' in kwargs['text'] or 'ZH_AUTO' in kwargs['text'] or 'ZH_AUTO1' in kwargs['text'] :
                if isShowLog:
                    print('启用翻译(Enable translation)>>>>>>>>>>>>>')
                text = kwargs['text']
                kwargs['text'] = text2other(text,isShowLog)
            # else:
            #     if isShowLog:
            #         print('未启用翻译，请注意输入内容语言，如需翻译请添加 ZH_CN2EN 或 ZH_AUTO (Translation is not enabled. Please note the content language. If translation is required, please add ZH_CN2EN or ZH_AUTO)>>>>>>>>>>>>>')
        return func(*args, **kwargs)
    return wrapper

# 使用装饰器去修饰CLIPTextEncode类的encode方法
# Use the decorator to decorate the encode method of the CLIPTEXTENCODE class
CLIPTextEncode.encode = CLIPTextEncodeDec(CLIPTextEncode.encode)

# 使用post调用有道api
# Using post called youdao API
def translate(text,isShowLog):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # type:ZH_CN2EN   AUTO
    # i:要翻译的内容
    # I: to the content of the translation
    Type = 'AUTO'
    # 优先使用中转英，如果是AUTO，则让有道api自动判断转义
    # It is preferred to use Chinese to English. If it is AUTO, let Youdao api automatically determine escape
    if 'ZH_CN2EN' in text or 'ZH_CN2EN1' in text :
        Type = 'ZH_CN2EN'
    else:
        Type = 'AUTO'
    text = text.replace('ZH_CN2EN1','').replace('ZH_AUTO1','').replace('ZH_CN2EN','').replace('ZH_AUTO','')
    key = {
        'type': Type,
        'i': text,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    response = requests.post(url, data=key)
    # 服务器返回是否成功
    # the server returns success
    if response.status_code == 200:
        # 获得相应的结果
        # to get the corresponding results
        return response.text
    else:
        if isShowLog:
            print("调用翻译失败，未进行翻译，原数据返回（call translation failure, not for translation, the original data back）>>>>>>：",text)
        return text

def set_textStr(textStr,text,isShowLog):
    try:
        # 处理成json格式，方便获取翻译回来的tgt内容
        # processing into json format, convenient access to translation back TGT content
        result = json.loads(textStr)
        tgtText = ''
        tgtList = result['translateResult'][0]
        # 循环获取tgt
        # loop gain TGT
        for i in tgtList:
            tgtText = tgtText+i['tgt']
        # 把转义后的符号转回来
        # to escape after sign back
        resText = tgtText.replace('，',',').replace('：',':').replace('\"','"').replace('）',')').replace('(','(').replace('!',':').replace('！',':')
        if isShowLog:
            print('转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓','\n\n',resText,'\n\n','↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑','\n\n')
        return resText
    except:
        if isShowLog:
            print('转换失败，如有需要请自行翻译（conversion failed in English, if necessary please make your own translation）>>>>>>>>>>>>>：',text)
        return text

def text2other(text,isShowLog):
    if text:
        # 翻译前，转义一些特殊符号，要不然翻译api那边翻译后可能位置错乱或缺少某些符号
        # before translation, some special symbols, escape or after translation API there may position disorder or lack some symbols
        textStr = translate(text.replace('（','(').replace('(','(').replace('）',')').replace(')',')').replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('【','[').replace('】',']').replace(':','!').replace('：','!'),isShowLog)
        return set_textStr(textStr,text,isShowLog)
    else:
        return text

# if __name__ == '__main__':
#     # text2other('中文，｛{[【（图文，|散文：0.2)】]}｝')
#     # text2other('ZH_CN2EN1 （黄色眼睛：1.2），|她的眼中有着灵气，embeddings:cryq（她)（的笑容）有着(((仙音：1.3)|))[|修炼：3]，她（（（（的身材有着））））法相，她是一个修炼成仙的（（（美人儿）））。',True)
#     text2other('ZH_CN2EN1 18岁， (embedding:SDA768:1.2 )(embedding:SDA768:1.2 )',True)
#     # init()