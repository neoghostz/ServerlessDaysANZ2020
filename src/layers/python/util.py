import uuid
from datetime import date, datetime

def unquie_uuid():
    return str(uuid.uuid4())

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))