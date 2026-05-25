from pathlib import Path
from urllib.parse import urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))


def url_for(request: Request, name: str, **path_params):
    return request.url_for(name, **path_params)


def flash(request: Request, message: str, category: str = 'info'):
    messages = request.session.setdefault('_flashes', [])
    messages.append((category, message))


def get_flashed_messages(request: Request, with_categories: bool = False):
    messages = request.session.pop('_flashes', [])
    if with_categories:
        return messages
    return [message for _, message in messages]


def redirect_with_flash(request: Request, route_name: str, message: str | None = None, category: str = 'info'):
    if message:
        flash(request, message, category)
    return request.url_for(route_name)


def add_query_params(url: str, **params):
    return f'{url}?{urlencode(params)}'


templates.env.globals['get_flashed_messages'] = get_flashed_messages
templates.env.globals['url_for'] = url_for
