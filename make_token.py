from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import re
import sys

USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an X-App-Token for one user.")
    parser.add_argument("user_id", help="User ID used in API paths")
    args = parser.parse_args()

    if USER_ID_PATTERN.fullmatch(args.user_id) is None:
        parser.error("user_id must start with a letter or digit and use only letters, digits, _ or -")

    secret = os.getenv("APP_TOKEN_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        print("APP_TOKEN_SECRET must be set and contain at least 32 UTF-8 bytes.", file=sys.stderr)
        return 1

    digest = hmac.new(secret.encode("utf-8"), args.user_id.encode("utf-8"), hashlib.sha256).hexdigest()
    print(f"v1.{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
