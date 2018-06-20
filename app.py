from app import app as application
from app import socketio

if __name__ == '__main__':
    socketio.run(application, debug=False,port=8082, host='0.0.0.0')
