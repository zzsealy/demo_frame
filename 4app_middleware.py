
'''
这个文件实现了基本的路由功能

实现方法：
 1 维护一个请求路径到可调用对象的 tuple列表。
 2 每次从列表中查找请求路径是否满足当前的pattern
 3 满足则调用当前pattern对应的可调用对象进行处理。 否则抛出异常返回404 response
'''

from six.moves import urllib
import http.client
from wsgiref.headers import Headers
import re

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





class NotFoundError(Exception):
    pass


class DecoratorRouter:
    def __init__(self):
        self.routing_table = []   # 一个列表，每个列表是元组， 元组的值是 url, parttern, 可调用对象
    '''
    def add_router(self, pattern, callback):
        self.routing_table.append((pattern, callback))   # callback是可调用对象
    '''
    def match(self, path):          # 迭代routing_table， 并且用正则表达式匹配。
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())   # 返回可调用对象和参数
        raise NotFoundError()

    def __call__(self, pattern):
        def _(func):
            self.routing_table.append((pattern, func))
        return _


routers = DecoratorRouter()


@routers(r'/hello/(.*)/$')
def hello(request, name):
    return Response("<h1>Hello, {name}</h1>".format(name=name))


@routers(r'/goodbye/(.*)/$')
def goodbye(request, name):
    return Response("<h1>Goodbye, {name}</h1>".format(name=name))


class Application(object):

    def __init__(self, routers, **kwargs):
        self.routers = routers

    def __call__(self, environ, start_response):
        try:
            request = Request(environ)
            callback, args = routers.match(request.path)
            response = callback(request, *args)
        except NotFoundError:
            response = Response("<h1>Not, found</h1>", status = 404)
        start_response(response.status, response.headers.items())
        return iter(response)


class UppercaseMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        for data in self.app(environ. start_response):
            yield data.upper()


application = UppercaseMiddleware(Application(routers))

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()
