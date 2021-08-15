import os
import subprocess
import uuid

import requests
from requests.packages.urllib3.util.retry import Retry


def test_args():
    name = str(uuid.uuid4())
    port = os.getenv('PORT', 8080)  # Each functions framework instance needs a unique port

    process = subprocess.Popen(
      [
        'functions-framework',
        '--source', '../main.py',
        '--target', 'symone_bot',
        '--port', str(port)
      ],
      cwd=os.path.dirname(__file__),
      stdout=subprocess.PIPE
    )

    # Send HTTP request simulating Pub/Sub message
    # (GCF translates Pub/Sub messages to HTTP requests internally)
    BASE_URL = f'http://localhost:{port}'

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
      max_retries=retry_policy)

    session = requests.Session()
    session.mount(BASE_URL, retry_adapter)

    name = str(uuid.uuid4())
    res = requests.post(
      BASE_URL,
      json={'name': name}
    )
    assert res.text == "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do."

    # Stop the functions framework process
    process.kill()
    process.wait()
