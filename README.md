# EDAT - Exploratory data analysis tool

This is a tool for dataset visualization using Seabourne running on FastAPI with Django and VueJs for front-end part. 

## Setup

```
git clone https://github.com/igorvoltaic/edat
pip install -r requirements.txt
cd edat/
./manage.py migrate
./manage.py createsuperuser 
```

## Running

```
uvicorn project.asgi:app --debug
```
An OS tool should be set to crean `tmpdir/` once a day/hour in case there were interrupted used sessions

## Routes

The Django app is available at `/` (e.g. `http://localhost:8000/django/admin/`)

The FastAPI app is is available at `/api` (e.g. `http://localhost:8000/api/datasets/`)


### Code correctness

Linters: `Pyright`, `Pylint`, `Flake8`
Static Type-checking: `Pyright`, `mypy`
Formatters: `autopep8`, `yapf`
