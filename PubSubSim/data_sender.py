import requests
from datetime import datetime
import csv
import base64
import json
import time

url = "http://127.0.0.1:8080/send-data"

def get_data_from_csv(path_to_csv):
    result = []
    row_names = []
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                row_names = row
                line_count += 1
            else:
                aRow = {}
                for index, data in enumerate(row):
                    aRow[row_names[index]] = data
                encodedRow = base64.b64encode(json.dumps(aRow).encode('utf-8'))
                encodedRow = encodedRow.decode('utf-8')
                result.append(encodedRow)
                line_count += 1
    return result

def start_test():
    data = get_data_from_csv('data.csv')
    id = 1
    for line in data:
        now = datetime.now().isoformat()
        payload = {}
        payload["message"] = {}
        payload["message"]["attributes"] = {}
        payload["message"]["attributes"]["key"] = "value"
        payload["message"]["data"] = line
        payload["message"]["messageId"] = id
        payload["message"]["message_id"] = id
        payload["message"]["publishTime"] = now
        payload["message"]["publish_time"] = now
        payload["subscription"] = "projects/myproject/subscriptions/mysubscription"
        payload = json.dumps(payload)
        payload = payload.encode('utf-8')
        response = requests.post(url, payload, headers={'Content-Type': 'text/plain'})
        time.sleep(0.1)
        print(response)

if __name__ == '__main__':
    start_test()