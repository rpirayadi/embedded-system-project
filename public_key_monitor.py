import time
import requests

def peek_line(f):
    position = f.tell()
    line = f.readline()
    f.seek(position)
    return line



f = open('./info/public_key', 'r')

f1 = open('./info/device_serial', 'r')
device_serial = f1.read()
f1.close()


f2 = open('./info/private_key', 'r')
private_key = f2.read()
f2.close()


prev_public_key = None

url = 'http://94.101.178.12/api/public_key_update'

try:
    while True:
    
        new_public_key = peek_line(f)
        if prev_public_key != new_public_key:
            
            update_data = {
                'deviceSerial': int(device_serial),
                'privateKey' : private_key,
                'publicKey' : new_public_key}

            print(update_data)
            update_result = requests.patch(url, data = update_data)
            print(update_result)
            print(update_result.text)
            
        
        prev_public_key = new_public_key
        time.sleep(1)
        
except KeyboardInterrupt:
    pass




    