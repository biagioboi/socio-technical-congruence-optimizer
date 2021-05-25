import requests
import matplotlib.pyplot as plt
import networkx as nx

session = requests.Session()
session.auth = ("username", "authToken")


class ExtractDevelopersCommunicationInfo:

    def __init__(self, repository_name):
        self._repository_name = repository_name
        self._graph = nx.Graph()
        self._contributors = dict()

    def get_communications_between_contributors(self):
        contributors_for_issue = self.get_contributors_for_issue(self.get_issues())
        contributors = dict()
        # for each item we have an issue with related devs that took part of issue with related interactions
        for issue_id, devs in contributors_for_issue.items():
            if len(devs) > 1:  # if empty or equal to 1, we don't consider it
                for k, v in devs.items():  # for each dev
                    if k not in contributors:  # if we haven't seen this dev, we initialize him
                        contributors[k] = dict()
                    for k1, v1 in devs.items():
                        if k1 == k:
                            continue
                        if k1 not in contributors[k]:
                            contributors[k][k1] = 0
                        contributors[k][k1] += v1
        self._contributors = contributors
        return self.construct_graph()

    def construct_graph(self):
        y = self._graph
        for contributor, devs in self._contributors.items():
            for dev, val in devs.items():
                y.add_edge(contributor, dev, weight=val)

        pos = nx.spring_layout(y)
        nx.draw_networkx_nodes(y, pos, node_size=70)
        nx.draw_networkx_edges(y, pos, edgelist=y.edges, edge_color="b", style="solid")
        nx.draw_networkx_labels(y, pos, font_size=5, font_family="sans-serif")

        plt.axis("off")
        plt.show()
        return True

    def get_issues(self):
        # It's possible to catch only one page for time, and for each page at most 100 issues
        # so we should consider at least 10 pages to have a good dataset
        issues = session.get(
                    'https://api.github.com/repos/' + self._repository_name + '/issues',
                     headers={'content-type': 'application/vnd.github.v3+json'},
                     params={'page': 1, 'per_page': 30})
        to_return = dict()
        if issues.status_code != 200:
            print(issues.json())
            raise ApiError('GET /issues/ {}'.format(issues.status_code))
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
print(z.get_communications_between_contributors())
