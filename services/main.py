from dht22_get_json import *


def main():
    conn = database_connect()
    rabbitmq_connect(conn)
    

if __name__ == "__main__":
    main()


