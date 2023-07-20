drop table if exists test_to_battery, test_table, data_table, battery_table, testdata;

CREATE TABLE battery_table (
    battery_id SERIAL PRIMARY KEY,
    attribute1 TEXT,
    attribute2 TEXT,
    attribute3 TEXT,
    attribute4 TEXT,
    attribute5 TEXT,
    date_made DATE
);

CREATE TABLE data_table (
    data_id SERIAL PRIMARY KEY,
    testtype TEXT,
    time DOUBLE PRECISION,
    volts DOUBLE PRECISION,
    current DOUBLE PRECISION,
    power DOUBLE PRECISION,
    c_rate DOUBLE PRECISION,
    cycle_number INTEGER,
    date DATE
);

CREATE TABLE test_table (
    test_id  INTEGER,
    battery_id INTEGER REFERENCES battery_table(battery_id),
    data_id INTEGER REFERENCES data_table(data_id)
);