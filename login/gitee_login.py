import re
import rsa
import base64
import requests


def login(username, password):
    session = requests.session()
    request = session.get('https://gitee.com/login')
    csrf_pattern = re.compile('<meta name=\"csrf-token\" content=\"(.+)?\" />')
    csrf_token = csrf_pattern.search(request.text).group(1)
    md5_pattern = re.compile('-----BEGIN PUBLIC KEY-----(.+)-----END PUBLIC KEY-----')
    md5_key = md5_pattern.search(request.text).group()
    md5_key = '\n'.join(md5_key.split('\\n'))
    real_key = rsa.PublicKey.load_pkcs1_openssl_pem(md5_key.encode('utf-8'))
    real_pass = base64.b64encode(rsa.encrypt(password.encode('gbk'), real_key))
    request = session.post(url='https://gitee.com/login', data={
        'encrypt_key': 'password',
        'authenticity_token': csrf_token,
        'user[login]': username,
        'encrypt_data[user[password]]': real_pass.decode('utf-8')
    })
    user_pattern = re.compile('\"current_user\":\"(.+)\",\"action_name\"')
    if user_pattern.search(request.text) is None:
        print('登录失败')
        exit(0)
    current_user = user_pattern.search(request.text).group(1)
    return session, current_user
