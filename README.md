Requests are made via passing a JSON payload
```python
payload = {
        "query": "mountains",
        "limit": "10",
        "dest_dir": "test_download"
    }
 
    print(f"Sending: {payload}")
    socket.send_json(payload)
```

While results are received as a json payload like so
```python
payload = {
        "results": [list_of_relative_file_paths]
    }
 ```