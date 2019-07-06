# -*- coding:utf-8 -*-
'''
关于 WSGI， 全称Web Server Gateway Interface， 其实可以说是一个协议规范。
描述了web server(Gunicorn, uWSGI等）,如何与web application(flask, django等进行交互), web application如何处理请求
'''


# 定义一个简单的application
def application(environ, start_response):   # environ是取决于web server
    '''
        application 就是 WSGI app， 是一个可调用对象。
        参数：
            environ：一个包含WSGI环境信息的字典，由WSGI服务器提供，常见的key有PATH_INFO, QUERY_STRING等
            start_response: 生成WSGI响应的回调函数，接受两个参数， status和headers
        函数返回响应体的迭代器
        '''
    import pprint
    pprint.pprint(environ)  # 为了以字典形式打印出都有什么环境变量的值.
    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html; charset=utf8')
    ]
    # 举个例子 比如输入http://localhost:8000/?name=join  返回 hello join
    query_string = environ['QUERY_STRING'] # 从环境变量获取值，environ其实就是一个字典，可以从pprint(environ)证实
    name = query_string.split("=")[1]   # 以等号分隔开，取第二个的值

    start_response(status, headers)
    return [b"<h1>Hello,{}! </h1>".format(name)]  # 最后返回的是一个可迭代的bytes序列


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()

