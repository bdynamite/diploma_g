import requests
import time
import json

TOKEN_URL = 'https://oauth.vk.com/blank.html#access_token=' \
            '5794f313f436101f5eefdf8d152c8f0c62a7adb8e4b8a3dcb16040585d1ece4755a1d68e0061d914006a1' \
            '&expires_in=0&user_id=289384'
ACCESS_TOKEN = '5794f313f436101f5eefdf8d152c8f0c62a7adb8e4b8a3dcb16040585d1ece4755a1d68e0061d914006a1'
VERSION = '5.52'


def get_friends(dict_params):
    response = requests.get('https://api.vk.com/method/friends.get', dict_params)
    return response.json()['response']['items']


def get_followers(dict_params):
    dict_params['count'] = 100
    response = requests.get('https://api.vk.com/method/users.getFollowers', dict_params)
    return response.json()['response']['items']


def get_groups(users, dict_params):
    all_groups = []
    for i, user in enumerate(users):
        if (i + 1) % 3 == 0: # для удовлетворения ограничениям API по количеству запросов в секунду
            time.sleep(1)
        params['user_id'] = user
        groups = requests.get('https://api.vk.com/method/groups.get', dict_params).json()
        if not groups.get('error'):
            print(groups)
            continue
        all_groups.extend(groups['response']['items'])
        print('{}/{}'.format(i + 1, len(users)))
    print(len(all_groups))
    print(len(set(all_groups)))
    return all_groups


def save_json(data):
    with open('groups.json', 'w') as file:
        json.dump(data, file)


def make_list_of_top_n_groups(groups, n):
    list_of_dicts = [{'title':x, 'count':groups.count(x)} for x in set(groups)]
    list_of_dicts = sorted(list_of_dicts, key=lambda x: x['count'], reverse=True)
    return list_of_dicts[:n]


target_id = input('Введите id пользователя: ')
params = dict(access_token=ACCESS_TOKEN, v=VERSION, user_id=target_id)

followers = get_followers(params)
followers.extend(get_friends(params))
list_of_groups = get_groups(followers, params)
list_of_groups = make_list_of_top_n_groups(list_of_groups, 10)
save_json(list_of_groups)

print(list_of_groups)



'https://vk.com/326374'
