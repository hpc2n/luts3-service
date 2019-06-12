
from twisted.python.log import FileLogObserver

def logger():
        return FileLogObserver(open("/var/log/sgas.log", "a")).emit
