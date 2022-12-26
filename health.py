import http.client

conn = http.client.HTTPSConnection("healthwise.p.rapidapi.com")

headers = {
    'X-RapidAPI-Key': "2f4c515745msh58baf53059bed97p107d5ajsnd14e2f3cb3c6",
    'X-RapidAPI-Host': "healthwise.p.rapidapi.com"
    }

conn.request("GET", "/body/diseases/%7Bbodypart%7D", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))