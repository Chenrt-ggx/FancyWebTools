import rsa
import base64
import requests
import requests.utils
from bs4 import BeautifulSoup


def get_utils():
    request = requests.get('https://www.bv2008.cn/app/user/login.php')
    cookies = requests.utils.dict_from_cookiejar(request.cookies)
    soup = BeautifulSoup(request.text, 'html.parser')
    csrf_token = soup.find(name='meta', attrs={'name': 'csrf-token'}, recursive=True)['content']
    seid = soup.find(name='input', attrs={'id': 'seid'}, recursive=True)['value']
    request = requests.get('https://css.zhiyuanyun.com/common/login.js')
    pubkey = ''
    for i in filter(lambda x: 'pubkey' in x and '\'' in x, request.text.split('\n')):
        pubkey += i.split('\'')[1] + '\n'
    request = requests.post(url='https://www.bv2008.cn/app/api/view.php?m=get_login_yzm', headers={
        'Host': 'www.bv2008.cn',
        'User-Agent': 'MicroMessenger'
    })
    soup = BeautifulSoup(request.text, 'html.parser')
    code = soup.find(name='p', attrs={
        'style': 'font-size:28px;font-weight:bold;letter-spacing:5px;'
    }, recursive=True).string
    return cookies, csrf_token, seid, code, rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode())


def login(username, password):
    cookies, csrf_token, seid, code, rsa_key = get_utils()
    request = requests.post(url='https://www.bv2008.cn/app/user/login.php?m=login', headers={
        'X-CSRF-TOKEN': csrf_token
    }, data={
        'seid': seid,
        'uname': username,
        'upass': base64.b64encode(rsa.encrypt(password.encode(), rsa_key)).decode(),
        'referer': 'https://www.bv2008.cn/',
        'uyzm': code
    }, cookies=cookies)
    if '\"code\":0' not in request.text:
        print(request.text)
        exit(0)
    cookies = requests.utils.dict_from_cookiejar(request.cookies)
    return cookies
