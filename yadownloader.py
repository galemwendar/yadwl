import os
import requests
import sys
import urllib.parse
import humanfriendly
import re
from tqdm import tqdm

if len(sys.argv) < 2:
  print('Usage: yadowmloader  <public_url_from_yandex_disk>')
  sys.exit()

public_url = sys.argv[1]  

def download_file_from_disk(public_url):
  #парсим json
  json_url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}'
  response = requests.get(json_url)
  json_data = response.json()
  api_url = json_data['href']
  #получаем настоящую ссылку
  head = requests.head(api_url)
  download_url = head.headers['Location']
  head = requests.head(download_url)
  file_size = int(head.headers['Content-Length'])
  size = humanfriendly.format_size(file_size)   
  name = head.headers['Content-Disposition'].split(';')[1].split('=')[1]
  name = urllib.parse.unquote(name)
  name = re.sub('^UTF-8\'\'', '', name)
  
  print(name,size)
  
  choice = input('Хотите скачать файл? (y/n): ')
  if choice.lower() != 'y':
    sys.exit()
  
  response = requests.get(download_url,stream=True)
  with open(name, 'wb') as f:
    for data in tqdm(response.iter_content(), total=file_size, unit='B', unit_scale=True):
       f.write(data)
    
  print(f'Файл {name} скачан')

if __name__ == '__main__':
  public_url = sys.argv[1]
  
  download_file_from_disk(public_url)
