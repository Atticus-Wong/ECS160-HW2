import csv
import requests
import sys


def load_posts(input_path):
    with open(input_path, mode="r", newline="") as file:
        return list(csv.DictReader(file))


def get_top_posts(posts, limit=10):
    sortedPosts = sorted(posts, key=lambda post: int(post["like_count"]), reverse=True)
    return sortedPosts[:limit]


def send_to_pipeline(post_content):
    """
    Send a post to the moderation service.
    Returns the hashtag string on success, or 'FAILED' if moderation fails.
    """
    response = requests.post(
        "http://localhost:8001/moderate", json={"post_content": post_content}
    )
    data = response.json()
    return data["result"]


def process_post(post, index):
    result = send_to_pipeline(post["text"])

    if result == "FAILED":
        print(f"Post {index}: [DELETED]")
    else:
        print(f"Post {index}: {post['text']} {result}")


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.csv"

    posts = load_posts(input_path)
    top_posts = get_top_posts(posts, limit=10)

    print(f"Processing {len(top_posts)} most-liked posts...\n")

    for i, post in enumerate(top_posts, start=1):
        process_post(post, i)


if __name__ == "__main__":
    main()
