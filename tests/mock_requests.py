import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

import requests

_orgininal_requests_get = requests.get

_collected_responses = []

class MockingResponse:
    def __init__(self, text, status_code=200, error_msg=None):
        self.text = text
        self.status_code = status_code
        self.error_msg = error_msg
        self.encoding = 'utf8'

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException(self.error_msg)


mode = os.environ.get('PUBS_TESTS_MODE', 'MOCK')

if mode == 'MOCK':

    with open('test_apis_data.pickle', 'rb') as fd:
        _collected_responses.extend(pickle.load(fd))

    def mock_requests_get(*args, **kwargs):
        for args2, kwargs2, text, status_code, error_msg in _collected_responses:
            if args == args2 and kwargs == kwargs2:
                return MockingResponse(text, status_code, error_msg)
        raise KeyError('No stub data found for requests.get({}, {})'.format(args, kwargs))

elif mode == 'COLLECT':

    def mock_requests_get(*args, **kwargs):
        text, status_code, error_msg = None, None, None
        try:
            r = _orgininal_requests_get(*args, **kwargs)
            text, status_code = r.text, r.status_code
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
        key = (sorted(args), sorted((k, v) for k, v in kwargs.items()))

        _collected_responses.append((args, kwargs, text, status_code, error_msg))
        _save_collected_responses()

        return MockingResponse(text, status_code, error_msg)

    def _save_collected_responses():
        with open('test_apis_data.pickle', 'wb') as fd:
            pickle.dump(_collected_responses, fd, protocol=3)

elif mode == 'ONLINE':
    def mock_requests_get(*args, **kwargs):
        return _orgininal_requests_get(*args, **kwargs)
