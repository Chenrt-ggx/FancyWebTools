import re
import rsa
import base64
import requests
import requests.utils
from utils.image_tools import do_ocr


def get_utils():
    request = requests.get(url='https://m.bjyouth.net/site/login')
    pubkey = '\n'.join([i for i in re.findall('pubkey \\+?= \'(.*?)\'', request.text)])
    rsa_key = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode())
    return rsa_key


def get_code(session):
    request = session.get(url='https://m.bjyouth.net/site/login')
    csrf_token = requests.utils.dict_from_cookiejar(request.cookies)['_csrf_mobile']
    match = re.search('src=\"(/site/captcha.+)\" alt=\"验证码\"', request.text)
    request = session.get('https://m.bjyouth.net' + match.group(1))
    return csrf_token, do_ocr(request.content)


def login(username, password):
    rsa_key = get_utils()
    while True:
        session = requests.session()
        session.timeout = 5
        session.headers.update({
            'User-Agent': 'Y.J.Aickson'
        })
        csrf_token, code = get_code(session)
        request = session.post('https://m.bjyouth.net/site/login', data={
            '_csrf_mobile': csrf_token,
            'Login[username]': base64.b64encode(rsa.encrypt(username.encode(), rsa_key)).decode(),
            'Login[password]': base64.b64encode(rsa.encrypt(password.encode(), rsa_key)).decode(),
            'Login[verifyCode]': code
        })
        if request.text == '8':
            print('识别的验证码错误，重试中')
            continue
        if 'fail' in request.text:
            print('登录失败')
            exit(0)
        return session
