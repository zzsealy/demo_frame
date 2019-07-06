# -*- coding:utf-8 -*-
'''
封装request 和 response
request获取环境信息并且转换成可供查找的字典。
'''


from six.moves import urllib
import http.client
from wsgiref.headers import Headers


# 封装request
class Request(object):
    def __init__(self, environ):
        self.environ = environ

    # property把方法变成属性
    @property
    def args(self):
        # 把查询参数转换成字典形式
        get_arguments = urllib.parse.parse_qs(
        self.environ['QUERY_STRING']
        )
        return {k: v[0] for k, v in get_arguments.items()}

    @property
    def path(self):
        return self.environ['PATH_INFO']


'''
实现response
1 返回内容 2 返回状态码  3 字符编码  4 返回类型
'''


class Response(object):
    def __init__(self, response=None, status=200, charset='utf-8', content_type='text/html'):
        self.response = [] if response is None else response
        self._status = status
        self.charset = charset
        self.headers = Headers()
        content_type = '{content_type}; charset={charset}'.format(content_type = content_type, charset=charset)
        self.headers.add_header('content_type', content_type)

    @property
    def status(self):
        status_string = http.client.responses.get(self._status, 'UNKNOWN')  # 如果没有status， 就回复UNKNOWN
        return '{status} {status_string}'.format(status=self._status, status_string = status_string)

    def __iter__(self):  # 如果response里面的值是bytes的话，就返回， 否则转换成设定的字符编码再返回。
        for val in self.response:
            if isinstance(val, bytes):
                yield val
            else:
                yield val.encode(self.charset)


'''
我们有了Request/Response函数之后，还需要一个转换函数， 
用来把之前的WSGI函数转换成使用我们的Request/Response对象的函数。
通过装饰器来实现这个功能。
'''


def request_response_application(func):
    def application(environ, start_response):
        request = Request(environ)
        response = func(request)
        start_response(
            response.status,
            response.headers.items()
        )
        return iter(response)
    return application


@request_response_application
def application(request):
    name = request.args.get('name', 'default_name')  # 查询字符串中的name
    return Response(['<h1>hello {name}</h1>'.format(name=name)])


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()