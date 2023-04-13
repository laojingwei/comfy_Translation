import json
import requests
from nodes import CLIPTextEncode
import execution

import webbrowser
import time
import os

CHARACTERLIST = ['ZH_CN2EN1','ZH_CN2EN','ZH_AUTO1','ZH_AUTO']
CHARACTERLISTLOG = ['ZH_CN2EN1','ZH_AUTO1']
CHARACTERLISTCN = ['ZH_CN2EN1','ZH_CN2EN']
LINEFEED = '\n\n'


# 定义一个装饰器处理保存绘图的内容
# Define a decorator
def recursive_executeDec(func):
    def wrapper(*args, **kwargs):
        for a in args[1] :
            if args[1][a]['inputs']:
                text = ''
                try:
                    text = args[1][a]['inputs']['text']
                    isShowLog = False
                    catIsIn = False

                    for i in CHARACTERLISTLOG:
                        if i in text:
                            isShowLog = True

                    for i in CHARACTERLIST:
                        if i in text:
                            catIsIn = True

                    if catIsIn:
                        if isShowLog:
                            print('启用翻译(Enable translation)>>>>>>>>>>>>>')
                    if catIsIn:
                        textNew = text2other(text,isShowLog)
                        args[1][a]['inputs']['text'] = textNew
                except:
                    pass
        return func(*args, **kwargs)
    return wrapper

# 使用装饰器去修饰recursive_execute方法
# Use the decorator to decorate recursive_execute
execution.recursive_execute = recursive_executeDec(execution.recursive_execute)


# 定义一个装饰器处理传给ai绘图的内容
# Define a decorator
def CLIPTextEncodeDec(func):
    def wrapper(*args, **kwargs):
        if kwargs and kwargs['text']:
            text = kwargs['text']
            print(LINEFEED,'最终用于AI渲染的关键词如下（The final keywords used for AI rendering are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,text,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
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
    for i in CHARACTERLISTCN:
        if i in text:
            Type = 'ZH_CN2EN'
    for i in CHARACTERLIST:
        if i in text:
            text = text.replace(i,'')
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
            print("LINEFEED调用翻译失败，未进行翻译，原数据返回（call translation failure, not for translation, the original data back）>>>>>>：",text,LINEFEED)
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
            print(LINEFEED,'转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,resText,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
        return resText
    except:
        if isShowLog:
            print(LINEFEED,'转换失败，如有需要请自行翻译（conversion failed in English, if necessary please make your own translation）>>>>>>>>>>>>>：',LINEFEED,text,LINEFEED)
        return text

def text2other(text,isShowLog):
    if text:
        # 翻译前，转义一些特殊符号，要不然翻译api那边翻译后可能位置错乱或缺少某些符号
        # before translation, some special symbols, escape or after translation API there may position disorder or lack some symbols
        textStr = translate(text.replace('（','(').replace('(','(').replace('）',')').replace(')',')').replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('【','[').replace('】',']').replace(':','!').replace('：','!'),isShowLog)
        return set_textStr(textStr,text,isShowLog)
    else:
        return text


try:
    # 打开自定义浏览器，如果配置了openIE.txt，会去获取里面路径打开你想要打开的浏览器，如果没有这个文件，则按默认方式去打开
    # Open the custom browser, if configured with openIE.txt, will go to the inside path to open the browser you want to open
    # TODO 目前会打开两个浏览器，一个是默认一个是自定义的，需要你手动关闭不想要打开的浏览器
    # TODO currently opens two browsers, one by default and one by custom, requiring you to manually close any browser you don't want to open
    # 这里很抱歉无法屏蔽ComfyUI去打开默认浏览器，我会尝试找ComfyUI的作者看看能否修改一下他们的代码好让我们可以去自定义打开浏览器
    # I'm sorry that I can't block ComfyUI to open the default browser. I will try to find the ComfyUI authors to see if they can modify their code so that we can customize the browser to open
    txtPath = './ComfyUI/custom_nodes/openIE.txt'
    if os.path.exists(txtPath): 
        f = open(txtPath, "r", encoding="utf-8")
        linesList = f.readlines()
        f.close()
        IEPath = ''
        for t in linesList:
            if "PATH=" in t:
                IEPath = t.replace('PATH=','')
                break
        url = "http://127.0.0.1:8188"
        IEPath = IEPath+" %s"
        # 打开第一个网址
        webbrowser.get(IEPath).open(url)
        # 延时一秒
        time.sleep(1)
        # 在新标签页打开第二个网址
        # webbrowser.get(chrome_path).open_new_tab(url)
except :
    pass

# if __name__ == '__main__':
#     customizeOpenIE()
# if __name__ == '__main__':
#     # text2other('中文，｛{[【（图文，|散文：0.2)】]}｝')
#     text2other('ZH_CN2EN1 （黄色眼睛：1.2），|她的眼中有着灵气，embeddings:cryq（她)（的笑容）有着(((仙音：1.3)))[修|炼：3]，她（（（（的身材有着））））法相，她是一个修炼成仙的（（（美人儿）））。',True)
#     # text2other('ZH_CN2EN1 18岁， (embedding:SDA768:1.2 )(embedding:SDA768:1.2 )',True)
#     # init()


# webbrowser.open("http://{}:{}".format(address, port))
# IEPath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# webbrowser.register('IE', None, webbrowser.BackgroundBrowser(IEPath))
# webbrowser.get('IE').open("http://{}:{}".format(address, port), new=1,autoraise=True)