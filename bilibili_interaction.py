import re
import json
import requests
import networkx as nx
import matplotlib.pyplot as plt

use_var = False
bvid = 'BV1Dt411N7LY'


def to_get_url(url, data):
    url += '?'
    for i in data:
        url += i + '=' + data[i] + '&'
    return url[:-1]


def get_version():
    request = requests.get(to_get_url(url='https://api.bilibili.com/x/player/v2', data={
        'cid': '233',
        'bvid': bvid,
    }))
    data = json.loads(request.text)['data']
    if data.get('interaction'):
        return data['interaction']['graph_version']
    print('no interaction detected')
    exit(0)


def parse_variable(var):
    count = 1
    result = {}
    var = json.loads(var)['data']
    if var.get('hidden_vars'):
        var = var['hidden_vars']
        for i in sorted(var, key=lambda x: x['name']):
            result[i['id_v2']] = {
                'name': i['name'],
                'default': i['value'],
                'id': '< var_' + str(count) + ': ' + i['name'] + ' >'
            }
            count += 1
    return result


def parse_expr(expr, var):
    if not expr:
        return None
    global use_var
    use_var = True
    pattern = re.compile('\\$[a-zA-Z0-9]+')
    for i in pattern.findall(expr):
        expr = expr.replace(i, var[i]['id'])
    return expr


def parse(data, var, cid=1):
    data = json.loads(data)['data']
    result = {
        'id': cid,
        'title': data['title'] if data.get('title') else None
    }
    if data.get('edges').get('questions'):
        result['choices'] = {}
        for i in data['edges']['questions'][0]['choices']:
            result['choices'][i['id']] = {
                'id': i['id'],
                'cid': i['cid'],
                'option': i['option'],
                'action': parse_expr(i['native_action'], var),
                'condition': parse_expr(i['condition'], var)
            }
    return result


def search(node, vis, version, var):
    if node.get('choices'):
        for i in node['choices']:
            if node['choices'][i]['cid'] not in vis:
                request = requests.get(to_get_url(url='https://api.bilibili.com/x/stein/edgeinfo_v2', data={
                    'bvid': bvid,
                    'edge_id': str(i),
                    'graph_version': version,
                }))
                child = parse(request.text, var, node['choices'][i]['cid'])
                vis[node['choices'][i]['cid']] = child
                search(child, vis, version, var)


def display(main_map):
    node_labels = {}
    edge_labels = {}
    graph = nx.DiGraph()
    for i in main_map:
        graph.add_node(i)
    for i in main_map:
        node_labels[i] = main_map[i]['title']
        if main_map[i].get('choices'):
            for j in main_map[i]['choices']:
                node = main_map[i]['choices'][j]
                graph.add_edge(i, node['cid'])
                if edge_labels.get((i, node['cid'])) is None:
                    edge_labels[(i, node['cid'])] = node['option']
                else:
                    edge_labels[(i, node['cid'])] += '\n' + node['option']
    plt.figure(figsize=(20, 10))
    pos = nx.shell_layout(graph)
    nx.draw(graph, pos)
    nx.draw_networkx_labels(graph, pos, node_labels, font_family='YaHei Consolas Hybrid')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_family='YaHei Consolas Hybrid')
    plt.show()


def solve():
    version = str(get_version())
    request = requests.get(to_get_url(url='https://api.bilibili.com/x/stein/edgeinfo_v2', data={
        'bvid': bvid,
        'graph_version': version,
    }))
    variables = parse_variable(request.text)
    print(json.dumps(variables, indent=4, ensure_ascii=False))
    print('\n---------------------------------------\n')
    root = parse(request.text, variables)
    main_map = {root['id']: root}
    search(root, main_map, version, variables)
    print(json.dumps(main_map, indent=4, ensure_ascii=False))
    print('\n---------------------------------------\n')
    print(str(len(main_map)) + ' nodes detected')
    print('using hidden vars: ' + str(use_var))
    print('\n---------------------------------------\n')
    display(main_map)


if __name__ == '__main__':
    solve()
