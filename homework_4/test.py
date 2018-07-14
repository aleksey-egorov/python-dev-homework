import unittest
import functools

import api



def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                print ("\n---\nCase {}: ".format(c))
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)


    @cases([
        {"account": "horns&hoofs", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f"},
        {"account": "h12324oofs", "methods": "online_score", "token": "", "arguments": {}},
    ])
    def test_invalid_request(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)


    @cases([
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ])
    def test_invalid_request(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)

if __name__ == "__main__":
    unittest.main()
