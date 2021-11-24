import os 
from flask import Flask

# from werkzeug.contrib.fixers import ProxyFix
from werkzeug.debug import DebuggedApplication
from werkzeug.routing import BaseConverter


# from flask_cors import CORS


class DateConverter(BaseConverter):
    """Extracts a ISO8601 date from the path and validates it."""

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.strftime("%Y-%m-%d")



# from routes import *

def create_app(config_obj: str = ""):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """

    # if not config_obj:
    #     import settings 
    #     config_obj = settings.py 
    app = Flask(__name__.split(".")[0])
    # app = Flask(__name__)
    app.url_map.converters["date"] = DateConverter
    # app.config.from_object(config_object)
    # register_extensions(app)
    register_blueprints(app)
    # register_errorhandlers(app)
    # register_shellcontext(app)
    # register_commands(app)
    # configure_logger(app)
    return app


def register_blueprints(app):
    # import all of our routes
    from routes import app as routes_app
    app.register_blueprint(routes_app)

# enable CORS - need to install flask_cors first
# CORS(app)

# app.wsgi_app = ProxyFix(app.wsgi_app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
# wsgi_app = app.wsgi_app



# Launching server
if __name__ == "__main__":
    PORT = 8090
    print(f"running on localhost port {PORT} huh")
    # import os
    HOST = os.environ.get("SERVER_HOST", "localhost")
    print(HOST)
    # try:
    #    PORT = int(os.environ.get('SERVER_PORT', '8000'))
    # except ValueError:
    app.debug = True
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
    # print PORT
    app.run(HOST, PORT, threaded=True)
    # app.run(port = 8081, threaded = True, debug = True)
    # app.run(host='127.0.0.1',port=8000)


app = create_app()



