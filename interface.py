import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import access_token, community_token
from core import VkTools
from data_store import Vkinder_viewed_id, insert_data, session

class BotInterface:
    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)

    """Функция для отправки ботом текстового сообщения"""
    def message_send(self, user_id, message):
        self.bot.method('messages.send', 
                        {'user_id': user_id, 
                         'message': message, 
                         'random_id': get_random_id()})

    """Функция для отправки ботом медиа файла"""
    def photo_send(self, user_id, attachment):
        self.bot.method('messages.send', 
                        {'user_id': user_id, 
                         'attachment': attachment, 
                         'random_id': get_random_id()})
    
    """Основная функция работы бота"""
    def handler(self):
        longpoll = VkLongPoll(self.bot)        
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                if event.text.lower() == 'привет':
                    self.message_send(event.user_id, 
                                      'Привет! Чтобы начать, отправь слово "поиск"')

                elif event.text.lower() == 'поиск':    
                    tools = VkTools(access_token)
                    info = tools.get_profile_info(event.user_id)
                    search_params_dict = tools.get_search_parametres(info)
                    res = tools.user_search(**search_params_dict)

                    for item in res:
                        if item['is_closed'] == False:
                            id = item['id']
                            photos_list = tools.get_photos(id)

                            if photos_list != []:
                                for i in photos_list:
                                    attachment = f"photo{id}_{i['id']}"
                                    self.photo_send(event.user_id, attachment)
                                url = f"https://vk.com/{id}"
                                self.message_send(event.user_id, url)

                            insert_data(event.user_id, id)
                    
                    for item in session.query(Vkinder_viewed_id):
                        print(item)

                    self.message_send(event.user_id, 
                                      'Чтобы продолжить просмотр, отправь слово "далее"')

                elif event.text.lower() == 'далее':
                    search_params_dict['offset'] += 30

                    res = tools.user_search(**search_params_dict)
                    print(res)

                    for item in res:
                        if item['is_closed'] == False:
                            id = item['id']

                            results = session.query(Vkinder_viewed_id).\
                                filter(Vkinder_viewed_id.user_id == event.user_id, \
                                       Vkinder_viewed_id.viewed_id == id).all()
                            
                            if results == []:
                                photos_list = tools.get_photos(id)

                                if photos_list != []:
                                    for i in photos_list:
                                        attachment = f"photo{id}_{i['id']}"
                                        self.photo_send(event.user_id, attachment)
                                    url = f"https://vk.com/{id}"
                                    self.message_send(event.user_id, url)

                                insert_data(event.user_id, id)
                            
                            else:
                                self.message_send(event.user_id, "Уже показывал")

                    for item in session.query(Vkinder_viewed_id):
                        print(item)
  
                else: 
                    self.message_send(event.user_id, 
                                      'Неизвестная команда. Чтобы продолжить просмотр, отправь слово "далее"')

if __name__ == "__main__":
    my_bot = BotInterface(token=community_token)
    my_bot.handler()