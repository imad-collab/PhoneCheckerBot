import requests
from bs4 import BeautifulSoup

def scam_search(number: str):
    """
    Search DuckDuckGo for scam reports related to the number.
    """
    try:
        query = f"{number} scam OR spam OR fraud"
        url = "https://html.duckduckgo.com/html/"

        resp = requests.post(
            url,
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if resp.status_code != 200:
            return [f"❌ DuckDuckGo error {resp.status_code}"]

        # Parse results
        soup = BeautifulSoup(resp.text, "html.parser")
        results = [a.get_text() for a in soup.select(".result__snippet")]

        # Debug log in terminal
        print("\n🔎 [DuckDuckGo Debug]")
        print(f"Query: {query}")
        print(f"Status: {resp.status_code}")
        print("Raw snippet of HTML:")
        print(resp.text[:400])
        print("------ END RAW ------\n")

        return results[:5] if results else ["No scam reports found."]
    except Exception as e:
        return [f"❌ DuckDuckGo search failed: {e}"]
