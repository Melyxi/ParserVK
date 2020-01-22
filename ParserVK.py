import json
import requests
import time
import datetime


def write_res(name, data):
    with open(name, 'w') as file:
        file.write(data)


def read_data(name):
    with open(name) as file:
        data_loaded = json.load(file)
    return data_loaded


def save(data, name):
    with open(name, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=2)


class Parser():
    
    
    def __init__(self, __name):
        self.__name = __name 
        self.dict_filter = self.open_file()
        self.my_id = self.dict_filter['id'][0]
        self.access_token = "access_token" # здесь нужен ключ пользователя
        self.my_groups = self.my_groups_func()
        self.save_name = 'parsVK.json'
        
    
    def my_groups_func(self): # метод возвращает группы пользователя       
        access_token = self.access_token
        params = {"user_id": self.my_id, "v": 5.103, "access_token": access_token, "offset": 0, 'count': 1000}
        r = requests.get("https://api.vk.com/method/groups.get", params)
        my_groups = r.json()['response']['items']

        return my_groups
    
    
    def processing(self): # метод возвращает список участников сообщества.
        groups_user = []
        my_groups = self.my_groups
        for group in my_groups:
            new_groups = [1]    
            offset = 0
            group_list = []
            group_dict = {}
            url_getmembers = "https://api.vk.com/method/groups.getMembers"
            access_token = self.access_token
 
            while len(new_groups):
                params = {'group_id': group,
                  'offset': offset,
                  'count': 1000,
                  "v": 5.103,
                  "access_token": access_token,
                  'fields': ['sex, city, country, bdate, relation, can_write_private_message, universities']
                  }

                try:
                    users_group = requests.get(url_getmembers, params)
                    new_groups = users_group.json()['response']['items']
                except:
                    time.sleep(0.35)
                    try:
                        users_group = requests.get(url_getmembers, params)
                        new_groups = users_group.json()['response']['items']
                        
                    except:
                        #print("что то не так ")
                        new_groups = []


                sort_list = self.filter_user(new_groups)
                offset += 1000
                group_list.extend(sort_list)
            group_dict[str(group)] = group_list 
            groups_user.append(group_dict)
            save(groups_user, self.save_name)
            
        del groups_user
        
    
    def print_result(self, number_matches): # печать результата параметр number_matches колличество совпадений
        
        data_loaded = read_data(self.save_name)
        my_groups = self.my_groups
        users = []
        for x, item in enumerate(my_groups):
            try:
                users.extend(data_loaded[x][str(item )]) # здесь мы собираем все id пользователей, которые состоят в группах 
            except:
                continue

        top_tayn = {}
        len_users = len(set(users))
        for i, user in enumerate(set(users), 1):      # создаем множество из юзеров и считаем сколько раз они встречаются в группах
            #print('{:.3f}'.format((i/len_users)*100), '%')
            if users.count(user) > number_matches:
                top_tayn[user] = users.count(user) # формируем количество 
                
        sorted_by_value = sorted(top_tayn.items(), key=lambda kv: kv[1], reverse=True)  # сортируем     
        res = ''
        count = 1
        for i, j in enumerate(sorted_by_value, 1):
            
            if not self.dict_filter['occupation_university'] == '':
                time.sleep(0.3)
                url_getuser = "https://api.vk.com/method/users.get" 
                params = {
                  'user_ids': j[0],
                  "v": 5.103,
                  "access_token": self.access_token,
                  'fields': ['occupation']
                  }
                users = requests.get(url_getuser, params)
                if users.json()['response'][0].get('occupation'): # проверка на то, что человек учится в этом институте 
                    if users.json()['response'][0]['occupation']['type'] == "university":
                        if users.json()['response'][0]['occupation']['id'] in self.dict_filter['occupation_university']:                     
                            strr = f'{count}) https://vk.com/id{j[0]} - {j[1]}'
                            res += (f'{strr}\n')
                            count += 1
                            #print(strr)      
            else:
                strr = f'{count}) https://vk.com/id{j[0]} - {j[1]}'
                res += (f'{strr}\n')
                count += 1
                #print(strr)             
        write_res("result.txt", res) # записываем в файл    


    def open_file(self): # метод считывающий файл 
        self.__name
        dict_filter = {}
        with open(self.__name, 'r') as file:
            lines = file.readlines()
            for line in lines:  
                key = line.split(' ')[0].replace(':','').lstrip(" ").rstrip('\n').rstrip(' ')
                value = line.split(':')[1].lstrip(" ").rstrip('\n').rstrip(' ')
                list_value = [(int(item.lstrip(" ")) if item.lstrip(" ").isdigit() else item.lstrip(" ")) for item in value.split(",")]
                dict_filter[key] = (([int(value)] if value.isdigit() else value) if len(list_value) == 1 else list_value)
                
        return dict_filter

    
    def filter_user(self, new_groups): # фильтрация 
        dict_filter = self.dict_filter
        sort_list = []
        now_year = int(str(datetime.date.today()).split("-")[0])
        age_to = now_year - dict_filter['age_to'][0]
        age_of = now_year - dict_filter['age_of'][0]
        universities = dict_filter['universities']
        relativ = dict_filter['relation']
        city = dict_filter['city']
        country = dict_filter['country']
        sex = dict_filter['sex'][0]

        for item in new_groups:
            if item.get('deactivated') is None: # проверка на бан 
                if str(item['is_closed']) == dict_filter['is_closed'] or dict_filter['is_closed'] == '': # закрыт ли акк
                    if str(item['can_access_closed']) == dict_filter['can_access_closed'] or dict_filter['can_access_closed'] == '': # может ли текущий пользователь видеть профиль
                        if item['can_write_private_message'] == dict_filter['can_write_private_message'][0] or dict_filter['can_write_private_message'] == '': # можно ли написать сообщение 
                            if item.get('universities') is None or (True if universities == '' else bool(set([i['id'] for i in item['universities']]) & set(universities))): # проверка закончил ли пользователь университет 
                                if item['sex'] == sex or sex == '': # проверка на пол
                                    if item.get('relation') is None or (True if relativ == '' else item['relation'] in relativ ): # проверка на статус
                                        try:
                                            if (True if country == '' else item['country']['id'] in country): # проверка на страну
                                                if (True if city == '' else item['city']['id'] in city): #проверка на город
                                                    if item.get("bdate") is not None or not (age_to == '' and age_fo == ''):
                                                        if age_of >= int(item['bdate'].split('.')[-1]) >= age_to or len(item['bdate'].split('.')) == 2: # проверка на возраст это недостаточная проверка 
                                                                                                                                                        #если у человека нет даты он все равно пройдет
                                                            sort_list.append(item['id'])
                                                    else:
                                                        sort_list.append(item['id'])

                                        except:
                                            continue

        return sort_list
        
            
if __name__ == "__main__":
    bot = Parser('inputParser.txt')
    bot.processing() 
    bot.print_result(6) # сохраняет результат больше 6 совпадений 			
                                                                    