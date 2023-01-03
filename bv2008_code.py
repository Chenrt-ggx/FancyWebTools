import re
import requests

if __name__ == '__main__':
    request = requests.post(url='https://www.bv2008.cn/app/api/view.php?m=get_login_yzm', headers={
        'Host': 'www.bv2008.cn',
        'User-Agent': 'MicroMessenger'
    })
    print(re.search('\\d{6}', request.text).group())
