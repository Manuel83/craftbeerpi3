CREATE TABLE kettle
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    sensor VARCHAR(80),
    heater VARCHAR(10),
    automatic VARCHAR(255),
    logic VARCHAR(50),
    config VARCHAR(1000),
    agitator VARCHAR(10),
    target_temp INTEGER,
    height INTEGER,
    diameter INTEGER
);

CREATE TABLE step
(
    id INTEGER PRIMARY KEY NOT NULL,
    "order" INTEGER,
    name VARCHAR(80),
    type VARCHAR(100),
    stepstate VARCHAR(255),
    state VARCHAR(1),
    start INTEGER,
    end INTEGER,
    config VARCHAR(255),
    kettleid INTEGER
);

CREATE TABLE sensor
(
    id INTEGER PRIMARY KEY NOT NULL,
    type VARCHAR(100),
    name VARCHAR(80),
    config VARCHAR(500),
    hide BOOLEAN
);

CREATE TABLE fermenter_step
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    hours INTEGER,
    minutes INTEGER,
    days INTEGER,
    temp INTEGER,
    direction VARCHAR(1),
    "order" INTEGER,
    state VARCHAR(1),
    start INTEGER,
    timer_start INTEGER,
    end INTEGER,
    fermenter_id INTEGER,
    FOREIGN KEY (fermenter_id) REFERENCES fermenter (id)
);

CREATE TABLE fermenter
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    brewname VARCHAR(80),
    sensor VARCHAR(80),
    sensor2 VARCHAR(80),
    sensor3 VARCHAR(80),
    heater VARCHAR(10),
    logic VARCHAR(50),
    config VARCHAR(1000),
    cooler VARCHAR(10),
    target_temp INTEGER
);

CREATE TABLE config
(
    name VARCHAR(50) PRIMARY KEY NOT NULL,
    value VARCHAR(255),
    type VARCHAR(50),
    description VARCHAR(255),
    options VARCHAR(255)
);


INSERT INTO config VALUES ('kettle_cols', 4, 'select', 'Adjust the width of a kettle widget on the brewing dashboard', '[1,2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12]');
INSERT INTO config VALUES ('actor_cols', 4, 'select', 'Adjust the width of a actor widget on the brewing dashboard', '[1,2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12]');
INSERT INTO config VALUES ('sensor_cols', 4, 'select', 'Adjust the width of a sensor widget on the brewing dashboard', '[1,2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12]');
INSERT INTO config VALUES ('unit', 'C', 'select', 'Temperature Unit', '["C","F"]');
INSERT INTO config VALUES ('brewery_name', 'My Home Brewery', 'text', 'Your brewery name', NULL );
INSERT INTO config VALUES ('buzzer', 16, 'select', 'Buzzer GPIO', '[16,17,18,19,20]');
INSERT INTO config VALUES ('setup', 'YES', 'select', 'Show the Setup dialog', '["YES","NO"]');

CREATE TABLE actor
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(50),
    type VARCHAR(100),
    config VARCHAR(500),
    hide BOOLEAN
);