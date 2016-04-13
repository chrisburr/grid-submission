import collections
import json

import gevent

from . import db


def _print_summary():
    counter = collections.Counter()
    for k, v in db.RangeIter():
        obj = json.loads(v)
        counter[obj['status']] += 1
    display = [
               ('S', 'Submitted'),
               ('R', 'Received'),
               ('W', 'Waiting'),
               ('M', 'Matched'),
               ('R', 'Running'),
               ('D', 'Done'),
               ('F', 'Failed'),
              ]
    output = []
    for d in display:
        output.append('{}: {: 3d}'.format(d[0], counter[d[1]]))
    print('\t'.join(output))
    gevent.sleep(5)
    gevent.spawn(_print_summary)


def start_ui():
    gevent.spawn(_print_summary)


__all__ = [
    start_ui
]
