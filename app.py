from alchemyapi import AlchemyAPI
from flask import Flask, request
import jinja2
import json
import re
import nltk
from nltk import tokenize

nltk.download('punkt')

TOPIC_ENTITIES_THRESHOLD = 0.5
TOPIC_KEYWORDS_THRESHOLD = 0.75
TOPIC_CONCEPTS_THRESHOLD = 0.75

ENTITY_SENTIMENT_THRESHOLD = 0.25
KEYWORD_SENTIMENT_THRESHOLD = 0.25
CONCEPT_SENTIMENT_THRESHOLD = 0.25

alchemyapi = AlchemyAPI()

def annotate(s, entities, keywords, concepts):
	a = []

	for dict in [entities, keywords, concepts]:
		for key, value in dict.iteritems():

			if s.find(key) > -1:
				a.append("Possible " + value + " bias towards " + key)

	if len(a) == 0: a = None

	return (s, a)

app = Flask(__name__)

jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("templates")
		)

def pprint(jsonData, title=None):
	pp = (title + "\n" if title else "") + json.dumps(jsonData, indent=4, separators=(',', ': '))
	return pp

@app.route("/")
def get_index():
	template = jinja_env.get_template("index.html")
	return template.render()

@app.route("/result", methods=["POST"])
def get_result():
	doc = str(request.form["doc"])

#	entities = alchemyapi.entities("text", doc, options={"sentiment":1})
#	keywords = alchemyapi.keywords("text", doc, options={"sentiment":1})

	combined = alchemyapi.combined("text", doc, options={"extract":"entity,keyword,concept", "sentiment":1})

	if combined["status"] == "OK":
		entities = combined["entities"]
		keywords = combined["keywords"]
		concepts = combined["concepts"]
		topicEntities = filter(lambda e: float(e["relevance"]) > TOPIC_ENTITIES_THRESHOLD, entities)
		topicKeywords = filter(lambda k: float(k["relevance"]) > TOPIC_KEYWORDS_THRESHOLD, keywords)
		topicConcepts = filter(lambda c: float(c["relevance"]) > TOPIC_CONCEPTS_THRESHOLD, concepts)
		biasedEntitiesList = filter(lambda e: float(e["sentiment"]["score"]) > ENTITY_SENTIMENT_THRESHOLD, entities)
		biasedEntities = {biasedEntitiesList[i]["text"]: biasedEntitiesList[i]["sentiment"]["type"] for i in range(len(biasedEntitiesList))}
		biasedKeywordsList = filter(lambda e: float(e["sentiment"]["score"]) > ENTITY_SENTIMENT_THRESHOLD, entities)
		biasedKeywords = {biasedKeywordsList[i]["text"]: biasedKeywordsList[i]["sentiment"]["type"] for i in range(len(biasedKeywordsList))}
		biasedConceptsList = filter(lambda e: float(e["sentiment"]["score"]) > ENTITY_SENTIMENT_THRESHOLD, entities)
		biasedConcepts = {biasedConceptsList[i]["text"]: biasedConceptsList[i]["sentiment"]["type"] for i in range(len(biasedConceptsList))}

		docSentences = tokenize.sent_tokenize(doc)

		sentencesAnnotated = [ annotate(s, biasedEntities, biasedKeywords, biasedConcepts) for s in docSentences]

		template = jinja_env.get_template("result.html")

		return template.render(sentences=sentencesAnnotated, extras=[
				pprint(topicEntities, "TOPIC ENTITIES"),
				pprint(topicKeywords, "TOPIC KEYWORDS"),
				pprint(topicConcepts, "TOPIC CONCEPTS"),
				pprint(combined, "COMBINED")
				])
			
	else:
		return "There was an error!" + pprint("COMBINED", combined)

#	sentiment = alchemyapi.sentiment("text", doc)["docSentiment"]
#	epp = json.dumps(entities, sort_keys=True, indent=4, separators=(',', ': '))
#	kpp = json.dumps(keywords, sort_keys=True, indent=4, separators=(',', ': '))

app.run(debug=True)
