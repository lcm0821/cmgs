

from datetime import datetime, date #类
import json#模块


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):#isinstance用于判断o是否为date或datetime类型如果是则返回true
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def json_dumps(obj):
    return json.dumps(obj, cls=JSONEncoder)


def json_loads(s):
    return json.loads(s)  #通过json中loads方法将其转变成python中的字典对象来出来
