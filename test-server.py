from flask import Flask, send_file
import build

app = Flask(__name__, static_url_path = '/unrendered')

## i hate this but its only for testing :/
@app.route('/')
def root():
    build.build()
    return send_file('rendered/index.html')

@app.route('/<path>')
def path(path):
    build.build()
    if path != 'favicon.ico':
        return send_file('rendered/' + path + '.html')
    return send_file('rendered/' + path)

@app.route('/<path>/<path2>')
def path2(path, path2):
    build.build()
    return send_file('rendered/' + path + '/' + path2)

@app.route('/<path>/<path2>/<path3>')
def path3(path, path2, path3):
    build.build()
    return send_file('rendered/' + path + '/' + path2 + '/' + path3)

if __name__ == '__main__':
    app.run(debug = True, port = 5000)