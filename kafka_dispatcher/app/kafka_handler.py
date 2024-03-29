import json
import os
import threading
from time import sleep

from confluent_kafka import Consumer, KafkaError, KafkaException

"""
This module provides the KafkaService class, which is used to consume data from Kafka.
It also provides the KafkaStreamHandler class, which is used to handle the latest kafka data with http.
It also provides the KafkaSocketIO class, which is used to handle the Kafka data to socketio.

Todo:
    * Add more features

"""


class KafkaService:
    """
    KafkaService is a class to consume data from Kafka.
    It can be used to consume data from a single topic or multiple topics.
    """

    def __init__(self, config=None):
        """
        Instantiated the class.
        It sets up the Kafka consumer configs and assigns it to self.consumer.

        :param self: Represent the instance of the class
        :param config: Pass in a dictionary of configuration options
        :return: A consumer object
        :doc-author: Yukkei
        """
        if config is None:
            self.config = {
                'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
                'group.id': os.environ.get('KAFKA_GROUP_ID'),
                'auto.offset.reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET'),
                'enable.auto.commit': True,
                # 'fetch.max.bytes': 52428800,
                # 'max.partition.fetch.bytes': 1048576
            }

        else:
            self.config = config

        self.consumer = Consumer(self.config)

    def subscribe(self, topics):
        """
        The subscribe function subscribes to a list of topics.
            The function takes in a list of topics and assigns the consumer to those topics.

        :param topics: Specify the topics to subscribe to
        :doc-author: Yukkei
        """
        consumer = self.consumer
        consumer.subscribe(topics, on_assign=on_assign)
        # consumer.subscribe(topics)

    def consume(self):
        """
        This consumes a single message from the Kafka queue.

        :return: A list of messages that have been consumed
        :doc-author: Yukkei
        """

        return self.consumer.poll(timeout=10)

    def batch_consume(self, batch_size=50):
        """
        This consumes a batch of messages from the Kafka queue.

        :return: A list of messages that have been consumed
        :doc-author: Yukkei
        """
        return self.consumer.consume(num_messages=batch_size, timeout=1)

    def commit(self):
        """
        This commits the current offset for the consumer.

        :doc-author: Yukkei
        """
        self.consumer.commit()

    def receive(self):
        """
        This is used to receive a single message.
        If there are no messages in the queue, it will return None.
        If there is an error, it will raise an exception.
        If there is a message, it will return the decoded message value.

        :return: The decoded message value
        :doc-author: Trelent
        """
        msg = self.consume()
        if msg is None:
            # print("No message received")
            return None
        if msg.error():
            if msg.error().code() == KafkaError.PARTITION_EOF:
                print('End of partition reached {0}/{1}')
                return None
            else:
                raise KafkaException(msg.error())
        else:
            return msg.value().decode('utf-8')

    def gen_messages(self, rate=1):
        """
        The gen_messages function is a generator that yields messages from the Kafka topic.
        It takes an optional rate argument, which defaults to 0.
        The rate argument specifies how long to wait between yielding each message.

        :param self: Represent the instance of the class
        :param rate: Control the speed of the message consumption
        :return: A generator object that contains the messages from the topic
        :doc-author: Yukkei
        """
        while True:

            msg = self.consume()
            sleep(rate)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                yield msg

    def close(self):
        """
        The close function closes the Kafka consumer.

        :doc-author: Yukkei
        """
        try:
            self.consumer.close()
        except Exception as e:
            print(f"Error closing Kafka consumer: {e}")

    def reset_consumer(self):
        """Method to reset the Kafka consumer."""
        self.close()  # Close the current consumer
        self.consumer = Consumer(self.config)  # Reinitialize the consumer


