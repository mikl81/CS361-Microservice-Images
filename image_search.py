"""
ZMQ Image Search Microservice - Server
---------------------------------------
Listens for search query strings over ZMQ and replies with
the raw bytes of the top Google Image Search result.

Setup:
    pip install pyzmq requests

Usage:
    export GOOGLE_API_KEY="your_api_key"
    export GOOGLE_CX="your_custom_search_engine_id"
    python zmq_image_server.py
"""

import os
import zmq
import requests

#Globals
ZMQ_ADDRESS   = "tcp://*:5555"
GOOGLE_API_KEY = os.environ.get("GCS_DEVELOPER_KEY")
GOOGLE_CX      = os.environ.get("GCS_CX")
SEARCH_URL     = "https://cse.google.com/cse?cx=d7d12af2cc4af4107"
REQUEST_TIMEOUT = 10  # seconds



def search_google_images(query: str) -> str | None:
    """Return the URL of the top Google image result, or None on failure."""
    params = {
        "key": GOOGLE_API_KEY,
        "cx":  GOOGLE_CX,
        "q":   query,
        "searchType": "image",
        "num": 1,
    }
    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            print("No image results for query: %s", query)
            return None
        return items[0]["link"]
    except requests.RequestException as exc:
        print("Google Search API error: %s", exc)
        return None


def fetch_image_bytes(url: str) -> bytes | None:
    """Download an image URL and return its raw bytes, or None on failure."""
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, stream=True)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as exc:
        print("Failed to fetch image from %s: %s", url, exc)
        return None


def run_server():
    context = zmq.Context()
    socket  = context.socket(zmq.REP)
    socket.bind(ZMQ_ADDRESS)
    print("Server listening on %s", ZMQ_ADDRESS)

    while True:
        #Receive query
        raw = socket.recv()
        query = raw.decode("utf-8").strip()
        print("Received query: %r", query)

        if not query:
            socket.send(b"ERROR:empty_query")
            continue

        #Search
        image_url = search_google_images(query)
        if image_url is None:
            socket.send(b"ERROR:no_results")
            continue

        print("Top result URL: %s", image_url)

        # Fetch image
        image_bytes = fetch_image_bytes(image_url)
        if image_bytes is None:
            socket.send(b"ERROR:fetch_failed")
            continue

        #Reply with raw image bytes
        print("Sending image (%d bytes)", len(image_bytes))
        socket.send(image_bytes)


if __name__ == "__main__":
    run_server()