import os
import subprocess
import aiohttp
import aiohttp
import aiofiles
import asyncio
from tqdm import tqdm
import sys
import urllib.parse
import humanfriendly
import re
import requests
from pathlib import Path

def check_python_installation():
    try:
        subprocess.run(["python", "--version"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Python not installed")
        return False

def create_and_prepare_virtual_environment():
    # Создание виртуальной среды
    env_path = "./my_venv"
    if not os.path.exists(env_path):
        print("Creating virtual environment...")
        path_to_python = f"{env_path}\\Scripts\\python.exe" if os.name == "nt" else f"{env_path}/bin/python3"
        
        subprocess.run(["python", "-m", "venv", env_path])
        print(f"Virtual environment created at {env_path}")
        
        # Установка нужных библиотек
        print("Installing required packages...")
        packages = ["aiohttp", "aiofiles", "tqdm", "humanfriendly"]

        subprocess.run([path_to_python, "-m", "pip", "install"] + packages)

async def download_file(session, download_url, name, output_dir=None):
    if output_dir:
      # Проверка существования каталога
        if not os.path.exists(output_dir):
          print(f"Error: The directory {output_dir} does not exist.")
          return
        output_path = Path(output_dir) / name
    else:
        output_path = name
    async with session.get(download_url,timeout=600) as response:
        total = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total, ncols=70, unit='B', unit_scale=True,
                                    unit_divisor=1024, file=sys.stdout)
        async with aiofiles.open(output_path, 'wb') as f:
            chunk_size = 512 * 1024
            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                progress_bar.update(len(chunk))
                await f.write(chunk)
        progress_bar.close()

async def main():
    if len(sys.argv) < 2:
        print('Usage: yadwl <public_url_from_yandex_disk> <optional/path/to/directory>')
        sys.exit()

    public_url = sys.argv[1]
    output_dir = sys.argv[2]
    
    create_and_prepare_virtual_environment()
    api_url = get_api_url(public_url)
    download_url = get_download_url(api_url)
    name = get_metadata(download_url)
    
    choice = input('Хотите скачать файл? (y/n): ')
    if choice.lower() == 'y':
        async with aiohttp.ClientSession() as session:
            await download_file(session, download_url, name, output_dir)
    

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
  
#обходим редирект
def get_download_url(api_url):
  head = requests.head(api_url)
  return head.headers['Location']
  
if __name__ == '__main__':
    if not check_python_installation():
       exit(1)
    asyncio.run(main())
