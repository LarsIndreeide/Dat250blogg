import os
from flask import Flask, request
from flask.cli import with_appcontext
import click


app = Flask(__name__, instance_relative_config=True)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY']= os.getenv('SECRET_KEY')

    app.config['DATABASE'] =  os.getenv('DATABASE_URL') #
    print(os.getenv('DATABASE_URL'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    from . import db
    db.init_app(app)

    @app.route('/slycooper')
    def tierlist():
        return ('static/images/SlyCooperTierlist.png')

    #return app

    from . import auth
    app.register_blueprint(auth.bp)

    from . import db
    db.init_app(app)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().execute(f.read())


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')