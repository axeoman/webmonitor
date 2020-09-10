"""SQL queries for postgresql database"""

INIT_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS {prefix}_metrics
(
id SERIAL PRIMARY KEY,
status_code SMALLINT NOT NULL,
response_time INT,
regexp_id INT NULL,
FOREIGN KEY (regexp_id) REFERENCES {prefix}_regexp (id),
regexp_matched BOOLEAN NULL,
time TIMESTAMP NOT NULL
)
"""

INIT_REGEXP_TABLE = """
CREATE TABLE IF NOT EXISTS {prefix}_regexp 
(
id SERIAL PRIMARY KEY,
pattern VARCHAR(128) NOT NULL UNIQUE
)
"""

INSERT_METRICS_RESULT = """
INSERT INTO {prefix}_metrics
(status_code, response_time, regexp_id, regexp_matched, time)
VALUES 
(%s, %s, %s, %s, %s)
"""

INSERT_REGEXP_RESULT = """
INSERT INTO {prefix}_regexp
(pattern) VALUES (%s)
ON CONFLICT DO NOTHING
RETURNING id;
"""

SELECT_REGEXP = """SELECT * FROM {prefix}_regexp 
WHERE pattern = %s"""
