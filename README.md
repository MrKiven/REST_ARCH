# :punch: Easier To Build Your RESTful App
A Restful Frame Based On Gunicorn

## Develop With Me
1. Fork repo
2. Clone to your local
3. Add Remote as upstream
4. Do some change
5. Push to your origin
6. Pull request

## Develop
> after you add some future or fix something, you should add unittest for your change

> `make unittest -sx` to make sure test is pass

> `make pylint` can check your code with flake8

> `make bump ver=x.x.x.x` to bump a new version

## Installation
> `pip install rest_arch`

## App struct

        ├── app.yaml
        ├── foo
        │   ├── __init__.py
        │   ├── app.py
        │   ├── models.py
        │   ├── settings.py
        ├── requirements.txt

## Usage
1. `skt bootstrap` to build a app.
2. `cd your_app_path` run `skt serve` to start app.
3. `skt shell` to run a client as `c`.
4. `c.get('/ping')` to get a response.

## APP&LOG

    import logging
    from rest_arch.app import make_app

    app = make_app(__name__)

    logger = logging.getLogger(__name__)

    logger.info('A Test Log Info')

## Contact
1. kiven.mr@gmail.com
2. create issue or pull request
