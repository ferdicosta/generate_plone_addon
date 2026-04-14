# -*- coding: utf-8 -*-
from contextlib import contextmanager
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from zope.interface import implementer, Interface

import json


@contextmanager
def as_superuser():
    """Context manager per eseguire codice come superuser"""
    old_sm = getSecurityManager()
    try:
        portal = api.portal.get()
        from AccessControl.User import UnrestrictedUser
        user = UnrestrictedUser('zope', '', ['Manager'], [])
        user = user.__of__(portal.acl_users)
        newSecurityManager(None, user)
        yield
    finally:
        setSecurityManager(old_sm)


def request_cache(key_suffix_func=None):
    def decorator(func):
        def wrapper(self):
            if key_suffix_func:
                suffix = key_suffix_func(self)
            else:
                suffix = self.context.UID()

            key = "_cache_{}_{}".format(func.__name__, suffix)

            if not hasattr(self.request, key):
                result = func(self)
                setattr(self.request, key, result)

            return getattr(self.request, key)

        return wrapper

    return decorator


class IUtils(Interface):
    """Utility"""


@implementer(IUtils)
class Utils(object):
    @staticmethod
    def is_admin():
        current = api.user.get_current()

        if current.getId() in ['zope']:
            return True

        return False

    @staticmethod
    def json_response_with_errors(errors, request):
        response = request.RESPONSE

        results = {
            'status': False,
            'type': 'validation',
            'data': {
                'errors': errors,
                'type': 'danger',
                'message': "Correggi gli errori evidenziati"
            }
        }

        data = json.dumps(results)

        response.setHeader("Content-type", "application/json")
        response.setHeader('Content-Length', len(data))

        return data

    @staticmethod
    def json_response_with_redirect(url, request, status_message=None):
        response = request.RESPONSE

        results = {
            'status': True,
            'type': 'redirect',
            'data': {
                'url': url
            }
        }

        data = json.dumps(results)

        if status_message:
            IStatusMessage(request).addStatusMessage(status_message, type = 'info')

        response.setHeader("Content-type", "application/json")
        response.setHeader('Content-Length', len(data))

        return data

    @staticmethod
    def remove_p_wrapper(html):
        html = html.strip()

        if html.startswith('<p>') and html.endswith('</p>'):
            html = html[3:-4]

        return html

    @staticmethod
    def text_to_html(text, remove_p_wrapper=False):
        portal_transforms = api.portal.get_tool('portal_transforms')
        transforms = getattr(portal_transforms, 'text_to_html')
        stream = transforms.convertTo('text/x-html-safe', text)
        html = stream.getData().strip()

        if remove_p_wrapper:
            if html.startswith('<p>') and html.endswith('</p>'):
                html = html[3:-4]

        return html

    @staticmethod
    def convert_bytes(size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = float(size)

        i = 0

        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1

        return f"{size:.2f} {units[i]}"
