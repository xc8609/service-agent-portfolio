import argparse
import os

from .db import migrate, provision_runtime
from .fixtures import reset, seed


def main():
    parser = argparse.ArgumentParser(description="Explicit local disposable-demo management")
    parser.add_argument("command", choices=["migrate", "init-demo", "seed", "reset", "provision"])
    parser.add_argument("--target", default="")
    args = parser.parse_args()
    dsn = os.environ["BANK_ADMIN_DATABASE_URL"]
    if args.command == "migrate":
        migrate(dsn)
    elif args.command == "provision":
        provision_runtime(dsn, os.environ["BANK_APP_PASSWORD"])
    elif args.command == "reset":
        reset(dsn, args.target)
    else:
        seed(dsn, args.target, initialize=args.command == "init-demo")
    print(args.command + " completed; synthetic local environment only")


if __name__ == "__main__":
    main()
