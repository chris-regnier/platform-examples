def main(debug: bool = False):
    """
    Runs the various apps, i.e. message board.
    """

    from .adapters.incoming.api import app

    app.debug = debug
    return app
