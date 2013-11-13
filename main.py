import web
import json
from basic_user import *

urls = (
    '/json', 'myapp'
)


class myapp:

    def POST(self):
        web_data = web.input()
        t_return = {}
        if web_data["class"] == "basic_user":
            t_return = basic_user.call_function(web_data)
        string_json = json.dumps(t_return)
        return string_json

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()