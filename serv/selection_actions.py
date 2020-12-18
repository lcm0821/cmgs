from aiohttp import web
import psycopg2.errors
from urllib.parse import urlencode

from .config import db_block, web_routes

@web_routes.post('/action/selection/add')
async def action_selection_add(request):
    params = await request.post()
    stu_sn = params.get("stu_sn")
    cou_sn = params.get("cou_sn")
    term = params.get("term")
    place = params.get("place")

    if stu_sn is None or cou_sn is None or term is None or place is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, term, place must be required")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        term =  TEXT(term)
        place = TEXT(place)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO course_selection (stu_sn, cou_sn, term, place) 
            VALUES ( %(stu_sn)s, %(cou_sn)s, %(term)s,%(place)s)
            """, dict(stu_sn=stu_sn, cou_sn=cou_sn, term=term,place=place))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生的选课",
            "return": "/selection"
        })
        return web.HTTPFound(location=f"/error?{query}")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

    return web.HTTPFound(location="/selection")


@web_routes.post('/action/selection/edit/{stu_sn}/{cou_sn}')
async def edit_selection_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    params = await request.post()
    grade = params.get("grade")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        term = text(term)
        place = text(place)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    with db_block() as db:
        db.execute("""
        UPDATE course_selection SET term=%(term)s
        WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn, term=term))

    return web.HTTPFound(location="/term")


@web_routes.post('/action/selection/delete/{stu_sn}/{cou_sn}')
def delete_selection_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        DELETE FROM course_selection
            WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

    return web.HTTPFound(location="/selection")
