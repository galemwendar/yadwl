import os
import aiohttp
import aiofiles
import asyncio
from tqdm import tqdm
import sys
import urllib.parse
import humanfriendly
import re
from tqdm import tqdm
import requests

async def download_file(download_url,name):
  async with aiohttp.ClientSession() as session:
    async with session.get(download_url) as response:
    
      # получаем контент
      data = await response.read()  
      # открываем файл асинхронно
      async with aiofiles.open(name, 'wb') as f:
        # делим данные на чанки для имитации прогресс-бара
        chunk_size = 512
        num_chunks = int(len(data)) // chunk_size + 1
        chunks = split_in_chunks(data, chunk_size)
        #int_num_chunks = int(num_chunks)  
        for chunk in tqdm(chunks, total=num_chunks):
          await f.write(chunk)

#имитация прогресс-бара
def split_in_chunks(data, chunk_size):
  num_chunks = int(len(data)) // chunk_size + 1
  for i in range(num_chunks):
    start = i * chunk_size
    end = (i+1) * chunk_size
    yield data[start:end]

#получение прямой ссылки из JSON
def get_api_url(public_url):
  if len(sys.argv) < 2:
    print('Usage: yadowmloader  <public_url_from_yandex_disk>')
    sys.exit()
  
  api_url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}'
  response = requests.get(api_url)
  return response.json()['href']

def get_metadata(download_url):
  head = requests.head(download_url)
  file_size = int(head.headers['Content-Length'])
  size = humanfriendly.format_size(file_size)
  name = head.headers['Content-Disposition'].split(';')[1].split('=')[1]
  name = urllib.parse.unquote(name)
  name = re.sub('^UTF-8\'\'', '', name)
  print(name,size)
  return name

def confirm_download():
  choice = input('Хотите скачать файл? (y/n): ')
  if choice.lower() != 'y':
    sys.exit()  
  
#обходим редирект
def get_download_url(api_url):
  head = requests.head(api_url)
  return head.headers['Location']
  
if __name__ == '__main__':
  public_url = sys.argv[1]
  
  # получаем данные из API
  api_url = get_api_url(public_url) 
  # извлекаем ссылку для скачивания
  download_url = get_download_url(api_url)
  #выводим имя, размер файла
  name = get_metadata(download_url)
  #спрашиваем разрешение на скачивание
  confirm_download()
  # вызываем асинхронное скачивание
  asyncio.run(download_file(download_url,name))
