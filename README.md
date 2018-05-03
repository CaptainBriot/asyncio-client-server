# Install
```bash
cd asyncio-client-server
virtualenv -p python3.6 venv
venv/bin/pip install -r requirements.txt
```

# Test
```bash
nosetests -v tests
venv/bin/pylint --rcfile .pylintrc client.py server.py common.py
```
