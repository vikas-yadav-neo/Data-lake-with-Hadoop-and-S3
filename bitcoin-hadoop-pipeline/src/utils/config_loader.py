import yaml
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / 'config.yaml'


def load_config(path: Path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)


@dataclass
class RPCConfig:
    user: str
    password: str
    host: str
    port: int
    url: str


@dataclass
class ZMQConfig:
    port: int


@dataclass
class LoggingConfig:
    json_file: str
    poll_interval: int
    log_dir: str


@dataclass
class DBInstanceConfig:
    host: str
    port: int
    name: str
    user: str
    password: str


@dataclass
class WalletConfig:
    addresses: List[str]


@dataclass
class ElectrumInstanceConfig:
    host: str
    port: int
    use_ssl: bool
    retry_delay: int


@dataclass
class KafkaConfig:
    host: str
    port: int
    bootstrap_servers: str
    security_protocol: str
    acks: str
    topics: Dict[str, str]

@dataclass
class SchemaRegistryConfig:
    host: str
    port: int


@dataclass
class HadoopConfig:
    url: str
    user: str
    password: str = None

@dataclass
class MongoConfig:
    url: str
    database: str


@dataclass
class InfluxConfig:
    token: str


@dataclass
class AppConfig:
    rpc: RPCConfig
    zmq: ZMQConfig
    logging: LoggingConfig
    database: DBInstanceConfig
    wallet: WalletConfig
    electrum: ElectrumInstanceConfig
    kafka: KafkaConfig
    schema_registry: SchemaRegistryConfig
    mongo: MongoConfig
    influx: InfluxConfig
    hadoop: HadoopConfig


def build_config(data: dict) -> AppConfig:
    return AppConfig(
        rpc=RPCConfig(**data['rpc']),
        zmq=ZMQConfig(**data['zmq']),
        logging=LoggingConfig(**data['logging']),
        database=DBInstanceConfig(**data['postgres']),
        wallet=WalletConfig(**data['wallet']),
        electrum=ElectrumInstanceConfig(**data['electrum']),
        kafka=KafkaConfig(
            host=data['kafka']['host'],
            port=data['kafka']['port'],
            bootstrap_servers=data['kafka']['bootstrap.servers'],
            security_protocol=data['kafka']['security.protocol'],
            acks=data['kafka']['acks'],
            topics=data['kafka']['topics']
        ),
        schema_registry=SchemaRegistryConfig(
            host=data['schema-registry']['host'],
            port=data['schema-registry']['port']
        ),
        hadoop=HadoopConfig(**data['hadoop']),
        mongo=MongoConfig(url=data['mongo']['url'], database=data['mongo']['database']),
        influx=InfluxConfig(token=data['influx']['token'])
    )


# Load and build the configuration
raw_config = load_config(CONFIG_PATH)
loaded_config = build_config(raw_config)