import json


class QueuePublisher:
    def __init__(self, conn):
        self.conn = conn

    def publish(self, destination: str, payload: dict):
        self.conn.send(
            destination=destination,
            body=json.dumps(payload),
            headers={
                "persistent": "true",
                "content-type": "application/json",
            },
        )
