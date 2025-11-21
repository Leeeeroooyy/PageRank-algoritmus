import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import numpy as np

BASE_URL = "https://realpython.com/"

def get_links(url, domain):
    try:
        html = requests.get(url, timeout=5).text
    except:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        full = urljoin(url, href)
        parsed = urlparse(full)

        if parsed.netloc == domain:
            clean = parsed.scheme + "://" + parsed.netloc + parsed.path
            links.append(clean)

    return list(set(links))

domain = urlparse(BASE_URL).netloc

level1 = get_links(BASE_URL, domain)
dataset = []

print("Found level-1 links:", len(level1))

for link in level1:
    level2 = get_links(link, domain)
    # add edges
    for tgt in level2:
        dataset.append((link, tgt))


dataset = list(set(dataset))

print("Dataset edges:", len(dataset))

nodes = sorted(set([src for src, _ in dataset] +
                   [dst for _, dst in dataset]))
N = len(nodes)
print("Number of pages:", N)

index = {url: i for i, url in enumerate(nodes)}

M = np.zeros((N, N))

for src, dst in dataset:
    j = index[src]
    i = index[dst]
    M[i][j] = 1.0

for col in range(N):
    s = M[:, col].sum()
    if s > 0:
        M[:, col] /= s
    else:
        M[:, col] = 1.0 / N

beta = 0.85
E = np.ones((N, N))
A = beta * M + (1 - beta) * (1.0 / N) * E

r = np.ones(N) / N  

for _ in range(50):
    r = A @ r

ranking = sorted([(nodes[i], r[i]) for i in range(N)],
                 key=lambda x: x[1], reverse=True)

print("\nTOP PAGES:")
for url, score in ranking[:30]:
    print(f"{score:.6f}  {url}")
