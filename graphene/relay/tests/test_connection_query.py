from collections import OrderedDict

from promise import Promise

from ..connection import ConnectionField, Connection, PageInfo
from ..node import Node
from graphql_relay.utils import base64
from ...types import ObjectType, String, Schema

letter_chars = ['A', 'B', 'C', 'D', 'E']


class Letter(ObjectType):
    class Meta:
        interfaces = (Node, )

    letter = String()


class MyLetterObjectConnection(Connection):
    extra = String()

    class Meta:
        node = Letter

    class Edge:
        other = String()

LetterConnection = Connection.for_type(Letter)


class Query(ObjectType):
    letters = ConnectionField(LetterConnection)
    letters_wrong_connection = ConnectionField(LetterConnection)
    letters_promise = ConnectionField(LetterConnection)
    letters_connection = ConnectionField(MyLetterObjectConnection)

    def resolve_letters(self, *_):
        return list(letters.values())

    def resolve_letters_wrong_connection(self, *_):
        return MyLetterObjectConnection()

    def resolve_letters_connection(self, *_):
        return MyLetterObjectConnection(
            extra='1',
            page_info=PageInfo(has_next_page=True, has_previous_page=False),
            edges=[MyLetterObjectConnection.Edge(cursor='1', node=Letter(letter='hello'))]
        )

    def resolve_letters_promise(self, *_):
        return Promise.resolve(list(letters.values()))

    node = Node.Field()


schema = Schema(Query)

letters = OrderedDict()
for i, letter in enumerate(letter_chars):
    l = Letter(id=i, letter=letter)
    letters[letter] = l


def edges(selected_letters):
    return [
        {
            'node': {
                'id': base64('Letter:%s' % l.id),
                'letter': l.letter
            },
            'cursor': base64('arrayconnection:%s' % l.id)
        }
        for l in [letters[i] for i in selected_letters]
    ]


def cursor_for(ltr):
    l = letters[ltr]
    return base64('arrayconnection:%s' % l.id)


def execute(args=''):
    if args:
        args = '(' + args + ')'

    return schema.execute('''
    {
        letters%s {
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''' % args)


def create_expexted_result(letters, has_previous_page=False, has_next_page=False, field_name='letters'):
    expected_edges = edges(letters)
    expected_page_info = {
        'hasPreviousPage': has_previous_page,
        'hasNextPage': has_next_page,
        'endCursor': expected_edges[-1]['cursor'] if expected_edges else None,
        'startCursor': expected_edges[0]['cursor'] if expected_edges else None
    }
    return {
        field_name: {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def check(args, letters, has_previous_page=False, has_next_page=False):
    result = execute(args)
    assert not result.errors
    assert result.data == create_expexted_result(letters, has_previous_page, has_next_page)


def test_resolver_throws_error_on_returning_wrong_connection_type():
    result = schema.execute('''
    {
        lettersWrongConnection {
            edges {
                node {
                    id
                }
            }
        }
    }
    ''')
    assert result.errors[0].message == ('Resolved value from the connection field has to be a LetterConnection. '
                                        'Received MyLetterObjectConnection.')


def test_resolver_handles_returned_connection_field_correctly():
    result = schema.execute('''
    {
        lettersConnection {
            extra
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    assert not result.errors
    expected_result = {
        'lettersConnection': {
            'extra': '1',
            'edges': [
                {
                    'node': {
                        'id': 'TGV0dGVyOk5vbmU=',
                        'letter': 'hello',
                    },
                    'cursor': '1'
                }
            ],
            'pageInfo': {
                'hasPreviousPage': False,
                'hasNextPage': True,
                'startCursor': None,
                'endCursor': None,
            }
        }
    }
    assert result.data == expected_result


def test_resolver_handles_returned_promise_correctly():
    result = schema.execute('''
    {
        lettersPromise {
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    assert not result.errors
    assert result.data == create_expexted_result('ABCDE', field_name='lettersPromise')


def test_returns_all_elements_without_filters():
    check('', 'ABCDE')


def test_respects_a_smaller_first():
    check('first: 2', 'AB', has_next_page=True)


def test_respects_an_overly_large_first():
    check('first: 10', 'ABCDE')


def test_respects_a_smaller_last():
    check('last: 2', 'DE', has_previous_page=True)


def test_respects_an_overly_large_last():
    check('last: 10', 'ABCDE')


def test_respects_first_and_after():
    check('first: 2, after: "{}"'.format(cursor_for('B')), 'CD', has_next_page=True)


def test_respects_first_and_after_with_long_first():
    check('first: 10, after: "{}"'.format(cursor_for('B')), 'CDE')


def test_respects_last_and_before():
    check('last: 2, before: "{}"'.format(cursor_for('D')), 'BC', has_previous_page=True)


def test_respects_last_and_before_with_long_last():
    check('last: 10, before: "{}"'.format(cursor_for('D')), 'ABC')


def test_respects_first_and_after_and_before_too_few():
    check('first: 2, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BC', has_next_page=True)


def test_respects_first_and_after_and_before_too_many():
    check('first: 4, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_respects_first_and_after_and_before_exactly_right():
    check('first: 3, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), "BCD")


def test_respects_last_and_after_and_before_too_few():
    check('last: 2, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'CD', has_previous_page=True)


def test_respects_last_and_after_and_before_too_many():
    check('last: 4, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_respects_last_and_after_and_before_exactly_right():
    check('last: 3, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_returns_no_elements_if_first_is_0():
    check('first: 0', '', has_next_page=True)


def test_returns_all_elements_if_cursors_are_invalid():
    check('before: "invalid" after: "invalid"', 'ABCDE')


def test_returns_all_elements_if_cursors_are_on_the_outside():
    check('before: "{}" after: "{}"'.format(base64('arrayconnection:%s' % 6), base64('arrayconnection:%s' % -1)), 'ABCDE')


def test_returns_no_elements_if_cursors_cross():
    check('before: "{}" after: "{}"'.format(base64('arrayconnection:%s' % 2), base64('arrayconnection:%s' % 4)), '')
