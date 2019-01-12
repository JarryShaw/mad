# -*- coding: utf-8 -*-

import datetime
import json


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, bytes):
            return {'val': obj.hex(), '_spec_type': 'bytes'}
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, set):
            return {'val': list(obj), '_spec_type': 'set'}
        else:
            return super().default(obj)


def object_hook(obj):
    _spec_type = obj.get('_spec_type')
    if _spec_type:
        if _spec_type == 'bytes':
            return bytes.fromhex(obj['val'])
        if _spec_type == 'set':
            return set(obj['val'])
        return obj
    return obj
