import sys
import requests
import Adafruit_DHT
import time
import serial
import string
import psycopg2


sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
    sys.exit(1)
    
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

def insert_into_database(data_key, data_value, date):
    sql = """INSERT INTO unsent_data
             VALUES(%s, %s, %s)"""

    connection, cur = connect_to_database()
    
    if connection is not None:
        cur.execute(sql, (data_key, data_value, date))
        connection.commit()
        cur.close()
        connection.close()
            
    
def check_status_code(status_code):
    if status_code == 200:
        return True
    else:
        return False
    
def send_or_save_data(url, sensor_data):
    print(sensor_data)
    result = requests.post(url, data = sensor_data)
    if not check_status_code(result.status_code):
        print('Couldnt send Data. Data was saved in database')
        insert_into_database(sensor_data['dataKey'], sensor_data['dataValue'], sensor_data['timeInstant'])


f1 = open('./info/device_serial', 'r')
device_serial = f1.read()
f1.close()


f2 = open('./info/private_key', 'r')
private_key = f2.read()
f2.close()


ser=serial.Serial('/dev/ttyACM0', 9600)

url = 'http://94.101.178.12/api/post'
try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity == None or temperature == None:
            print('Data Read Failed')
            continue
        
        print('Data Read Finish')
        
        water_level = int(ser.readline().strip())
        
        temp_data = {
                    'deviceSerial': int(device_serial),
                    'privateKey' : private_key,
                    'timeInstant' : int(time.time() * 1000),
                    'dataKey': 'Temp',
                    'dataValue' : temperature}
        hum_data = {
                    'deviceSerial': int(device_serial),
                    'privateKey' : private_key,
                    'timeInstant' : int(time.time() * 1000),
                    'dataKey': 'Hum',
                    'dataValue' : humidity}
        
        lev_data = {
                    'deviceSerial': int(device_serial),
                    'privateKey' : private_key,
                    'timeInstant' : int(time.time() * 1000),
                    'dataKey': 'Lev',
                    'dataValue' : water_level}

        
        send_or_save_data(url, temp_data)
        send_or_save_data(url, hum_data)
        send_or_save_data(url, lev_data)
        
               
        time.sleep(10)
        
except KeyboardInterrupt:
    pass
