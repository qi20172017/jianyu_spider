
from sonyflake import SonyFlake
from kafka import KafkaConsumer, KafkaProducer
import json

source_topic = 'user_subject_3357724503697408'

bootstrap_servers = ["xgsj-kafka.istarshine.com:9092", "xgsj-kafka.istarshine.com:9093",
                     "xgsj-kafka.istarshine.com:9094"]

security_protocol = 'SASL_PLAINTEXT'
sasl_mechanism = 'PLAIN'
sasl_plain_username = 'u782135'
sasl_plain_password = 'e250e863f6a511e8b4c79cb6d002907c'


class Translate:
    def __init__(self):
        self.consumer = KafkaConsumer(source_topic,
                                      group_id="group_ysf",
                                      # auto_offset_reset='smallest',
                                      auto_offset_reset='latest',
                                      # value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                      value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                      # consumer_timeout_ms=1000,
                                      bootstrap_servers=bootstrap_servers,

                                      security_protocol=security_protocol,
                                      sasl_mechanism=sasl_mechanism,
                                      sasl_plain_username=sasl_plain_username,
                                      sasl_plain_password=sasl_plain_password
                                      )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def on_send_success(self, record_metadata):
        print("发送到：topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                           record_metadata.offset))

    def on_send_error(self, excp):
        print(excp)

    def run(self):
        print(f'listing at: {source_topic}')
        for message in self.consumer:
            print("读取到：%s:%d:%d" % (message.topic, message.partition,
                                    message.offset
                                    ))
            print(message.value)


if __name__ == '__main__':
    tran = Translate()

    tran.run()

