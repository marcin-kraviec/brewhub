from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    app.debug = True

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('500.html'), 500

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
