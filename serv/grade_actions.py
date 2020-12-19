from aiohttp import web
import psycopg2.errors
from urllib.parse import urlencode
from .config import db_block, web_routes, render_html

from .config import db_block, web_routes

@web_routes.post('/action/grade/add')
async def action_grade_add(request):
    print("add_action")
    params = await request.post()
    stu_sn = params.get("stu_sn")
    cou_sn = params.get("cou_sn")
    grade = params.get("grade")

    if stu_sn is None or cou_sn is None or grade is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, grade must be required")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = float(grade)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO course_grade (stu_sn, cou_sn, grade) 
            VALUES ( %(stu_sn)s, %(cou_sn)s, %(grade)s)
            """, dict(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生的课程成绩",
            "return": "/grade"
        })
        return web.HTTPFound(location=f"/error?{query}")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

    return web.HTTPFound(location="/grade")

@web_routes.post('/action/grade/select')
async def action_grade_select(request):
    print("select_name_action")
    params = await request.post()
    select_name = params.get("select_name")
    if(select_name==""):
        return web.HTTPFound(location="/grade")
    if select_name is None:
        return web.HTTPBadRequest(text="select_name must be required")
    with db_block() as db:
        db.execute("""
        select student.name as stu_name,course.name as cou_name,course_grade.grade as grade
        from course_grade,student,course
        where course_grade.stu_sn=student.sn and course_grade.cou_sn=course.sn and student.name=%(select_name)s
        """, dict(select_name=select_name))

        student_result = list(db)
        db.execute("""
        SELECT sn AS stu_sn, name as stu_name FROM student ORDER BY name
        """)
        students = list(db)

        db.execute("""
        SELECT sn AS cou_sn, name as cou_name FROM course ORDER BY name
        """)
        courses = list(db)
    return render_html(request, 'grade_list.html',
                       students=students,
                       courses=courses,
                       items=student_result)




@web_routes.post('/action/grade/select_grade')
async def action_grade_select(request):
    print("select_grade_name_action")
    params = await request.post()
    cou_sn = params.get("cou_sn")
    term = params.get("term")
    print(cou_sn,term)

    if(cou_sn=="" or term==""):
        return web.HTTPFound(location="/grade")
    if cou_sn is None or term is None:
        return web.HTTPBadRequest(text="select_name must be required")
    with db_block() as db:
        db.execute("""
        select student.name as stu_name,course.name as cou_name,course_grade.grade as grade
        from course_grade,student,course
        where course_grade.stu_sn=student.sn and course_grade.cou_sn=course.sn and course.sn=%(cou_sn)s and course.term=%(term)s;
        """, dict(cou_sn=cou_sn,term=term))
        student_result = list(db)

        print(student_result)
        db.execute("""
        SELECT sn AS stu_sn, name as stu_name FROM student ORDER BY name
        """)
        students = list(db)

        db.execute("""
        SELECT sn AS cou_sn, name as cou_name FROM course ORDER BY name
        """)
        courses = list(db)
    return render_html(request, 'grade_list.html',
                       students=students,
                       courses=courses,
                       items=student_result)

@web_routes.post('/action/grade/edit/{stu_sn}/{cou_sn}')
async def edit_grade_action(request):
    print("edit_action")
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    params = await request.post()
    grade = params.get("grade")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = float(grade)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    with db_block() as db:
        db.execute("""
        UPDATE course_grade SET grade=%(grade)s
        WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))

    return web.HTTPFound(location="/grade")


@web_routes.post('/action/grade/delete/{stu_sn}/{cou_sn}')
def delete_grade_action(request):
    print("deletion_action")
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        DELETE FROM course_grade
            WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

    return web.HTTPFound(location="/grade")
