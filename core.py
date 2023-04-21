import vk_api
import datetime

class VkTools:
    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)
    
    """Получение инфо о пользователе бота"""
    def get_profile_info(self, user_id):
        info = self.ext_api.method('users.get', 
                                   {'user_id': user_id,
                                    'fields': 'bdate,city,sex,relation'
                                   })
        return info

    """На основе инфо о пользователе
    создается словарь с параметрами поиска
    подходящих аккаунтов вк: город, возраст от,
    возраст до, пол, сдвиг (по списку выдачи от вк)"""
    def get_search_parametres(self, info):        
        search_params_dict = {}

        search_params_dict['city_id'] = info[0]['city']['id']

        user_bdate = info[0]['bdate']        
        user_bdate_list = user_bdate.split('.')
        byear = int(user_bdate_list[2])
        bmonth = int(user_bdate_list[1])
        bday = int(user_bdate_list[0])
        today = datetime.date.today()
        age = today.year - byear
        if bmonth >= today.month and bday > today.day:
            age -= 1        
        search_params_dict['age_from'] = age - 2
        search_params_dict['age_to'] = age + 2        

        if info[0]['sex'] == 2:
            search_params_dict['sex'] = 1
        else:
            search_params_dict['sex'] = 2

        search_params_dict['offset'] = 0

        return search_params_dict

    """Поиск пользователей по параметрам из словаря выше"""
    def user_search(self, city_id, age_from, age_to, sex, offset):
        profiles = self.ext_api.method('users.search', 
                                       {'city_id': city_id,
                                        'age_from': age_from,
                                        'age_to': age_to,
                                        'sex': sex,
                                        'count': 30,
                                        'offset': offset,
                                        'fields': 'relation'
                                        })
        res = [i for i in profiles['items'] if 'relation' in i.keys() and i['relation'] in [0, 1, 6]]
        return res
    
    """У тех людей, которые подошли по требованиям пользователю, получать 
    топ-3 популярных фотографии профиля и отправлять их пользователю в
    чат вместе со ссылкой на найденного человека.
    Популярность определяется по количеству лайков и комментариев."""
    def get_photos(self, user_id):
        info = self.ext_api.method('photos.get', 
                                   {'album_id': 'profile',
                                    'owner_id': user_id,
                                    'extended': 1
                                   })
        photos_list = []

        for item in info['items']:
            photo_dict = {}
            photo_dict['owner_id'] = user_id
            photo_dict['id'] = item['id']
            photo_dict['likes'] = item['likes']['count']            
            photos_list.append(photo_dict)

        """сортировка по кол-ву лайков"""
        photos_list.sort(key=lambda dictionary: dictionary['likes'], reverse=True)
        
        """если у пользователя больше 3х фото в профиле, 
        оставляем три первых в отсортированном списке"""
        if len(photos_list) > 3:
            photos_list = photos_list[0:3]

        return photos_list
