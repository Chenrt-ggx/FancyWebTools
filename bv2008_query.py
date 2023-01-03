import json
import time
import requests
from bs4 import BeautifulSoup
from login.bv2008_login import login
from login.get_user_info import get_user_info


def parse(data):
    result = []
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find(name='table', attrs={'class': 'table1'}, recursive=True)
    lst = ['time', 'text', 'valid', 'from', 'project', 'group', 'date']
    for i in table.contents[2:]:
        cnt, info = 0, {}
        if type(i) == type(table):
            for j in i.contents:
                if type(j) == type(table):
                    for k in j.contents:
                        if type(k) == type(table):
                            if k.string is not None:
                                info[lst[cnt]] = k.string
                                cnt += 1
                        else:
                            info[lst[len(lst) - 1]] = time.strptime(str(k), '%Y-%m-%d %X')
            result.append(info)
    total = 0
    for i in result:
        i['date'] = time.strftime('%Y-%m-%d %X', i['date'])
        i['text'] = i['text'].split('【')[1].split('】')[0]
        i['time'] = float(i['time'].split('小时')[0])
        i['valid'] = i['valid'] == '已生效'
        if i['valid']:
            total += i['time']
    final = {'sum': total, 'result': result}
    return final


def solve():
    username, password = get_user_info('bv2008')
    cookies = login(username, password)
    request = requests.get('https://www.bv2008.cn/app/user/hour.php', cookies=cookies)
    result = parse(request.text)
    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    solve()
