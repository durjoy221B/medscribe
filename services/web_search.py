
from tavily import TavilyClient
from rapidfuzz import fuzz
from config.load_env import TAVILY_API_KEY

def calculate_similarity(source_text: str, target_text: str) -> float:
    """
    Compute fuzzy similarity between two strings (0.0 – 1.0).
    """
    return fuzz.ratio(source_text.lower(), target_text.lower()) / 100


def extract_primary_word(text: str) -> str:
    """
    Extract the first meaningful word (assumed medicine name) from a title.
    """
    words = text.replace('-', ' ').replace('|', ' ').split()
    return words[0] if words else ""


def find_best_medicine_match(
    search_text: str,
    reference_name: str,
    similarity_threshold: float = 0.7
) -> str:
    """
    Search for medicines using Tavily and return the best fuzzy-matched name.

    Args:
        search_text (str): The full search query used for Tavily search.
        reference_name (str): The medicine name to compare against (e.g., "Topuva").
        similarity_threshold (float): Minimum similarity score (default 0.7 for 70%).

    Returns:
        str: The best matching medicine name or 'Not found' if no match exceeds the threshold.
    """
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    search_response = tavily_client.search(
        query=search_text,
        max_results=20,
        country="Bangladesh"
    )

    search_results = search_response.get("results", [])

    # Domains relevant to medicine listings
    allowed_domains = [
        "medex", "arogga", "medeasy", "epharma",
        "othoba", "inceptapharma", "osudpotro",
        "lazzpharma", "chaldal", "medsbd"
    ]

    # Filter search results to keep only those from allowed domains
    valid_results = [
        result for result in search_results
        if any(domain in result["url"].lower() for domain in allowed_domains)
    ]

    best_match_name = "Sorry can't detect the correct name"
    highest_similarity = 0.0

    # Evaluate fuzzy similarity for each valid result
    for result in valid_results:
        title_text = result["title"]
        candidate_name = extract_primary_word(title_text)

        similarity_score = calculate_similarity(reference_name, candidate_name)

        # Keep the highest-scoring valid match
        if similarity_score >= similarity_threshold and similarity_score > highest_similarity:
            best_match_name = candidate_name
            highest_similarity = similarity_score

    return best_match_name
