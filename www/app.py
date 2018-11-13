# -*- coding: utf-8 -*-


# import the Flask class from the flask module
from flask import Flask, render_template

# create the application object
app = Flask(__name__, static_url_path='/img', static_folder='verndors', template_folder='pages')

# use decorators to link the function to a url
@app.route('/')
def home():
    return "Hello, World!"  # return a string

@app.route('/about')
def welcome():
    return render_template('about.html')  # render a template

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
