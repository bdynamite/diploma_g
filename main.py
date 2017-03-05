import requests
import json
from tqdm import tqdm

TOKEN_URL = ''
ACCESS_TOKEN = ''
VERSION = '5.52'


def get_users(dict_params, method):
    dict_params['count'] = 1000
    response = requests.get('https://api.vk.com/method/{method}'.format(method=method), dict_params).json()
    if response['response']['count'] > 1000:
        users = get_via_execute(dict_params, method, response['response']['count'])
    else:
        users = response['response']['items']
    return users


def get_via_execute(dict_params, method, number):
    number_of_query = [25000 for x in range(number // 25000)]
    number_of_query.append(number % 25000)
    users = []
    offset = 0
    for i in tqdm(number_of_query):
        number_of_execute = round((i + 499) / 1000)
        execute = 'var members = 0;' \
                  'var i = {i};' \
                  'var offset = {offset};' \
                  'while (i > 0)' \
                  '{open_bracket}' \
                  'members = members + ' \
                  'API.{method}({open_bracket}"user_id": {user_id}, "v": {v}, ' \
                  '"count": "1000", "offset": offset{close_bracket}).items;' \
                  'offset = offset + 1000;' \
                  'i = i - 1;' \
                  '{close_bracket}' \
                  'return members;'.format(i=number_of_execute, open_bracket='{', method=method, offset=offset,
                                           user_id=target_id, v=dict_params['v'], close_bracket='}')
        offset += i
        dict_params['code'] = execute
        response = requests.get('https://api.vk.com/method/execute', dict_params).json()
        users.extend(response['response'].split(','))
    return users


def get_groups(users, dict_params):
    all_groups = []
    users = list(map(int, users))
    number_of_query = [25 for x in range(len(users) // 25)]
    number_of_query.append(len(users) % 25)
    for i,number in tqdm(enumerate(number_of_query)):
        users_slice = users[i * 25:(i + 1) * 25]
        execute = 'var groups = [];' \
                  'var i = {i};' \
                  'var users = {users};' \
                  'while (i > 0)' \
                  '{open_bracket}' \
                  'groups.push(API.{method}({open_bracket}"user_id": users[i-1], "v": {v}, ' \
                  '"count": "1000", "extended": "1"{close_bracket}).items);' \
                  'i = i - 1;' \
                  '{close_bracket}' \
                  'return groups;'.format(i=number, open_bracket='{', method='groups.get',
                                          users=[*users_slice], v=dict_params['v'], close_bracket='}')
        dict_params['code'] = execute
        response = requests.get('https://api.vk.com/method/execute', dict_params).json()
        for element in response['response']:
            try:
                elements_list = [(x['id'], x['screen_name']) for x in element]
                all_groups.extend(elements_list)
            except TypeError:
                pass
    return all_groups


def save_json(data):
    with open('groups.json', 'w') as file:
        json.dump(data, file)


def make_list_of_top_n_groups(groups, n):
    list_of_dicts = [{'title': x[1], 'id': x[0], 'count': groups.count(x)} for x in tqdm(set(groups))]
    list_of_dicts = sorted(list_of_dicts, key=lambda x: x['count'], reverse=True)
    return list_of_dicts[:n]


target_id = input('Введите id пользователя: ')
params = dict(access_token=ACCESS_TOKEN, v=VERSION, user_id=target_id)

followers = get_users(params.copy(), 'users.getFollowers')
followers.extend(get_users(params.copy(), 'friends.get'))

list_of_groups = get_groups(followers, params.copy())
list_of_groups = make_list_of_top_n_groups(list_of_groups, 10)
save_json(list_of_groups)

print('Success!')



