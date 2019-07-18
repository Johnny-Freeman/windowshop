'''
	Functions to Aid in class management in Python
'''
import json


class importDict_Xeye(object):
    """
		https://stackoverflow.com/questions/1305532/convert-python-dict-to-object/31569634#31569634
	"""
    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return importDict_Xeye(value) if isinstance(value, dict) else value

def string2Object(str):
	'''
		str2dict = json.loads(str)
		return importDict_Xeye(str2dict)
	'''
	return importDict_Xeye(json.loads(	str.encode('ascii', 'ignore')	))

def dict2obj(d):
	"""
		https://stackoverflow.com/questions/1305532/convert-python-dict-to-object/31569634#31569634
	"""
        if isinstance(d, list):
            d = [dict2obj(x) for x in d]
        if not isinstance(d, dict):
            return d
        class importDict(object):
            pass
        o = importDict()
        for k in d:
            o.__dict__[k] = dict2obj(d[k])
        return o

def jsondump_str(obj):
	'''
		wraps json's str dump into something more readable
	'''
	return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=None)

'''
	Class includes, functions, modifiers
'''	
def cl_funct_addobj(self,objname,obj, sub=None):
	'''
		Post init adds obj to current level, include in classes
		For nested inserts, place in parent class!
		setattr is a python funct
	'''
	setattr(self, objname, obj)