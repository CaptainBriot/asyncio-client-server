# Install
```bash
cd asyncio-client-server
virtualenv -p python3.6 venv
venv/bin/pip install -r requirements.txt
```

# Test
```bash
venv/bin/nosetests -v tests
venv/bin/pylint --rcfile .pylintrc client.py server.py common.py
```

# Run the server
```bash
venv/bin/python server.py
```

# Run the client
```bash
venv/bin/python client.py frequency
```

To send 10 requests per second:
```bash
venv/bin/python client.py 10
```
