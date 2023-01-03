import json
import requests
import datetime

debug = False

filter_limit = datetime.timedelta(hours=24)

urls = {
    'space': 'https://api.bilibili.com/x/space/acc/info',
    'dynamic': 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
}

headers = {
    'User-Agent': 'Tadokoro',
    'Accept-Encoding': 'gzip, deflate, br'
}


def append_query(url, query):
    if len(query):
        param = []
        for i in query:
            param.append(str(i) + '=' + str(query[i]))
        url += '?' + '&'.join(param)
    return url


def parse_space(mid, info_map):
    print('request space ' + str(mid), end=': ')
    url = append_query(urls['space'], {'mid': mid})
    request = requests.get(url, headers=headers)
    parse = json.loads(request.text)
    info_map[mid] = {
        'name': str(parse['data']['name']).strip(),
        'sign': str(parse['data']['sign']).strip()
    }
    print('done')


def parse_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def parse_text(item, key):
    if item is None:
        return None
    if '\n' in item[key]:
        return item[key].split('\n')
    return item[key]


def parse_major(item):
    if item is None:
        return None
    if item['type'] == 'MAJOR_TYPE_DRAW':
        return [i['src'] for i in item['draw']['items']]
    if item['type'] == 'MAJOR_TYPE_ARTICLE':
        return {
            'title': item['article']['title'],
            'desc': parse_text(item['article'], 'desc'),
            'id': item['article']['id']
        }
    if item['type'] == 'MAJOR_TYPE_LIVE_RCMD':
        content = json.loads(item['live_rcmd']['content'])
        return {
            'title': content['live_play_info']['title'],
            'room': content['live_play_info']['room_id'],
            'start': parse_timestamp(content['live_play_info']['live_start_time'])
        }
    if item['type'] == 'MAJOR_TYPE_ARCHIVE':
        return {
            'title': item['archive']['title'],
            'desc': parse_text(item['archive'], 'desc'),
            'duration': item['archive']['duration_text'],
            'bvid': item['archive']['bvid']
        }
    return None


def parse_item(item):
    return {
        'time': parse_timestamp(item['modules']['module_author']['pub_ts']),
        'topped': item['modules'].get('module_tag') is not None and item['modules']['module_tag']['text'] == '置顶',
        'text': parse_text(item['modules']['module_dynamic']['desc'], 'text'),
        'major': parse_major(item['modules']['module_dynamic']['major']),
        'orig': None if item.get('orig') is None else parse_item(item['orig'])
    }


def parse_dynamic(mid, update_map):
    print('request dynamic ' + str(mid), end=': ')
    url = append_query(urls['dynamic'], {'host_mid': mid})
    request = requests.get(url, headers=headers)
    parse = json.loads(request.text)
    update = {
        'next': parse['data']['offset'] if parse['data']['has_more'] else '',
        'list': [parse_item(i) for i in parse['data']['items']]
    }
    last_time = datetime.datetime.strptime(update['list'][-1]['time'], '%Y-%m-%d %H:%M:%S')
    while update['next'] != '' and last_time + filter_limit > datetime.datetime.now():
        url = append_query(urls['dynamic'], {'offset': update['next'], 'host_mid': mid})
        print(url)
        request = requests.get(url, headers=headers)
        print(request.text)
        parse = json.loads(request.text)
        update['next'] = parse['data']['offset'] if parse['data']['has_more'] else -1
        update['list'] += [parse_item(i) for i in parse['data']['items']]
    update_map['update'] = update
    print('done')


def filter_update(item):
    now = datetime.datetime.now()
    result = []
    for i in item['update']['list']:
        if datetime.datetime.strptime(i['time'], '%Y-%m-%d %H:%M:%S') + filter_limit > now:
            result.append(i)
    item['update'] = '未发现更新' if len(result) == 0 else result


def delete_update(main_map, key):
    now = datetime.datetime.now()
    result = []
    for i in main_map[key]['update']['list']:
        if datetime.datetime.strptime(i['time'], '%Y-%m-%d %H:%M:%S') + filter_limit > now:
            result.append(i)
    if len(result) == 0:
        main_map.pop(key)
    else:
        main_map[key]['update'] = result


def solve():
    main_map = {}
    with open('./profile/pigeons.json', 'r') as file:
        query_list = json.loads(file.read())
    for i in query_list:
        parse_space(i, main_map)
    print()
    print('------------------- 关注列表 -------------------\n')
    print(json.dumps(main_map, indent=4, ensure_ascii=False) + '\n')
    for i in main_map:
        parse_dynamic(i, main_map[i])
    if debug:
        print()
        print('------------------- 追踪内容 -------------------\n')
        print(json.dumps(main_map, indent=4, ensure_ascii=False) + '\n')
    if debug:
        for i in main_map:
            filter_update(main_map[i])
    else:
        for i in query_list:
            delete_update(main_map, i)
    print()
    print('------------------- 更新内容 -------------------\n')
    print(json.dumps(main_map, indent=4, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    solve()
