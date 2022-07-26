import requests
import psycopg2
import time


def connect_to_database():
    connection = None
    try:
        connection = psycopg2.connect(user = 'pi',
                                      password = '1234',
                                      host = 'localhost',
                                      port = '5432',
                                      database = 'data')
        
        cur = connection.cursor()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return connection, cur


def select_from_database():
    sql = """SELECT * FROM unsent_data
            LIMIT 1"""
    connection, cur = connect_to_database()
    
    if connection is not None:
        cur.execute(sql)
        row = cur.fetchall()
        
        connection.commit()
        cur.close()
        connection.close()
        
        return row
    
def delete_from_database(data_key, date):
    sql = """ DELETE FROM unsent_data
        WHERE  data_key = (%s) and date = (%s)"""
    connection, cur = connect_to_database()
    
    if connection is not None:
        cur.execute(sql, (data_key, date))
        
        connection.commit()
        cur.close()
        connection.close()
        

def check_status_code(status_code):
    if status_code == 200:
        return True
    else:
        return False
    
def check_server():
    url = 'http://94.101.178.12/api/ping'
    response = requests.get(url)
    return check_status_code(response.status_code)


f1 = open('./info/device_serial', 'r')
device_serial = f1.read()
f1.close()


f2 = open('./info/private_key', 'r')
private_key = f2.read()
f2.close()

def send_data(row):
    url = 'http://94.101.178.12/api/post'

    sensor_data = {
            'deviceSerial': int(device_serial),
            'privateKey' : private_key,
            'timeInstant' : row[2],
            'dataKey': row[0],
            'dataValue' : row[1]}
    
    result = requests.post(url, data = sensor_data)
    if check_status_code(result.status_code):
        delete_from_database(row[0], row[2])
    


try:
    while True:
        while check_server():
            row = select_from_database()
            if len(row) != 0:
                send_data(row[0])
            else:
                break
            
        time.sleep(1)
        
        
except KeyboardInterrupt:
    pass



