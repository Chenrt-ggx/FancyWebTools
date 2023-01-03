import requests
from login.bv2008_login import login
from login.get_user_info import get_user_info


def solve():
    username, password = get_user_info('bv2008')
    cookies = login(username, password)
    request = requests.get('https://www.bv2008.cn/app/user/cert.php', cookies=cookies)
    with open(username + '_cert.pdf', 'wb') as file:
        file.write(request.content)


if __name__ == '__main__':
    solve()
