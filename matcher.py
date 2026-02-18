import re

def clean_text(text):
    if not text:
        return ""
    # Remove emojis, special characters, and lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.lower()

def calculate_similarity(my_interests, target_text):
    """
    Calculates Jaccard similarity between my interests and target profile text.
    Pure Python version - no sklearn required.
    """
    if not target_text:
        return 0, []

    target_text = clean_text(target_text)
    target_words = set(target_text.split())
    
    my_interests_cleaned = [clean_text(i) for i in my_interests]
    my_interest_words = set()
    for i in my_interests_cleaned:
        my_interest_words.update(i.split())
    
    # Simple keyword check for finding 'common' interests
    common_interests = [interest for interest in my_interests if clean_text(interest) in target_text]
    
    if not my_interest_words or not target_words:
        return 0, common_interests

    # Jaccard Similarity
    intersection = my_interest_words.intersection(target_words)
    union = my_interest_words.union(target_words)
    
    # Boost if common interests found
    similarity = len(intersection) / len(union)
    if common_interests:
        similarity += 0.1 * len(common_interests) # Boost for exact matches
        
    return min(similarity, 1.0), common_interests

if __name__ == "__main__":
    # Test cases
    my_interests = ["coding", "python", "gaming", "sushi"]
    
    target_bio_1 = "Python developer | I love coding and gaming"
    score_1, common_1 = calculate_similarity(my_interests, target_bio_1)
    print(f"Match 1: Score {score_1:.2f}, Common: {common_1}")
    
    target_bio_2 = "Fashion model | Traveling the world"
    score_2, common_2 = calculate_similarity(my_interests, target_bio_2)
    print(f"Match 2: Score {score_2:.2f}, Common: {common_2}")
