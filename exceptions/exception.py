# -*- coding: utf-8 -*-
import sys
from werkzeug.utils import escape
from werkzeug.wrappers.response import Response
from werkzeug.exceptions import HTTPException


ERRCODES = {
    1000: '参数错误',
    5000: '短地址转换错误',
    # ************************ 用户 ************************ #
    10000: '找不到用户',
    10001: '用户已存在',
    # ************************ 直播间 ************************ #
    20000: '直播间不存在',
    20001: '直播间已存在',
    # ************************ 监测 ************************ #
    30000: '监测不存在',
    30001: '监测已存在',
    30002: '预约不存在',
    30003: '预约已存在'
}


class BaseException(Exception):

    code = 200
    errcode = None
    description = None

    def __init__(self, description=None, response=None):
        super(BaseException, self).__init__()
        if description is not None:
            self.description = description
        self.response = response

    @classmethod
    def wrap(cls, exception, name=None):
        """Create an exception that is a subclass of the calling HTTP
        exception and the ``exception`` argument.

        The first argument to the class will be passed to the
        wrapped ``exception``, the rest to the HTTP exception. If
        ``e.args`` is not empty and ``e.show_exception`` is ``True``,
        the wrapped exception message is added to the HTTP error
        description.

        .. versionchanged:: 0.15.5
            The ``show_exception`` attribute controls whether the
            description includes the wrapped exception message.

        .. versionchanged:: 0.15.0
            The description includes the wrapped exception message.
        """

        class newcls(cls, exception):
            _description = cls.description
            show_exception = False

            def __init__(self, arg=None, *args, **kwargs):
                super(cls, self).__init__(*args, **kwargs)

                if arg is None:
                    exception.__init__(self)
                else:
                    exception.__init__(self, arg)

            @property
            def description(self):
                if self.show_exception:
                    return "{}\n{}: {}".format(
                        self._description, exception.__name__, exception.__str__(self)
                    )

                return self._description

            @description.setter
            def description(self, value):
                self._description = value

        newcls.__module__ = sys._getframe(1).f_globals.get("__name__")
        name = name or cls.__name__ + exception.__name__
        newcls.__name__ = newcls.__qualname__ = name
        return newcls

    @property
    def name(self):
        return ERRCODES.get(self.errcode, "Unknown Error")

    def get_description(self, environ=None):
        return u"%s" % escape(self.description).replace("\n", "<br>")

    def get_body(self, environ=None):
        return (
                u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
                u"<title>%(code)s %(name)s</title>\n"
                u"<h1>%(name)s</h1>\n"
                u"%(description)s\n"
            ) % {
                "code": self.code,
                "name": escape(self.name),
                "description": self.get_description(environ),
            }


    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [("Content-Type", "text/html")]

    def get_response(self, environ=None):
        """Get a response object.  If one was passed to the exception
        it's returned directly.

        :param environ: the optional environ for the request.  This
                        can be used to modify the response depending
                        on how the request looked like.
        :return: a :class:`Response` object or a subclass thereof.
        """

        if self.response is not None:
            return self.response
        headers = self.get_headers(environ)
        return Response(self.get_body(environ), self.code, headers)

    def __call__(self, environ, start_response):
        """Call the exception as WSGI application.

        :param environ: the WSGI environment.
        :param start_response: the response callable provided by the WSGI
                               server.
        """
        response = self.get_response(environ)
        return response(environ, start_response)

    def __str__(self):
        code = self.code if self.code is not None else "???"
        return "%s %s: %s" % (code, self.name, self.description)

    def __repr__(self):
        code = self.code if self.code is not None else "???"
        return "<%s '%s: %s'>" % (self.__class__.__name__, code, self.name)


class InvalidParamsException(BaseException):
    errcode = 1000


class UserNotExistsException(BaseException):
    errcode = 10000


class TuNotExistsException(BaseException):
    errcode = 20000


class MonitorProjectNotExistsException(BaseException):
    errcode = 30000


class MonitorProjectAlreadyExistsException(BaseException):
    errcode = 30001


class MonitorReserveNotExistsException(BaseException):
    errcode = 30002


class MonitorReserveAlreadyExistsException(BaseException):
    errcode = 30003


class ShortUrlConvertException(BaseException):
    errcode = 5000


class DummyException(HTTPException):
    code = 400