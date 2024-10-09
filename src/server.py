from typing import Mapping, Dict

import socket, threading
import json
from colorama import Fore
from database.queries.users import get_user

# Global variable that mantain client's connections
connections = []
room_connections = {}

rooms = ["123", "456", "789"]


def send_msg_as_system(msg: str, connection: socket.socket):
    connection.send(f"[{Fore.RED}system{Fore.RESET}]: {msg}\n".encode())

def send_data(msg: str, connection: socket.socket):
    connection.send(msg.encode())


def command(data: Dict, connection: socket.socket, address: str) -> None:
    command = data['msg'].replace("/", "").split()[0]
    data["code"] = command

    print(f'{address[0]}:{address[1]} - {Fore.RED}System code{Fore.RESET} {json.dumps(data)}')

    if command == "join_room":
        room = data['msg'].replace("/", "").split()[1]
        if room not in room_connections.keys():
            room_connections[room] = []
        room_connections[room].append(connection)

    if command == "show_rooms":
        send_data(json.dumps({"rooms": rooms}), connection)
        # send_msg_as_system("Rooms: [" +", ".join(room_connections.keys()) + "]", connection)


def handle_user_connection(connection: socket.socket, address: str) -> None:
    """
        Get user connection in order to keep receiving their messages and
        sent to others users/connections.
    """
    while True:
        try:
            msg = connection.recv(1024)

            if msg:

                data = json.loads(msg.decode())

                if "user" not in data.keys() and "msg" not in data.keys():
                    # Sending message to client connection
                    print(f'{address[0]}:{address[1]} - {Fore.RED}Corruption{Fore.RESET} {json.dumps(data)}')
                    send_msg_as_system(f"Data is corrupted", connection)
                    continue

                if data['msg'].startswith("/"):
                    command(data, connection, address)
                    continue


                # TODO add logger
                print(f'{address[0]}:{address[1]} - {msg.decode()}')

                broadcast(msg.decode(), connection)

            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(connection)
            break


def broadcast(message: str, connection: socket.socket) -> None:
    """
        Broadcast message to all users connected to the server
    """

    data = json.loads(message.encode())

    for client_conn in connections:
        if client_conn != connection:
            try:

                client_conn.send(
                    "[{user}]: {msg}".format(
                        user=data['user'],
                        msg=data['msg']
                    ).encode()
                )

            except Exception as e:
                print('Error broadcasting message: {e}')
                remove_connection(client_conn)


def remove_connection(conn: socket.socket) -> None:
    """
        Remove specified connection from connections list
    """

    if conn in connections:
        conn.close()
        connections.remove(conn)


def server() -> None:
    """
        Main process that receive client's connections and start a new thread
        to handle their messages
    """

    LISTENING_PORT = 12000

    try:
        # Create server and specifying that it can only handle 4 connections by time!
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', LISTENING_PORT))
        socket_instance.listen(4)

        print('Server running!')

        while True:
            # Accept client connection
            socket_connection, address = socket_instance.accept()
            connections.append(socket_connection)
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()