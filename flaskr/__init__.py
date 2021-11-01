import os
from flask import Flask, request, send_file
from flask_recaptcha import ReCaptcha
from flask_paranoid import Paranoid


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY']= os.getenv('SECUREKEY_JADE_KEY')

    app.config['DATABASE'] =  os.getenv('DATABASE_URL') #

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['RECAPTCHA_SITE_KEY'] = '6LceNwQdAAAAAAWqsl1cehaMvCQ8mNsE5h7xj5Cj'
    app.config['RECAPTCHA_SECRET_KEY'] = '6LceNwQdAAAAAPpCrlpf8ZwKbWILexik4Y-A7QOR'
    recaptcha = ReCaptcha(app)
    paranoid = Paranoid(app)
    paranoid.redirect_view = '/'


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
