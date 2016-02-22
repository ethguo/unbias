import requests

if __name__ == "__main__":
	r = requests.post("https://amtera.p.mashape.com/relatedness/en",
		headers={
			"X-Mashape-Key": "KqUshZHH0Fmsh0oljgKXL2V2D3Yfp1T2Ju9jsnRxW7bkX1yiOZ",
			"Content-Type": "application/json",
			"Accept": "application/json"
		},
		json={
			"t1": "artificial intelligence", "t2":"computer science"
		}
	)

	print r.headers
	print r.text