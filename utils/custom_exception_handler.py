from datetime import date
from rest_framework import response, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler


def custom_exception_handler(exc,context):

    handlers={
        'ValidationError':_handle_generic_error,
        'Http404': _handle_generic_error,
        'PermissionDenied': _handle_generic_error,
        'NotAuthenticated': _handle_authentication_error,
        'InvalidToken' : _handle_authentication_error,
        'NotFound' : _handle_notfound_error,
        'PermissionDenied' : _handle_permissiondenied_error,
        }

    response=exception_handler(exc, context)

    if response is not None:
        if 'AuthUserAPIView' in str(context['view']) and exc.status_code == 401:
            response.status_code = 200
            response.data = {'is_logged_in':False,
                            'status_code': 200}
            return response
        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__
    
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response

def _handle_authentication_error(exc, context, response):
    response.data = {
        'code': 'HTTP_401_UNAUTHORIZED',
        'msg': 'Authentication credentials were not provided.',
    }

    return response
    
def _handle_generic_error(exc, context, response):
    return response

def _handle_notfound_error(exc, context, response):
    response.data = {
                    'code': 'HTTP_404_NOT_FOUND',
                    'msg': 'ไม่พบข้อมูล'
    }
    return response

def _handle_permissiondenied_error(exc, context, response):
    response.data = {
                    "code": "HTTP_403_FORBIDDEN",
                    "msg": "ไม่มีสิทธ์เข้าใช้งาน",
    }
    return response