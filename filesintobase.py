import psycopg2
conn = psycopg2.connect(dbname='', user='', password='', host='')
cursor = conn.cursor()
i=1
while i<17:
    text=rf'C:\Program Files\PostgreSQL\15\data\valentines\{i}.jpg'
    cursor.execute('INSERT INTO public.valentines (valentines) VALUES (%s)', (text,))
    i+=1
print('все')
cursor.close()
conn.commit()
conn.close() 
