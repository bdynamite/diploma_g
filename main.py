import requests
import json
from tqdm import tqdm

TOKEN_URL = 'https://oauth.vk.com/blank.html#access_token=' \
            '5794f313f436101f5eefdf8d152c8f0c62a7adb8e4b8a3dcb16040585d1ece4755a1d68e0061d914006a1' \
            '&expires_in=0&user_id=289384'
ACCESS_TOKEN = '5794f313f436101f5eefdf8d152c8f0c62a7adb8e4b8a3dcb16040585d1ece4755a1d68e0061d914006a1'
VERSION = '5.52'


class Celebrity:

    def __init__(self, id):
        self.id = id
        self.followers_method = 'https://api.vk.com/method/users.getFollowers'
        self.friends_method = 'https://api.vk.com/method/friends.get'
        self.groups_method = 'https://api.vk.com/method/groups.get'
        self.execute_method = 'https://api.vk.com/method/execute'
        self.params = dict(access_token=ACCESS_TOKEN, v=VERSION, user_id=self.id)

    def save_top_n_subscribers_groups_in_json(self, n):
        subscribers = self.get_subscribers()
        groups = self.get_groups(subscribers, self.params.copy())
        top_n_groups = self.make_list_of_top_n_groups(groups, n)
        self.save_json(top_n_groups)

    def get_subscribers(self):
        followers = self.response(self.followers_method, self.params.copy())['items']
        friends = self.response(self.friends_method, self.params.copy())['items']
        followers.extend(friends)
        return list(map(int, followers))

    def response(self, url, params):
        params['count'] = 1000
        response = requests.get(url, params).json()
        return response['response']

    def get_groups(self, users, params):
        all_groups = []
        number_of_query = [25 for x in range(len(users) // 25)]
        number_of_query.append(len(users) % 25)
        for i, number in tqdm(enumerate(number_of_query), total=len(number_of_query), desc='Получение всех групп'):
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
                                              users=[*users_slice], v=params['v'], close_bracket='}')
            params['code'] = execute
            groups = self.response(self.execute_method, params)
            for element in groups:
                try:
                    elements_list = [(x['id'], x['screen_name']) for x in element]
                    all_groups.extend(elements_list)
                except TypeError:
                    pass
        return all_groups

    def make_list_of_top_n_groups(self, groups, n):
        list_of_dicts = [{'title': x[1], 'id': x[0], 'count': groups.count(x)} for x in tqdm(set(groups),
                                                                                             desc='Обработка групп')]
        list_of_dicts = sorted(list_of_dicts, key=lambda x: x['count'], reverse=True)
        return list_of_dicts[:n]

    def save_json(self, data):
        with open('groups.json', 'w') as file:
            json.dump(data, file)
        print('Файл успешно сохранен')


target_id = input('Введите id пользователя: ')
user = Celebrity(target_id)
user.save_top_n_subscribers_groups_in_json(10)





