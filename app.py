from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "http://20.244.56.144/test"

# 1. Get Top Users API
@app.route('/users', methods=['GET'])
def get_top_users():
    users_response = requests.get(f"{BASE_URL}/users")
    if users_response.status_code != 200:
        return jsonify({"error": "Failed to fetch users"}), 500
    
    users = users_response.json().get("users", [])
    user_post_counts = []

    for user in users:
        posts_response = requests.get(f"{BASE_URL}/users/{user['id']}/posts")
        if posts_response.status_code == 200:
            post_count = len(posts_response.json().get("posts", []))
            user_post_counts.append({"user": user['name'], "post_count": post_count})

    top_users = sorted(user_post_counts, key=lambda x: x["post_count"], reverse=True)[:5]
    return jsonify(top_users)

# 2. Get Top/Latest Posts API
@app.route('/posts', methods=['GET'])
def get_top_or_latest_posts():
    post_type = request.args.get('type', 'latest')
    users_response = requests.get(f"{BASE_URL}/users")

    if users_response.status_code != 200:
        return jsonify({"error": "Failed to fetch users"}), 500
    
    users = users_response.json().get("users", [])
    posts_data = []

    for user in users:
        posts_response = requests.get(f"{BASE_URL}/users/{user['id']}/posts")
        if posts_response.status_code == 200:
            posts_data.extend(posts_response.json().get("posts", []))

    if post_type == 'popular':
        post_comments_count = []
        for post in posts_data:
            comments_response = requests.get(f"{BASE_URL}/posts/{post['id']}/comments")
            if comments_response.status_code == 200:
                comment_count = len(comments_response.json().get("comments", []))
                post_comments_count.append({"post": post, "comments": comment_count})
        
        max_comments = max([p['comments'] for p in post_comments_count], default=0)
        popular_posts = [p['post'] for p in post_comments_count if p['comments'] == max_comments]
        return jsonify(popular_posts)

    elif post_type == 'latest':
        latest_posts = sorted(posts_data, key=lambda x: x['id'], reverse=True)[:5]
        return jsonify(latest_posts)

    return jsonify({"error": "Invalid type"}), 400

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/')
def home():
    return "Welcome to the API! Use '/get_top_or_latest_posts?type=top' or '/get_top_or_latest_posts?type=latest' to see results."