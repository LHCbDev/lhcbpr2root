# =============================================================================
# STD:
# =============================================================================
import os
import sys

from service import app, utils
from dotenv import load_dotenv



# =============================================================================
os.environ.setdefault('ENV', 'default')
env_file = os.path.abspath(os.path.join('envs', "%s.env" % utils.env_var('ENV')))
print('*' * 80)
print("Read environment from '{}'".format(env_file))
load_dotenv(env_file)


# =============================================================================
# Constants:
# =============================================================================
ROOT_DATA = os.path.abspath(utils.env_var(
    'ROOT_DATA',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
))
print("Path to ROOT directory '{}'".format(ROOT_DATA))

FLASK_PORT = int(utils.env_var('FLASK_PORT', 5000))
FLASK_HOST = utils.env_var('FLASK_HOST', None)
DEBUG = utils.env_var('DEBUG', False)


def run_gunicorn_server(app):
    """run application use gunicorn http server
    """

    from gunicorn.app.base import Application

    class FlaskApplication(Application):

        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(FLASK_HOST, FLASK_PORT),
                'workers': 4
            }

        def load(self):
            return app

    FlaskApplication().run()


def run_devel_server(app):
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)


if __name__ == '__main__':
    if "--gunicorn" in sys.argv:
        sys.argv.pop(sys.argv.index("--gunicorn"))
        run_gunicorn_server(app)
    else:
        run_devel_server(app)
