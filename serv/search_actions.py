from aiohttp import web
import psycopg2.errors
from urllib.parse import urlencode

from .config import db_block, web_routes

@web_routes.get('/action/search')
async def action_search(request):
    params = await request.get()
    stu_sn = params.get("stu_sn")
    term = params.get("term")
    cou_sn = params.get("cou_sn")
    db.execute("""
    SELECT grade FROM course_grade