import requests
import execjs

'''
    模块：execjs
    功能：运行JS代码，获取Post特征代码
'''
def get_sign(word):
    with open('templates/yd.js','r') as sign:
        sign = execjs.compile(sign.read())
        res = sign.call('r', word)
    #print(res)
    transl(word,res)

'''
    模块：requests
    功能：提交post请求获取翻译后的值
'''
def transl(word,res):
    url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
    headers = {
        'Cookie': 'OUTFOX_SEARCH_USER_ID=-1823007390@120.229.22.22; DICT_UGC=be3af0da19b5c5e6aa4e17bd8d90b28a|; JSESSIONID=abcN6nS1T7jIE4L3-T8Kx; OUTFOX_SEARCH_USER_ID_NCOO=1093037412.8131955; ___rl__test__cookies=1620221370571',
        'Referer': 'https://fanyi.youdao.com/?keyfrom=dict2.index',
        'User-Agent': user_agent
    }

    date = {
        'i': word,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': res['salt'],
        'sign': res['sign'],
        'lts': res['ts'],
        'bv': res['bv'],
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTlME'
    }
    res = requests.post(url, headers=headers, data=date)
    res = res.json()['translateResult'][0][0]
    result = res['src']
    tgt = res['tgt']
    print(f'输入：{ result}\n翻译：{tgt}')


if __name__ == '__main__':
    while True:
        trans_word = input('输入需要翻译的文字:')
        if trans_word:
            get_sign(trans_word)


