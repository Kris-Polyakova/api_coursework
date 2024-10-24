import requests
import json
import os.path
from dotenv import load_dotenv
from pprint import pprint
from tqdm import tqdm


class Connect_vk:
    def __init__(self, access_token, version ='5.199'):
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.access_token,
            'v': self.version
            }
       
    def get_photo(self, user_id, count=5):
        url = f'{self.base_url}photos.get'
        params = {
            **self.params,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': count
            }
        response = requests.get(url, params=params)
        return response.json()
        

class Connect_yandex:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Authorization': 'OAuth ' + str(self.access_token)
            }
        
    def create_path(self, path_name):
        url = self.base_url
        headers = self.headers
        params = {
            'path': '/' + str(path_name)
            }
        requests.put(url, params=params, headers=headers)
    
    def upload_photos(self, path_name, photo_name, photo_url):
        url = f'{self.base_url}/upload'
        headers = self.headers
        params = {
            'url': photo_url,
            'path': f'/{path_name}/{photo_name}'
            }
        response = requests.post(url, params=params, headers=headers)
                 

def get_config(path=str):
    dotenv_path = path
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        
    ya_token = os.getenv('ya_token')
    vk_token = os.getenv('vk_token')
    vk_id = os.getenv('vk_id')
    
    return ya_token, vk_token, vk_id

def backup_profile_photos(vk_id, ya_token):
    vk = Connect_vk(get_config('config.env')[1])
    user_data = vk.get_photo(vk_id)
    photos = {}
    save_files = []
    
    for values in user_data['response']['items']:
        photo_dict = {}
        name = str(values['likes']['count'])
        
        if name in photos:
            name = str(name) + str(values['date'])
            
        photo_dict['name'] = name
        photo_dict['size'] = values['orig_photo']['type']
        photo_url = values['orig_photo']['url']
        photos[name]=photo_url
        save_files.append(photo_dict)
   
    yandex = Connect_yandex(ya_token)
    yandex.create_path('VK_Profile_Images')
    
    for photo in tqdm(photos.items()):
        yandex.upload_photos('VK_Profile_Images', photo[0], photo[1])
        
    with open ('photo_info.json', 'w', encoding='utf-8') as file:
        json.dump(save_files, file, ensure_ascii=False, indent=2)
     
        
backup_profile_photos(get_config('config.env')[2], get_config('config.env')[0])

