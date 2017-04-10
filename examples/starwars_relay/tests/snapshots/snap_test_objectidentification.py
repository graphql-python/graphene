# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_correctly_fetches_id_name_rebels 1'] = {
    'data': {
        'rebels': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
}

snapshots['test_correctly_refetches_rebels 1'] = {
    'data': {
        'node': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
}

snapshots['test_correctly_fetches_id_name_empire 1'] = {
    'data': {
        'empire': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
}

snapshots['test_correctly_refetches_empire 1'] = {
    'data': {
        'node': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
}

snapshots['test_correctly_refetches_xwing 1'] = {
    'data': {
        'node': {
            'id': 'U2hpcDox',
            'name': 'X-Wing'
        }
    }
}
