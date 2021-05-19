import requests, json
from requests.auth import HTTPBasicAuth

session = requests.Session()
session.auth = ("username", "tokenAuth")


class ExtractDevelopersCommunicationInfo:

    def __init__(self, repository_name):
        self._repository_name = repository_name

    def get_issues(self):
        # E' possibile prendere solo una pagina per volta, e per ogni pagina al più 100 issues,
        # per cui bisognerebbe ciclare per almeno le prime 10 pagine per avere un buon dataset
        issues = session.get(
                    'https://api.github.com/repos/' + self._repository_name + '/issues',
                     headers={'content-type': 'application/vnd.github.v3+json'},
                     params={'page': 1, 'per_page': 100})
        to_return = dict()
        if issues.status_code != 200:
            print(issues.json())
            raise ApiError('GET /issues/ {}'.format(resp.status_code))
        else:
            for x in issues.json():
                to_return[x['number']] = x['comments_url']

        return to_return

    def get_contributors_for_issue(self, comments_urls):
        to_return = dict()
        for k, v in comments_urls.items():
            to_return[k] = dict()
            comments = session.get(v,
                                    headers={'content-type': 'application/vnd.github.v3+json'})
            if comments.status_code != 200:
                raise ApiError('GET /issues/ {}'.format(comments.status_code))
            else:
                for item in comments.json():
                    if item['author_association'] != "NONE":
                        if item['user']['login'] in to_return[k]:
                            to_return[k][item['user']['login']] = to_return[k][item['user']['login']] + 1
                        else:
                            to_return[k][item['user']['login']] = 1
        return to_return


z = ExtractDevelopersCommunicationInfo('PrestaShop/PrestaShop')
print(z.get_contributors_for_issue(z.get_issues()))
