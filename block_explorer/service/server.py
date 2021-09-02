from flask import Flask, request, render_template_string, Markup, send_from_directory, render_template
from flask_bootstrap import Bootstrap
from service.modeling import load_data
import json


app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/health', methods=['GET'])
def health():
    return 'ok'


@app.route('/', methods=['GET'])
def index():
    data = load_data()
    print(json.dumps(data, indent=4))
    return render_template('index.html', data=data)


@app.route('/charts/<network>/<type>', methods=['POST'])
def charts(network, type):
    data = load_data()
    return data[network][type]


if __name__ == '__main__':
    app.run(debug=True)