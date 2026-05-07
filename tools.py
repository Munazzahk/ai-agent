import requests

def invert_abstract(inv):
    """Convert OpenAlex inverted index into readable text"""
    if not inv:
        return None

    words = []
    for word, positions in inv.items():
        for pos in positions:
            words.append((pos, word))

    return " ".join(word for _, word in sorted(words))


def search_papers(query):
    url = "https://api.openalex.org/works"

    params = {
    "search": query.replace("-", " "),
    "per-page": 20,
    "sort": "cited_by_count:desc"
    }  

    r = requests.get(url, params=params)
    data = r.json()

    papers = []

    for item in data.get("results", []):

        abstract = invert_abstract(item.get("abstract_inverted_index"))

        papers.append({
            "title": item.get("title"),
            "authors": [
                a["author"]["display_name"]
                for a in item.get("authorships", [])
            ],
            "year": item.get("publication_year"),
            "citations": item.get("cited_by_count", 0),
            "url": item.get("id"),
            "abstract": abstract
        })

    return papers