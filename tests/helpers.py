# Copyright 2024 Ableton
# All rights reserved


import re


def extract_token(message) -> str:
    pattern = r'token=([a-f0-9\-]+)'
    match = re.search(pattern, message)

    return match.group(1) if match else None
