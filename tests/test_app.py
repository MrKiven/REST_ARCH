# -*- coding: utf-8 -*-

import mock
import rest_arch.app as app


def test_app():
    mock_obj = mock.Mock(return_value="app")
    with mock.patch.object(app, 'make_app', mock_obj):
        res = app.make_app("test")
        assert res == "app"
