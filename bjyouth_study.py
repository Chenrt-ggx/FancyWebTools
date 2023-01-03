import re
import json
import time
import random
import datetime
from login.bjyouth_login import login
from login.get_user_info import get_user_info

org_id = 114514


def query_available(session):
    request = session.get('https://m.bjyouth.net/dxx/course')
    courses = json.loads(request.text)
    return list(map(lambda x: {'id': x['id'], 'url': x['url'], 'title': x['title']}, courses['data']['data']))


def query_learned(session):
    year = datetime.datetime.now().year
    request = session.get('https://m.bjyouth.net/dxx/my-study?page=1&limit=15&year=' + str(year))
    learned = json.loads(request.text)
    return list(map(lambda x: {'date': x['date'], 'orgname': x['orgname'], 'title': x['text'][6:-1]}, learned['data']))


def get_todo(available, learned):
    todo, unique = [], set(map(lambda x: x['title'], learned))
    for i in available:
        if i['title'] not in unique:
            todo.append(i)
    return todo


def do_study(session, cid, url):
    match = re.search('https://h5.cyol.com/special/daxuexi/\\w+/m.html\\?t=1&z=201', url)
    if not match:
        print('地址错误: ' + url)
        return
    request = session.post('https://m.bjyouth.net/dxx/check', json={'id': cid, 'org_id': org_id})
    if request.text:
        print('请求错误: ' + request.text)
        return


def solve():
    username, password = get_user_info('bjyouth')
    session = login(username, password)
    available = query_available(session)
    print('检测到可用课程:')
    for i in available:
        print('\t' + str(i['id']) + ': ' + i['title'])
    learned = query_learned(session)
    print('检测到已学课程:')
    for i in learned:
        print('\t' + str(i['date']) + ': ' + i['title'])
    todo = get_todo(available, learned)
    print('检测到待学课程:')
    for i in todo:
        print('\t' + str(i['id']) + ': ' + i['title'])
    print('学习课程:')
    for i in todo:
        print('\t' + str(i['id']) + ': ' + i['title'])
        do_study(session, i['id'], i['url'])
        delay = random.randint(30, 300)
        print('\t随机延迟 ' + str(delay) + ' 秒')
        time.sleep(delay)
    learned = query_learned(session)
    print('检测到已学课程:')
    for i in learned:
        print('\t' + str(i['date']) + ': ' + i['title'])
    todo = get_todo(available, learned)
    print('检测到待学课程:')
    for i in todo:
        print('\t' + str(i['id']) + ': ' + i['title'])


if __name__ == '__main__':
    solve()
