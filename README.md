# lyrical-server

Server code for lyrical-v0.

A live production build of this server is hosted at [https://apreza.pythonanywhere.com](https://apreza.pythonanywhere.com)

## Setup

Initial configuration -- get your Genius access token from the [Genius developer website](https://genius.com/api-clients).

```bash
echo "GENIUS_ACCESS_TOKEN=youraccesstoken" > .env.local
echo "FLASK_CONFIG=config.py" >> .env.local
```

Make sure you have python3.7 installed so that this next script will create the virtual environment with the correct interpreter.

[pyenv](https://github.com/pyenv/pyenv) makes this easy for you i.e. `pyenv install 3.7.4 && pyenv shell 3.7.4`

Execute the build script to create the virtual environment and install the application + dependencies.

```bash
chmod +x scripts/*
scripts/build
```

Now you can run the development server directly.

```bash
scripts/runserver
```

Or activate the virtual environment for development.

```bash
source .venv/bin/activate
```

Install development dependencies such as linters, formatters, and typechecking.

```bash
pip install -rrequirements-dev.txt
```

Run tests locally with tox.

```bash
scripts/test
```

Deactivate virtual environment.

```bash
deactivate
```

Reset project.

```bash
rm -rf .venv && clear
```

A web client that makes calls to this server is [lyrical-react](https://github.com/anthonypreza/lyrical-react).
