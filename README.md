ToiletTimeTracker: 
  1. Use esp32 to record the time and duration time in the toilet.
  2. Insert this record to the DB.
  3. Adjusting the delay time of HC-SR501.

Setup DB:
  1. CREATE DATABASE live_monitor;
  2. use live_monitor;
  3. CREATE TABLE device_specific_parameters (
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    mac_addr VARCHAR(18) NOT NULL,
    delay_value INT UNSIGNED NOT NULL,
    toilet_id INT
    );
  4. CREATE TABLE toilet (
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    duration INT NOT NULL,
    toilet_id INT NOT NULL,
    mac_addr VARCHAR(18) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    send_notification TINYINT(1) DEFAULT 0
    );
  
Develop an application to utilize this data.
  1. Notify the time and duration of long use of specified toilet.  //handle_toilet_db.py
     ![1707020318050](https://github.com/everschen/SmartThings_ESP/assets/26154786/bdcded74-6bbd-4826-80bc-e1e853714b00)
  2. to be added


![1706414588664](https://github.com/everschen/SmartThings_ESP/assets/26154786/8d40e798-2206-4514-95f6-5f25a7f514b3)
![1706414556272](https://github.com/everschen/SmartThings_ESP/assets/26154786/5cb2536e-847a-4ba3-b9f4-3cd80ef45e4e)
![1706414793034](https://github.com/everschen/SmartThings_ESP/assets/26154786/825a7357-bb59-44eb-8c7f-c3ce32d4f50d)
![1706414770140](https://github.com/everschen/SmartThings_ESP/assets/26154786/434186f7-d286-43fd-a7f0-330af6016b1d)
![1706417981606](https://github.com/everschen/SmartThings_ESP/assets/26154786/a28d8fd4-4b25-4ea5-b719-5f71e501cfc8)
<img width="566" alt="db" src="https://github.com/everschen/SmartThings_ESP/assets/26154786/eda10a73-008b-4da1-a1b5-7b5edc3c3dbc">
