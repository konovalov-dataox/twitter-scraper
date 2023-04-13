import pika


class RMQ:
    def __init__(self, connection_string: str):
        self.parameters = pika.URLParameters(connection_string)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def _queue_declare(self, qnames):
        for name in qnames:
            self.channel.queue_declare(queue=name)

    def publish(self, **kwargs):
        self.channel.basic_publish(**kwargs)

    @staticmethod
    def properties(args):
        return pika.BasicProperties(**args)

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()
