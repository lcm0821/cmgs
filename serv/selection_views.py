from aiohttp import web
from .config import db_block, web_routes, render_html


@web_routes.get("/selection")
async def view_list_selection(request):
    with db_block() as db:
        db.execute("""
        SELECT sn AS stu_sn, name as stu_name FROM student ORDER BY name
        """)
        students = list(db)

        db.execute("""
        SELECT sn AS cou_sn, name as cou_name,term,place FROM course ORDER BY course
        """)
        courses = list(db)
        terms = list(db)
        places = list(db)


    return render_html(request, 'selection_list.html',
                       students=students,
                       courses=courses,
                       terms=terms,
                       places=places,)


@web_routes.get('/selection/edit/{stu_sn}/{term}')
def view_selection_editor(request):
    stu_sn = request.match_info.get("stu_sn")
    term = request.match_info.get("term")
    if stu_sn is None or term is None:
        return web.HTTPBadRequest(text="stu_sn, term, must be required")

    with db_block() as db:
        db.execute("""
        SELECT course FROM course_selection
            WHERE stu_sn = %(stu_sn)s AND term = %(term)s;
        """, dict(stu_sn=stu_sn, term=term))

        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such selection: stu_sn={stu_sn}, term={term}")

    return render_html(request, "selection_edit.html",
                       stu_sn=stu_sn,
                       course=course,
                       term=term,
                       place=place,
                       )


@web_routes.get("/selection/delete/{stu_sn}/{term}")
def selection_deletion_dialog(request):
    stu_sn = request.match_info.get("stu_sn")
    term = request.match_info.get("term")
    if stu_sn is None or term is None:
        return web.HTTPBadRequest(text="stu_sn, term, must be required")

    with db_block() as db:
        db.execute("""
        SELECT se.stu_sn, se.term,
            s.name as stu_name, 
            c.term as term
            se.course
            se.place
        FROM course_selection as se
            INNER JOIN student as s ON se.stu_sn = s.sn
        WHERE stu_sn = %(stu_sn)s AND term = %(term)s;
        """, dict(stu_sn=stu_sn, term=term))

        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such course: stu_sn={stu_sn}, term={term}")

    return render_html(request, 'selection_dialog_deletion.html', record=record)
