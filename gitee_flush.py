import re
import time
import random
from login.gitee_login import login
from login.get_user_info import get_user_info

count, name_list = 5, [
    'disgusting_gitee',
    'not_allow_cancel_account',
    'not_allow_delete_dynamics'
]


def random_sleep():
    sleep_time = int(random.random() * 30) + 1
    print('sleep: ' + str(sleep_time))
    time.sleep(sleep_time)


def create_warehouse(session, current_user, house_name):
    request = session.get('https://gitee.com/projects/new')
    csrf_pattern = re.compile('<meta name=\"csrf-token\" content=\"(.+)?\" />')
    csrf_token = csrf_pattern.search(request.text).group(1)
    session.post(url='https://gitee.com/' + current_user + '/projects', data={
        'authenticity_token': csrf_token,
        'project[name]': house_name,
        'project[namespace_path]': current_user,
        'project[path]': house_name,
        'project[public]': 1,
        'prod': 'master',
        'dev': 'develop',
        'feat': 'feature',
        'rel': 'release',
        'bugfix': 'hotfix'
    })
    random_sleep()


def remove_warehouse(session, password, current_user, house_name):
    request = session.get('https://gitee.com/' + current_user + '/' + house_name)
    csrf_pattern = re.compile('<meta name=\"csrf-token\" content=\"(.+)?\" />')
    csrf_token = csrf_pattern.search(request.text).group(1)
    request = session.delete(url='https://gitee.com/' + current_user + '/' + house_name, headers={
        'X-CSRF-Token': csrf_token
    }, data={
        'path_with_namespace': current_user + '/' + house_name
    })
    end_limit = '\\\\n<\\\\/div>\\\\n<div class=\\\\\'field password-wrap\\\\\'>'
    bundle_pattern = re.compile('id=\\\\\"_pavise_bundle\\\\\" value=\\\\\"(.+)\\\\\" />' + end_limit)
    pavise_bundle = bundle_pattern.search(request.text).group(1)
    session.post(url='https://gitee.com/' + current_user + '/' + house_name, headers={
        'X-CSRF-Token': csrf_token
    }, data={
        '_method': 'DELETE',
        '_pavise[bundle]': pavise_bundle,
        '_pavise[password]': password
    })
    random_sleep()


def solve():
    username, password = get_user_info('gitee')
    session, current_user = login(username, password)
    gen_list = []
    for i in range(count):
        for j in name_list:
            gen_list.append(j + '_' + str(random.random()))
    for i in gen_list:
        print('creating -> ' + i)
        create_warehouse(session, current_user, i)
    for i in gen_list:
        print('removing -> ' + i)
        remove_warehouse(session, password, current_user, i)


if __name__ == '__main__':
    solve()
