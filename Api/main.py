import base64
import json
from tinydb import TinyDB, Query
from flask import Flask, request, Response
from datetime import datetime

####################################### DB OPERATIONS #######################################

# I need to explain why I couldn't decide which database to use. I need more input about:
# - frequency of the data
# - kind of queries that user needs
# - how to structurize the data

# my initial instict for this database is to use Relational DB model since all the data is array-like
# and each row linked to a uniqe sensor. Easy to query for for user defined time frames.
# Relations model seems like the best option

# The second option could be using of Redis
# if the data frequency is too high and immediate processed data is important for the customer;
# run time efficiency would be our first goal, then we could discuss data persistency

# The third option could be NoSQL
# If customer needs more refined data, Categorization and flexibility would be our main focus, for instance;
# every day between 11:00 to 13:00 is peak hour frame and customer mostly interest in this period. 
# We could categorize day into 3 (or more) parts. ([Before 11], [11 - 13], [After 13])

# Since my example data is clear enough, for the sake of simplicity and readability.
# I used a library called Tinydb which provides some basic query functionalty and stores 
# data as json file


sensor_db = TinyDB('sensor_db.json')

def convert_to_timestamp(time_iso):
    time_epoch = datetime.fromisoformat(time_iso)
    return time_epoch.timestamp()

def record_data(data):
    sensor_id = data['v0']
    time_iso = data['Time']
    sensor_value = data['v18']
    time_epoch = convert_to_timestamp(time_iso)
    sensor_table = sensor_db.table(sensor_id)
    sensor_table.insert(
        {
            'val': sensor_value,
            'ts': time_epoch
        }
    )

def fetch_sensor_data(sensor_id):
    ret_val = []
    sensor_data = sensor_db.table(sensor_id).all()
    for data in sensor_data:
        time = datetime.fromtimestamp(data['ts']).isoformat()
        ret_val.append((time, data['val']))
    return json.dumps(ret_val)

def fetch_range_sensor_data(sensor_id, start_time, end_time):
    ret_val = []
    start_ts = convert_to_timestamp(start_time)
    end_ts = convert_to_timestamp(end_time)
    query = Query()

    sensor_data = sensor_db.table(sensor_id).search(
        (query.ts > start_ts) & (query.ts < end_ts)
    )

    for data in sensor_data:
        time = datetime.fromtimestamp(data['ts']).isoformat()
        ret_val.append((time, data['val']))
    return json.dumps(ret_val)

def fetch_sensor_list():
    return json.dumps(list(sensor_db.tables()))




####################################### API #######################################

app = Flask(__name__)

# This endpoints sends data to DB format must comply with the Google Cloud Pub/Sub message format
# returns only http codes
@app.route("/send-data", methods = ['POST'])
def set_sensor_data():
    try:
        envelope = json.loads(request.data.decode('utf-8'))
        payload = base64.b64decode(envelope['message']['data'])
        data = json.loads(payload)
        record_data(data)
        return 'OK', 200
    
    except Exception as e:
        return f"Faulty input and error:{e}", 400

# no input needed
# returns the list of sensors as json
@app.route("/get-sensors", methods = ['GET'])
def get_sensors():
    sensor_list = fetch_sensor_list()
    if sensor_list:
        response = Response(sensor_list, status = 201, mimetype='application/json')
    else:
        response = Response("No data found.", status = 204)
    return response

# input: <sensor_id>
# returns all data related to the input sensor as json
@app.route("/get-sensor-data", methods = ['GET'])
def get_processed_sensor_data():
    sensor_id = request.args.get('id')
    data = fetch_sensor_data(str(sensor_id))
    if data:
        response = Response(data, status = 201, mimetype='application/json')
    else:
        response = Response("No data found.", status = 204)
    return response

# input <sensor_id>
# input <start_date>
# input <end_date>
# returns range data between start_date and end_date for a particular sensor as json
@app.route("/get-sensor-range-data", methods = ['GET'])
def get_processed_sensor_range_data():
    sensor_id = request.args.get('id')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    data = fetch_range_sensor_data(sensor_id, start_time, end_time)
    if data:
        response = Response(data, status = 201, mimetype='application/json')
    else:
        response = Response("No data found.", status = 204)
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
