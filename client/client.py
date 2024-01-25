import socket

return_codes = {
    "1": "OK.",
    "-1": "KEY NOT FOUND IN DATABASE."
}


def main():
    addr = input("Enter address to connect to >> ")
    port = int(input("Enter port to connect >> "))
    _exit = False
    while not _exit:
        cmd = input(f"{addr}:{port} -> ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        if cmd.lower() == "exit":
            _exit = True
            sock.close()
            continue
        sock.sendall(cmd.encode("utf-8"))
        response = sock.recv(1024).decode().strip("\r\n")
        if response.isdigit():
            print(return_codes[response])
        else:
            print(response)
        sock.close()


if __name__ == '__main__':
    main()
