import csv
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def save_csv(filename, rows, header):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

print("\nTEST ON Ex. DATA")

edges = [
    (1, 2),
    (1, 3),
    (2, 4),
    (3, 1),
    (3, 2),
    (3, 4),
    (4, 3)
]

nodes_test = sorted(set([a for a, b in edges] + [b for a, b in edges]))
idx_test = {n: i for i, n in enumerate(nodes_test)}
N_test = len(nodes_test)

M_test = np.zeros((N_test, N_test))

for src, dst in edges:
    M_test[idx_test[dst], idx_test[src]] = 1

for col in range(N_test):
    s = M_test[:, col].sum()
    if s > 0:
        M_test[:, col] /= s
    else:
        M_test[:, col] = 1 / N_test

beta = 0.85
E_test = np.ones((N_test, N_test))
A_test = beta * M_test + (1 - beta) / N_test * E_test

r_test = np.ones(N_test) / N_test

print("r(0):", r_test)
for t in range(5):
    r_test = A_test @ r_test
    print(f"r({t+1}): {r_test}")

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
    return sorted(set(links))

domain = urlparse(BASE_URL).netloc

level1 = get_links(BASE_URL, domain)

print("\nLEVEL 1 LINKS:")
for link in level1:
    print(link)

save_csv("level1.csv", [[l] for l in level1], ["URL"])

dataset = []

for src in level1:
    level2 = get_links(src, domain)
    for dst in level2:
        dataset.append((src, dst))

dataset = sorted(set(dataset))

print("\nDATASET EDGES (first 20):")
for row in dataset[:20]:
    print(row)

save_csv("dataset.csv", dataset, ["Source", "Target"])

nodes = sorted(set([src for src, _ in dataset] + [dst for _, dst in dataset]))
N = len(nodes)
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

ranking = sorted([(nodes[i], float(r[i])) for i in range(N)], key=lambda x: x[1], reverse=True)

print("\nPAGE RANK r(50):")
for url, score in ranking[:20]:
    print(f"{score:.6f}  {url}")

save_csv("pagerank.csv", ranking, ["URL", "Rank"])
