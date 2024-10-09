import socket, threading
import os
from database.queries.users import get_user
import json
from colorama import Fore

def handle_messages(connection: socket.socket):
    """
        Receive messages sent by the server and display them to user
    """

    while True:
        try:
            msg = connection.recv(1024)

            # If there is no message, there is a chance that connection has closed
            # so the connection will be closed and an error will be displayed.
            # If not, it will try to decode message in order to show to user.
            if msg:
                print(
                    f"\n{msg.decode()}\n"
                )

            else:
                connection.close()
                break

        except Exception as e:
            print(f'Error handling message from server: {e}')
            connection.close()
            break

def client() -> None:
    '''
        Main process that start client connection to the server
        and handle it's input messages
    '''

    SERVER_ADDRESS = '127.0.0.1'
    SERVER_PORT = 12000

    try:
        # Instantiate socket and start connection with server
        socket_instance = socket.socket()
        socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))
        # Create a thread in order to handle messages sent by server
        threading.Thread(target=handle_messages, args=[socket_instance]).start()

        print('Connected to chat!')

        # Read user's input until it quit from chat and close connection
        while True:
            user = get_user(nick_name=os.getenv('USER'))["user"]
            msg = input(f"[{Fore.YELLOW}{user.nick_name}{Fore.RESET}]: ")

            if not msg:
                continue

            data = {
                "type": "message",
                "user": user.nick_name,
                "msg": msg,
            }

            if data["msg"] == "/quit":
                socket_instance.send(json.dumps(data).encode())
                break

            # Parse message to utf-8
            socket_instance.send(json.dumps(data).encode())

        # Close connection with the server
        socket_instance.close()

    except Exception as e:
        print(f'Error connecting to server socket {e}')
        socket_instance.close()


if __name__ == "__main__":
    client()
