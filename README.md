# EDAT - Exploratory data analysis tool

A dataset visualization tool implemented using Seaborn python library, running on [Django](https://www.djangoproject.com) + [FastAPI](https://fastapi.tiangolo.com) for backend and [Vue.js](https://vuejs.org) for the frontend.

## Setup

```
git clone https://github.com/igorvoltaic/edat
cd edat/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "SECRET_KEY=$(python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())')" > .env
source venv/bin/activate
./manage.py migrate
./manage.py createsuperuser 
```

## Running

```
uvicorn base.asgi:app --debug
```
An OS tool should be set to crean `tmpdir/` once a day/hour in case there were interrupted used sessions

## Routes

The Django app is available at `/` (e.g. `http://localhost:8000/django/admin/`)

The FastAPI app is is available at `/api` (e.g. `http://localhost:8000/api/dataset/`)


## Code correctness

Linters: `Pyright`, `Pylint`, `Flake8`

Static Type-checking: `Pyright`, `mypy`

Formatters: `autopep8`, `yapf`


## Testing

To do the testing you need to `cd` into `testing` directory and run `pytest`
