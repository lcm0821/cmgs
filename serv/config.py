from re import template
from aiohttp import web
import jinja2
from pathlib import Path


from .dbconn import register_db_block

home_path = Path(__file__).parent.parent


web_routes = web.RouteTableDef()
db_block = register_db_block(
    dsn="host=localhost dbname=examdb user=examdbo password=pass"
)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(home_path / "templates"))
)


def render_html(request, template, **kwargs):
    location = {"pathname": request.path}
    return web.Response(text=jinja_env.get_template(template).render(
        location=location, **kwargs#使用两个星号可以将参数收集到一个字典中kwargs是一个字典
    ), content_type="text/html")
