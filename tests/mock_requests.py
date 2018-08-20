"""
Mock the `requests.get` function, and handle collecting data to do so.

Three modes are available, and controlled via the `PUBS_TESTS_MODE` environment
variable. To modify the variable, under linux or macos, do one of:
$ export PUBS_TESTS_MODE=MOCK
$ export PUBS_TESTS_MODE=COLLECT
$ export PUBS_TESTS_MODE=ONLINE

The MOCK mode is the default one, active even if PUBS_TESTS_MODE has not been
set. It uses saved data to run pubs units tests relying on the `requests.get`
function without the need of an internet connection (it is also much faster).
The prefected data is save in the `test_apis_data.pickle` file.

The COLLECT mode does real GET requests, and updates the `test_apis_data.pickle`
file. It is needed if you add or modify the test relying on `requests.get`.

The ONLINE mode bypasses all this and use the original `requests.get` without
accessing or updating the `test_apis_data.pickle` data. It might be useful when
running tests on Travis for instance.
"""


import os
import json
import mock

import requests


_orgininal_requests_get = requests.get
_collected_responses = []
_data_filepath = os.path.join(os.path.dirname(__file__), 'test_apis_data.json')


class MockingResponse:
    def __init__(self, text, status_code=200, error_msg=None):
        self.text = text
        self.status_code = status_code
        self.error_msg = error_msg
        self.encoding = 'utf8'

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException(self.error_msg)


def intercept_text(text):
    try:
        if '10.1103/PhysRevD.89.084044' in text:
            # replace with wrong DOI
            text = text.replace('PhysRevD', 'INVALIDDOI')
    except TypeError:
        if b'10.1103/PhysRevD.89.084044' in text:
            # replace with wrong DOI
            text = text.replace(b'PhysRevD', b'INVALIDDOI')

    return text


mode = os.environ.get('PUBS_TESTS_MODE', 'MOCK')

if mode == 'MOCK':

    with open(os.path.join(_data_filepath), 'r') as fd:
        _collected_responses = json.load(fd)

    def mock_requests_get(*args, **kwargs):
        for args2, kwargs2, text, status_code, error_msg in _collected_responses:
            if list(args) == list(args2) and kwargs == kwargs2:
                return MockingResponse(text, status_code, error_msg)
        raise KeyError(('No stub data found for requests.get({}, {}).\n You may'
                        ' need to update the mock data. Look at the '
                        'tests/mock_requests.py file for an explanation').format(args, kwargs))

elif mode == 'COLLECT':

    def mock_requests_get(*args, **kwargs):
        text, status_code, error_msg = None, None, None
        try:
            r = _orgininal_requests_get(*args, **kwargs)
            text, status_code = r.text, r.status_code
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)

        text = intercept_text(text)
        _collected_responses.append((args, kwargs, text, status_code, error_msg))
        _save_collected_responses() # yes, we save everytime, because it's not
                                    # clear how to run once after all the tests
                                    # have run. If you figure it out...

        return MockingResponse(text, status_code, error_msg)

    def _save_collected_responses():
        with open(os.path.join(_data_filepath), 'w') as fd:
            json.dump(sorted(_collected_responses), fd, indent=2)

elif mode == 'ONLINE':
    def mock_requests_get(*args, **kwargs):
        # with mock.patch('requests.Response.text', new_callable=mock.PropertyMock) as mock_text:
        r = _orgininal_requests_get(*args, **kwargs)
        r._content = intercept_text(r.content)
            # print(r.content.__class__)
            # mock_text.return_value = intercept_text(r.text)
        return r
