from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.template import Library
from django.forms.models import model_to_dict
import json, decimal, uuid, datetime

register = Library()

def jsonify(object):
    if isinstance(object, QuerySet):
        return mark_safe(serialize('json', object))
    return mark_safe(json.dumps(object))

register.filter('jsonify', jsonify)
jsonify.is_safe = True  


"""
Alternate method returns unparsable JSON...

def jsonify(obj):
    if isinstance(obj, QuerySet):
    	json_obj = []
    	for inst in obj:
    		dict_inst = model_to_dict(inst)
    		json_dict = mark_safe(json.dumps(dict_inst, cls=RobustJSONEncoder))
    		json_obj.append(json_dict)
        return json_obj
    return mark_safe(json.dumps(obj, cls=RobustJSONEncoder))

class DateTimeJSONEncoder(json.JSONEncoder):
   def default(self, obj):
       for cls in (datetime.date, datetime.datetime, datetime.time):
           if isinstance(obj, cls):
               return obj.isoformat()

       return json.JSONEncoder.default(self, obj)

class RobustJSONEncoder(DateTimeJSONEncoder):
   def default(self, obj):
       if isinstance(obj, decimal.Decimal):
           return float(obj)
       elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
           return obj.to_dict()
       elif isinstance(obj, uuid.UUID):
           return str(obj)

       return DateTimeJSONEncoder.default(self, obj)
"""

