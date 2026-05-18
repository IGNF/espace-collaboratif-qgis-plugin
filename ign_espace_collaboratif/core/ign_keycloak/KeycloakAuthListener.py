import socket
from urllib.parse import urlparse, parse_qs


class KeycloakAuthListener:
    @staticmethod
    def listen(ip: str, port: int = 7070):
        # Page HTML de confirmation : <link rel="icon" href="data:,"> empêche le navigateur
        # de faire une requête supplémentaire pour /favicon.ico après le callback.
        body = (
            "<!DOCTYPE html><html><head>"
            '<meta charset="utf-8">'
            "<title>Connexion réussie</title>"
            '<link rel="icon" href="data:,">'
            "</head>"
            '<body style="font-family:sans-serif;max-width:600px;margin:50px auto;text-align:center">'
            "<h2>Connexion réussie !</h2>"
            "<p>Vous êtes connecté à l'Espace Collaboratif IGN.</p>"
            "<p>Vous pouvez fermer cet onglet et retourner dans QGIS.</p>"
            "</body></html>"
        ).encode("utf-8")

        # HTTP/1.1 avec Connection: close et Content-Length pour éviter que le navigateur
        # attende d'autres données ou tente de réutiliser la connexion.
        response_ok = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"Connection: close\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n"
            + body
        )
        response_err = (
            b"HTTP/1.1 400 Bad Request\r\n"
            b"Content-Type: text/plain\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 11\r\n"
            b"\r\n"
            b"Bad Request"
        )

        timeout = 120
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR évite "Address already in use" si le port est encore en TIME_WAIT
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen()
        server.settimeout(timeout)
        result = None
        try:
            while True:
                try:
                    conn, _ = server.accept()  # conn, addr
                except TimeoutError as e:
                    if result is not None:
                        return result
                    raise Exception(f"Authentication timeout, user credentials "
                                    f"must be entered within {timeout}s") from e

                try:
                    # Buffer agrandi à 4096 : les codes d'autorisation Keycloak peuvent
                    # générer des URLs dépassant 1024 octets.
                    data = conn.recv(4096).decode("utf-8", errors="replace")
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    if result is not None:
                        return result
                    continue

                lines = data.splitlines()
                parts = lines[0].split() if lines else []

                handled = False
                if len(parts) >= 2 and parts[0] == "GET":
                    u = urlparse(parts[1])
                    query_params = parse_qs(u.query)
                    if (u.path == "/authorization-code/callback"
                            and len(query_params) > 0
                            and "code" in query_params
                            and "state" in query_params):
                        conn.sendall(response_ok)
                        conn.close()
                        result = query_params
                        # Timeout court pour absorber les requêtes de suivi du navigateur
                        # (ex. favicon) sans bloquer indéfiniment.
                        server.settimeout(2)
                        handled = True

                if not handled:
                    try:
                        conn.sendall(response_err)
                    except Exception:
                        pass
                    try:
                        conn.close()
                    except Exception:
                        pass
                    if result is not None:
                        return result
        finally:
            server.close()  # Fermeture explicite du socket
