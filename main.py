import requests
import json
from tqdm import tqdm


class Celebrity:

    __followers_method = 'https://api.vk.com/method/users.getFollowers'
    __friends_method = 'https://api.vk.com/method/friends.get'
    __groups_method = 'https://api.vk.com/method/groups.get'
    __execute_method = 'https://api.vk.com/method/execute'
    __access_token = ''
    __version = '5.52'

    def __init__(self, id):
        self.id = id
        self.params = dict(access_token=self.__access_token, v=self.__version, user_id=self.id)

    def save_top_n_subscribers_groups_in_json(self, n):
        subscribers = self.get_subscribers()
        groups = self.get_groups(subscribers, self.params)
        top_n_groups = self.make_list_of_top_n_groups(groups, n)
        with open('groups.json', 'w') as file:
            json.dump(top_n_groups, file)
        print('Файл успешно сохранен')

    def get_subscribers(self):
        followers = self.response(self.__followers_method, self.params)['items']
        friends = self.response(self.__friends_method, self.params)['items']
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
            groups = self.response(self.__execute_method, params)
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


target_id = input('Введите id пользователя: ')
user = Celebrity(target_id)
user.save_top_n_subscribers_groups_in_json(10)





