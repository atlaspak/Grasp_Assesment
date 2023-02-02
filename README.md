# Sensor Data API

This project aims to receive sensor data, process it for future use and return acquired data when called for.

API has 4 endpoints:

| Endpoint        | Parameter           | Returns  |
| ------------- |:-------------:| -----:|
| http://127.0.0.1:8080/send-data | Google Cloud Pub/Sub message | none |
| http://127.0.0.1:8080/get-sensors | none | list of sensors |
| http://127.0.0.1:8080/get-sensor-data | sensor_id | data of given sensor |
| http://127.0.0.1:8080/get-sensor-range-data | sensor_id, start, end | data between given time interval for a sensor |

## Used libraries and why;
- Flask: Because it's simple. Provides all essential tools for this project https://github.com/pallets/flask
- TinyDB: I didn't want to use any external dependencies. https://github.com/msiemens/tinydb

## DB Selection
 I need to explain why I couldn't decide which database to use. I need more input about:
 - Frequency of the data
 - Kind of queries that the user needs
 - How to structurize the data

My initial instinct for this database is to use the Relational DB model since all the data is array-like
and each row is linked to a unique sensor. Easy to query for user-defined time frames.
The relational model seems like the best option

The second option could be using of Redis
if the data frequency is too high and immediately processed data is important for the customer;
run time efficiency would be our first goal, then we could discuss data persistency

The third option could be NoSQL
If a customer needs more refined data, Categorization and flexibility would be our main focus, for instance;
every day between 11:00 to 13:00 is the peak hour frame and customers are mostly interested in this period. 
We could categorize the day into 3 (or more) parts. ([Before 11], [11 - 13], [After 13])

Since my example data is clear enough, for the sake of simplicity and readability.
I used a library called Tinydb which provides some basic query functionality and stores 
data as JSON file.

## Usage
```
cd Api
pip install -r /path/to/requirements.txt
python main.py
```

### Data Generation
To populate the data: After running the API, you can use PubSubSim which provides Pub/Sub message like messages from csv file. This operation populates the DB.
```
cd PubSubSim
pip install requests
python data_sender.py
```
### Tests
Tests are exported from Postman (V2.1). So to test this API, Postman is required. https://github.com/postmanlabs
