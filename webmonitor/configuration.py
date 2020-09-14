"""
Provides configuration models and parse function for YAML config file
"""
from dataclasses import dataclass
from typing import List

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

CONFIG_TEMPLATE = \
"""kafka:
  host: localhost
  port: 9092
  ssl_cafile: /path/to/ca.pem
  ssl_certfile: /path/to/service.cert
  ssl_keyfile: /path/to/service.key
  topic: webmonitor
  consumer_group: webmonitor_saver01

postgresql:
  host: localhost
  port: 5432
  database: defaultdb
  username: username
  password: password
  sslmode: require
  table_prefix: webmonitor

websites:
  - url: https://google.com
    regexp: '.*'
    interval: 1
  - url: https://aiven.com
    interval: 10
  - url: https://goooogle.com
    regexp: '^NEVERMATCH$'
"""


@dataclass
class KafkaConfig:
    """Kafka configuration parameters model"""
    host: str
    port: int
    ssl_cafile: str
    ssl_certfile: str
    ssl_keyfile: str
    topic: str = 'webmonitor'
    consumer_group: str = 'webmonitor_saver01'

    @property
    def host_port(self):
        """host:port string"""
        return "%s:%s" % (self.host, self.port)


@dataclass
class PostgreSQLConfig:
    """PostgreSQL configuration parameters model"""
    host: str
    port: int
    database: str
    username: str
    password: str
    sslmode: str = 'require'
    table_prefix: str = 'webmonitor'

    @property
    def dsn(self):
        """Posgresql connection DSN"""
        return "postgres://%s:%s@%s:%s/%s?sslmode=%s" % (
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
            self.sslmode,
        )


@dataclass
class WebSiteRules:
    """WebSites monitoring rules"""
    url: str
    regexp: str = None
    interval: int = 10


@dataclass
class WebMonitorConfig:
    """Application configuration model"""
    kafka: KafkaConfig
    postgresql: PostgreSQLConfig
    websites: List[WebSiteRules]


def parse_config(filename: str) -> WebMonitorConfig:
    """Parse config file and return WebMonitorConfig"""

    with open(filename, 'r') as config_file:
        data = load(config_file, Loader=Loader)

    kafka_config = KafkaConfig(**data['kafka'])
    postgresql_config = PostgreSQLConfig(**data['postgresql'])
    website_rules = [WebSiteRules(**website) for website in data['websites']]

    return WebMonitorConfig(kafka_config, postgresql_config, website_rules)
