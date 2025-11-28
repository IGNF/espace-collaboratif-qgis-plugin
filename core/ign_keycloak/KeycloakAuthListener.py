import socket
from urllib.parse import urlparse, parse_qs


class KeycloakAuthListener:
    @staticmethod
    def listen(ip: str, port: int = 7070):
        response_ok = b"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nOk. After closing this tab, you need " \
                      b"to return to the QGIS application and wait the dialog [Parametres de travail].\r\n"
        response_err = b"HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request\r\n"

        timeout = 120
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen()
        server.settimeout(timeout)
        try:
            while True:
                try:
                    conn, _ = server.accept()  # conn, addr
                except TimeoutError as e:
                    raise Exception(f"Authentication timeout, user credentials "
                                    f"must be entered within {timeout}s") from e

                data = conn.recv(1024).decode()
                headers = data.splitlines()

                method, url, _ = headers[0].split()  # method, url, httpver
                if method == "GET":
                    u = urlparse(url)
                    query_params = parse_qs(u.query)
                    if u.path == "/authorization-code/callback" and query_params.__len__() > 0:
                        if "code" in query_params and "state" in query_params:
                            conn.sendall(response_ok)
                            conn.close()
                            return query_params

                conn.sendall(response_err)
                conn.close()
        finally:
            server.close()  # Fermeture explicite du socket
