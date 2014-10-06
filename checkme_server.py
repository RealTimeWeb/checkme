import os

from bottle import route, run, template
from bottle import request, response
from json import dumps

__version__ = '1'

def jsonify(**data):
    response.content_type = 'application/json'
    return dumps(data)

@route('/check/<name>')
def index(name):
    version = request.query.version or '1'
    if version != __version__:
        return jsonify(success=False, message="The server is using a different version of checkme than you are!\nPlease get the latest version at\n\thttp://think.cs.vt.edu/book/get_checkme/")
    output_file = os.path.join("instructor_tests",name+".py")
    if os.path.isfile(output_file):
        with open(output_file, "r") as of:
            data = of.read()
        return jsonify(success=True, output=data, version=version)
    else:
        return jsonify(success=False, message="There were no instructor tests found for {}.\nAre you sure that you've named your python file correctly?".format(name), version=version)

run(host='localhost', port=8080, reloader=True)