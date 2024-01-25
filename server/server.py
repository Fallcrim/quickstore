import socket
import logging
import threading
import sqlite3


class Server:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.info("Starting server")
        self._host = "localhost"
        self._port = 1776
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((self._host, self._port))
        self._sock.listen()
        self._logger.info("Server started")

        self._db_connection = sqlite3.connect("data.qsstore")

        self._data = {}
        self._stop = False

        self.run()

    def run(self):
        self._setup_database()
        self._restore_state()
        threading.Thread(target=self.shell).start()
        while not self._stop:
            conn, addr = self._sock.accept()
            self._logger.info(f"Connection from {addr}")
            threading.Thread(target=self._handle_connection, args=(conn,)).start()

    def _setup_database(self):
        cursor = self._db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS data (key TEXT, value TEXT)")
        self._db_connection.commit()
        cursor.close()

    def _restore_state(self):
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT * FROM data")
        old_data = cursor.fetchall()
        self._data = dict(old_data)

    def stop(self):
        self._sock.close()
        self._logger.info("Server stopped")

    def __del__(self):
        self._db_connection.close()
        self.stop()

    def _handle_connection(self, conn: socket.socket) -> None:
        """
        Handle a connection with a client
        :param conn: The socket connection of the client that connected
        :return:
        """
        data = conn.recv(2048).decode("utf-8")
        operation = data.split()[0]
        if operation == "GET":
            key = data.split()[1]
            if key in self._data:
                conn.sendall(self._data[key].encode("utf-8"))
            else:
                conn.sendall("\r\n-1".encode("utf-8"))
        elif operation == "SET":
            key = data.split()[1]
            value = data.split()[2:]
            self._data[key] = " ".join(value)
            conn.sendall("1\r\n".encode("utf-8"))
        else:
            self._logger.error(f"Invalid operation: {operation}")
            conn.sendall("-1\r\n".encode("utf-8"))
            return
        conn.close()
        self._store_locally()

    def __repr__(self):
        return f"Server(_host={self._host}, _port={self._port})"

    def __str__(self):
        return repr(self)

    def _store_locally(self):
        db_conn = sqlite3.connect("data.qsstore")
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM data")
        for key, value in self._data.items():
            cursor.execute("INSERT INTO data VALUES (?, ?)", (key, value))
        db_conn.commit()
        cursor.close()
        self._logger.info("Stored data locally")

    def shell(self):
        while not self._stop:
            cmd = input(":> ")
            if cmd == "quit":
                self._stop = True
                return
            if cmd == "save":
                self._store_locally()
            else:
                print("Command not found")


if __name__ == '__main__':
    server = Server()
