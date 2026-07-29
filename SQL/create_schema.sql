CREATE TABLE IF NOT EXISTS earthquakes (
    id SERIAL PRIMARY KEY,
    magnitude VARCHAR(50),
    depth VARCHAR(50),
    longitude VARCHAR(50),
    latitude VARCHAR(50),
    time VARCHAR(100),
    place VARCHAR(255),
    source VARCHAR(50)
);