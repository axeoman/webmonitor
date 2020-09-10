"""SQL queries for postgresql database"""

INIT_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS {prefix}_metrics
(
id SERIAL PRIMARY KEY,
time TIMESTAMP NOT NULL,
url_id INT NOT NULL,
connection_error BOOLEAN NULL,
status_code SMALLINT NULL,
response_time INT NULL,
regexp_id INT NULL,
regexp_matched BOOLEAN NULL,
FOREIGN KEY (url_id) REFERENCES {prefix}_urls (id),
FOREIGN KEY (regexp_id) REFERENCES {prefix}_regexps (id)
)
"""

INIT_REGEXPS_TABLE = """
CREATE TABLE IF NOT EXISTS {prefix}_regexps
(
id SERIAL PRIMARY KEY,
pattern VARCHAR(128) NOT NULL UNIQUE
)
"""

INIT_URLS_TABLE = """
CREATE TABLE IF NOT EXISTS {prefix}_urls
(
id SERIAL PRIMARY KEY,
url VARCHAR(512) NOT NULL UNIQUE
)
"""

INSERT_METRICS_RESULT = """
INSERT INTO {prefix}_metrics
(url_id, status_code, response_time, regexp_id, regexp_matched, connection_error, time)
VALUES 
(%s, %s, %s, %s, %s, %s, %s)
"""

INSERT_REGEXP = """
INSERT INTO {prefix}_regexps
(pattern) VALUES (%s)
RETURNING id;
"""

INSERT_URL = """
INSERT INTO {prefix}_urls
(url) VALUES (%s)
RETURNING id;
"""

# Have to do this because `ON CONFLICT DO NOTHING RETURNING id`
# returns NULL when no entry was updated
SELECT_REGEXPS = """SELECT * FROM {prefix}_regexps
WHERE pattern = %s"""

SELECT_URLS = """SELECT * FROM {prefix}_urls
WHERE url = %s"""
