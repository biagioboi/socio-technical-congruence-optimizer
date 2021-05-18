import requests, json
from requests.auth import HTTPBasicAuth


resp = requests.get('https://api.github.com/repos/immuni-app/immuni-app-android/issues', headers={'content-type': 'application/vnd.github.v3+json'}, auth = HTTPBasicAuth('biagioboi', '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'))
print(resp.status_code)
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))
else:
    for x in resp.json():
        resp2 = requests.get(x['comments_url'], headers={'content-type': 'application/vnd.github.v3+json'})
        print(json.dumps(resp2.json(), indent=4, sort_keys=True))
