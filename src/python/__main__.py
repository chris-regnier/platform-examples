import argparse
from . import main


parser = argparse.ArgumentParser(description="Run the message board.")
parser.add_argument(
    "--debug", action="store_true", help="Run the server in debug mode."
)
parser.add_argument(
    "--host", default="127.0.0.1", help="The host to run the server on."
)
parser.add_argument(
    "--port", default=8000, type=int, help="The port to run the server on."
)
parser.add_argument(
    "--reload", action="store_true", help="Reload the server on changes."
)


def cli():
    import uvicorn

    args = parser.parse_args()
    if args.reload:
        uvicorn.run(
            "src.python:main",
            factory=True,
            reload=args.reload,
            host=args.host,
            port=args.port,
        )
    else:
        app = main(debug=args.debug)
        uvicorn.run(app, reload=args.reload, host=args.host, port=args.port)


if __name__ == "__main__":
    cli()
