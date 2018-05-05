from app import app as application

if __name__ == '__main__':
    application.run(debug=False,port=8082, host='0.0.0.0')
