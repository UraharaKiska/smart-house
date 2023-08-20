import pika
import asyncio
# import aioamqp
import time
from connect_database import database_connect
import json
from models import Dht22
from pydantic import ValidationError
from datetime import datetime

CONN = 0

def on_message_received(ch, method, properties, body):
    global CONN
    if (not CONN):
        CONN = database_connect()
    if (CONN):
        cursor = CONN.cursor()
        message = json.loads(body.decode())
        now = datetime.now()
        date = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            info = Dht22(**message)
            cursor.execute(f"""INSERT INTO dht22 (temperature, humidity, heatindex, date_create) values 
                    ({info.temperature}, {info.humidity}, {info.heatindex}, '{date}');""")
            CONN.commit()
        except ValidationError as e:
            print(e.errors)
        
        print(info.model_dump)

    


def rabbitmq_connect(conn):
    CONN = conn
    rmq_url_connection_str = "amqp://sergey:1234@localhost"
    rmq_parameters = pika.URLParameters(rmq_url_connection_str)
    rmq_connection = pika.BlockingConnection(rmq_parameters)
    rmq_channel = rmq_connection.channel()

    rmq_channel.queue_declare(queue="dht22", durable=True)
    rmq_channel.queue_bind(exchange="amq.topic", queue="dht22", routing_key='dht22')

    rmq_channel.basic_consume(on_message_callback=on_message_received, queue="dht22", auto_ack=True)

    try:
        rmq_channel.start_consuming()
    except KeyboardInterrupt:
        rmq_channel.stop_consuming()
    except Exception:
        rmq_channel.stop_consuming
        # traceback.print_exc(file=sys.stdout)
    # result = channel.queue_declare(exclusive=True)
    # print(result)

    rmq_channel.start_consuming()
    
    
