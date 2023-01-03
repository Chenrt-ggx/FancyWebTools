import json
import base64


def get_user_info(aim):
    config = json.load(open('./login/config.json', 'r'))
    if config.get(aim + '_' + 'username') and config.get(aim + '_' + 'password'):
        username = base64.b64decode(config[aim + '_' + 'username'].encode()).decode()
        password = base64.b64decode(config[aim + '_' + 'password'].encode()).decode()
        return username, password
    else:
        print('get username or password failed')
        exit(0)