class KafkaStreamHandler:
    """
    KafkaStreamHandler is a class to handle the Kafka stream.
    It can be used to get the latest data from a single device or all the devices.
    It can also be used to get the latest data stream from a single device.
    """

    def __init__(self, scale=1):
        self.scale = scale
        self.consumer_thread_pool = {}
        self.data = {}  # {device_name: measurement} use to store the last measurement
        self.flag = {}  # {device_name: write_flag} use to indicate if the measurement is new
        self.running = False  # flag to stop the thread
        # self.thread = None  # thread to run the kafka consumer

    def storing_latest(self):
        """
        The storing_latest function is a thread that runs in the background.
        It consumes messages from Kafka and stores them in a dictionary called `self.data`,
        which is keyed by device_name (the name of the device that sent the message).
        The `self.flag` dictionary keeps track of whether the message is new or not.

        :doc-author: Yukkei
        """
        print("begin storing latest data")
        kafka_service = KafkaService()
        kafka_service.subscribe(['sensor_data', 'ml_result', 'slb_out'])
        sleep(1)
        while self.running:

            msg = kafka_service.consume()
            no_message_counter = 0
            # print("message received")
            if msg:
                try:
                    msg_json = json.loads(msg.value().decode('utf-8'))
                    msg_json['values'] = flatten_json(msg_json['values'])
                    device_name = msg_json.get("device_name", "")
                    identifier = msg_json.get("identifier", "")
                    if device_name:
                        if identifier:
                            device_name = f"{device_name}_{identifier}"
                        if device_name in self.data and str(msg_json.get('time')) > str(
                                self.data[device_name].get('time')):
                            # flatten the json
                            self.data[device_name] = msg_json
                            self.flag[device_name] += 1
                            if self.flag[device_name] > 100:
                                self.flag[device_name] = 0
                        elif device_name not in self.data:
                            self.data[device_name] = msg_json
                            self.flag[device_name] = 0
                except Exception as e:
                    kafka_service.reset_consumer()
                    kafka_service.subscribe(['sensor_data', 'ml_result', 'slb_out'])
                    print(f"Error: {e}")
            else:
                no_message_counter += 1
                print("No message received: ", no_message_counter)
                if no_message_counter > 60:
                    kafka_service.reset_consumer()
                    kafka_service.subscribe(['sensor_data', 'ml_result', 'slb_out'])
            sleep(0)

        kafka_service.close()

    def get_latest_data_for_single(self, device_name):
        """
        The get_latest_data_for_single function returns the latest data for a single device.

        :param self: Represent the instance of the class
        :param device_name: Specify which device's data is being requested
        :return: The latest data for a single device
        :doc-author: Yukkei
        """
        if device_name in self.data:
            return self.data[device_name]
        else:
            return None

    def get_latest_data_for_all(self):
        """
        The get_latest_data_for_all function returns the latest data for all the sensors in a dictionary.
        The keys are sensor names and values are tuples containing (timestamp, value) pairs.

        :return: A dictionary of the latest data for all sensors
        :doc-author: Yukkei
        """
        return self.data

    def get_latest_data_stream(self, device_name, frequency=0):
        """
        The get_latest_data_stream function is a generator that yields the latest data from a device.
            It takes in two arguments:
                1) device_name - The name of the device to get data from.
                This must be one of the devices listed in `self.data`, or else an error will be thrown.
                2) frequency - How often (in seconds) to check for new data on this stream.

        :param self: Represent the instance of the class
        :param device_name: Specify which device's data stream you want to get
        :param frequency: The sampling frequency of the data stream
        :return: generator of the latest data from a device
        :doc-author: Yukkei
        """
        if device_name not in self.data:
            print("Error: device name not found")
            return

        last_seen_flag = -1
        while self.running:
            sleep(frequency)
            current_flag = self.flag.get(device_name, 0)
            if current_flag != last_seen_flag:
                last_seen_flag = current_flag

                yield f"data: {self.data[device_name]}\n\n"

    def start(self):
        """
        The start function starts the Kafka stream.
        It sets the running variable to True, which is used in storing_latest()
            to determine whether it should continue running.
        It also creates a thread that runs storing_latest(), and then starts that thread.

        :doc-author: Yukkei
        """
        print("Kafka stream starting")
        self.running = True
        for i in range(self.scale):
            self.consumer_thread_pool[i] = threading.Thread(target=self.storing_latest)
            self.consumer_thread_pool[i].start()

        print("Kafka stream started")

    def stop(self):
        """
        The stop function is used to stop the service.
        It sets the running variable to False, which will cause the run function to exit.
        The thread is then joined and closed.

        :doc-author: Yukkei
        """
        self.running = False
        sleep(2)
        for i in range(self.scale):
            self.consumer_thread_pool[i].join()
        # self.kafka_service.close()
        # self.thread.join()


def on_assign(consumer, partitions):
    """
    The on_assign function is called when the consumer has been assigned partitions.
    The callback can be used to seek to particular offsets, or reset state associated with the assignment.
    This function should not raise models.

    :param consumer: Assign the partitions to the consumer
    :param partitions: Assign the partitions to the consumer
    :return: The partitions to be consumed
    :doc-author: Yukkei
    """
    for p in partitions:
        p.offset = -1
    consumer.assign(partitions)


def flatten_json(input_json):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        else:
            out[name[:-1]] = x

    flatten(input_json)
    return out
