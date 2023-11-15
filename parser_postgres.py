import requests
from bs4 import BeautifulSoup
import psycopg2

url = 'https://poetory.ru/all/rating/2'

response = requests.get(url)
bs = BeautifulSoup(response.text,'html.parser')
temp = bs.find_all('div', 'item-text')
print(f'temp = {temp}')
conn = psycopg2.connect(dbname='', user='', password='', host='')
cursor = conn.cursor()

for i in temp:
        stih = i.get_text()
        print(f'stih = {stih}')
        cursor.execute('INSERT INTO public.stihi (stih) VALUES (%s)', (stih,))
conn.commit()
cursor.close()
conn.close()


