

def get_local_address():
    import socket
    return socket.gethostbyname(socket.gethostname())


def get_public_address():
    from urllib.request import urlopen
    return urlopen('http://ip.42.pl/raw').read()
