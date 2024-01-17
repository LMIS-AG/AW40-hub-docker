from time import time

import httpx
from example_2 import example

# API key defined in dev.env is required while polling the hub api for the
# finished diagnosis
api_key_diagnostics = "diagnostics-key-dev"


def test_example():
    # Execute the example
    case_url = example.main(interactive=False)
    diag_url = f"{case_url}/diag"

    # After waiting for a short duration, we should be able to confirm that
    # the diagnosis is in state "failed", as the example provokes a crash of
    # the state  machine
    status = None
    timeout = 10
    start = time()
    while time() - start <= timeout and status != "failed":
        diag = httpx.get(diag_url, headers={"x-api-key": api_key_diagnostics})
        status = diag.json()["status"]

    assert status == "failed"
