from alchemyapi import AlchemyAPI
from flask import Flask, request
import jinja2
import json
import random
import nltk
from nltk import tokenize
from unidecode import unidecode

nltk.download('punkt')

TOPIC_ENTITIES_THRESHOLD = 0.5
TOPIC_KEYWORDS_THRESHOLD = 0.75
TOPIC_CONCEPTS_THRESHOLD = 0.75

ENTITY_SENTIMENT_THRESHOLD = 0.33
KEYWORD_SENTIMENT_THRESHOLD = 0.33

defaultDocs = [
"U.S. stocks finished little changed on Friday, but the Dow and the S&P 500 managed to log their best weekly gains since November, closing the curtain on a bumpy stretch of trading on Wall Street. A rally in the technology and consumer discretionary sectors eased a sharp selloff in the materials sector fueled by the drop in oil prices, while a reading on U.S. consumer inflation came in above economists' expectations. The S&P 500 SPX, +0.00% trimmed early losses to finish less than a point lower at 1,917.78. The materials sector fell the most, down 1.1%, while the consumer-discretionary sector led gainers, up 0.3%, followed by tech, up 0.2%. The index booked a 2.8% weekly gain, the largest weekly advance since Nov. 20. From http://www.marketwatch.com/story/wall-street-scrabbles-for-direction-ahead-of-inflation-data-2016-02-19", 
"U.S. stocks finished little changed on Friday, but the Dow and the S&P 500 managed to log their best weekly gains since November, closing the curtain on a bumpy stretch of trading on Wall Street. A rally in the technology and consumer discretionary sectors eased a sharp selloff in the materials sector fueled by the drop in oil prices, while a reading on U.S. consumer inflation came in above economists' expectations. The S&P 500 SPX, +0.00% trimmed early losses to finish less than a point lower at 1,917.78. The materials sector fell the most, down 1.1%, while the consumer-discretionary sector led gainers, up 0.3%, followed by tech, up 0.2%. The index booked a 2.8% weekly gain, the largest weekly advance since Nov. 20. From http://www.marketwatch.com/story/wall-street-scrabbles-for-direction-ahead-of-inflation-data-2016-02-19", 
"Apple's iPhone 5 received the biggest customer backlash following its launch in 2012, according to new research. One in five posts on social networks were critical of Apple's most recent handset, with the majority of people complaining about the introduction of a new power socket, the inaccuracy of Apple Maps and how similar the phone was to previous models. Samsung's Galaxy S4 received the least complaints - just 11 per cent - according to figures from analysts We Are Social. From http://www.dailymail.co.uk/sciencetech/article-2355833/Apples-iPhone-5-hated-handset--majority-people-love-Samsung-Galaxy-S4-study-finds.html#ixzz40sPfK3it",
"Florida plans to file a U.S. Supreme Court lawsuit against Georgia, saying the state is consuming too much water that would otherwise flow to Florida, the latest battle nationally over an increasingly scarce resource. The dispute is fueled by the rapid growth of the metropolitan area surrounding Atlanta, which is demanding more water and hurting the oyster industry in Northwest Florida, Florida Governor Rick Scott, 60, said yesterday. Scott, a Republican, said he would file suit next month after the two states couldn't reach an agreement. \"That's our water,\" Scott told reporters while standing next to the Apalachicola Bay in the Florida Panhandle. \"They've impacted our families. They've impacted the livelihood of people down here.\" From http://www.bloomberg.com/news/articles/2013-08-13/florida-to-sue-georgia-in-u-s-supreme-court-over-water",
"Credit cards offer many advantages. There is the convenience of being able to buy needed items now and the security of not having to carry cash. You also receive fraud protection and in some cases rewards for making purchases. With these advantages also come responsibilities. You need to manage credit cards wisely by understanding all of the card's terms and conditions; stay on top of payments; and realize the true cost of purchases made with credit. Using a credit card is like taking out a loan. If you don't pay your card balance in full each month, you'll pay interest on that loan."
]


alchemyapi = AlchemyAPI()

def annotate(s, entities, keywords):
	a = []

	for dic in [entities, keywords]:
		for key, value in dic.iteritems():

			if s.lower().find(key.lower()) != -1:
				a.append("Possible " + value + " bias towards \"" + key + "\"")

	if len(a) == 0: a = None

	return (s, a)

app = Flask(__name__)

jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("templates")
		)

def pprint(jsonData, title=None):
	pp = (title + "\n" if title else "") + json.dumps(jsonData, indent=4, separators=(',', ': '))
	return pp

@app.route("/", methods=["GET", "POST"])
def get_index():
	#if request.method == "POST":
	#	defaultDoc = request.form["doc"]
	#else:
	
	defaultDoc = random.choice(defaultDocs)
	template = jinja_env.get_template("index.html")
	return template.render(defaultDoc=defaultDoc)

@app.route("/result", methods=["POST"])
def get_result():
	reqDoc = request.form["doc"]
	try:
		doc = str(reqDoc)
	except UnicodeEncodeError:
		doc = unidecode(reqDoc)

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
		biasedEntities = {}
		for e in topicEntities:
			if "score" in e["sentiment"].keys():
				if (abs(float(e["sentiment"]["score"])) > ENTITY_SENTIMENT_THRESHOLD):
					biasedEntities[e["text"]] = e["sentiment"]["type"]

		biasedKeywords = {}
		for k in topicKeywords:
			if "score" in k["sentiment"].keys():
				if (abs(float(k["sentiment"]["score"])) > KEYWORD_SENTIMENT_THRESHOLD):
					biasedKeywords[k["text"]] = k["sentiment"]["type"]

		docSentences = tokenize.sent_tokenize(doc)

		sentencesAnnotated = [ annotate(s, biasedEntities, biasedKeywords) for s in docSentences]

		template = jinja_env.get_template("result.html")

		return template.render(sentences=sentencesAnnotated, doc=doc)
			
	else:
		return "There was an error!" + pprint("COMBINED", combined)

#	sentiment = alchemyapi.sentiment("text", doc)["docSentiment"]
#	epp = json.dumps(entities, sort_keys=True, indent=4, separators=(',', ': '))
#	kpp = json.dumps(keywords, sort_keys=True, indent=4, separators=(',', ': '))

app.run()
