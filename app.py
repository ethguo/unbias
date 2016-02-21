from alchemyapi import AlchemyAPI
from flask import Flask, request
import jinja2

alchemyapi = AlchemyAPI()

jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("templates")
		)

app = Flask(__name__)

@app.route("/")
def get_index():
	template = jinja_env.get_template("index.html")
	return template.render()

@app.route("/response", methods=["POST"])
def get_response():
	doc = str(request.form["doc"])
	alchemy = alchemyapi.sentiment("text", doc)
	try:
		res = alchemy["docSentiment"]
	except KeyError:
		res = alchemy
	return str(res)

app.run(debug=True)