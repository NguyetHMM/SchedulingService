import os
# from flask_script import Manager
from src.manage import app

# manager = Manager(app)

# @manager.command
# def runserver():
#     app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5000)))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5000)))
