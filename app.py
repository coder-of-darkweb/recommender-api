

from flask import Flask, request, jsonify
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)

client = MongoClient("mongodb+srv://aishwaryapanja682:7pgneBGbCIWo4JAN@cluster0.tutq4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["blogs"]

def preprocess_blog(blog):
    title = blog.get("title", "")
    content_data = blog.get("content", "")
    tags_data = blog.get("tags", [])
    author = blog.get("author", "")

    # Convert to strings if needed
    if isinstance(content_data, list):
        content_data = " ".join([str(item) for item in content_data])
    if isinstance(tags_data, list):
        tags_data = " ".join(tags_data)

    content = re.sub(r"<[^>]+>", "", str(content_data))
    tags = str(tags_data)
    author = str(author)

    combined = f"{title} {content} {tags * 3} {author * 2}".lower()
    return combined


@app.route("/recommend/<string:blog_id>", methods=["GET"])
def recommend(blog_id):
    from bson import ObjectId

    try:
        all_blogs = list(collection.find())
        blog_index = next((i for i, b in enumerate(all_blogs) if str(b["_id"]) == blog_id), None)

        if blog_index is None:
            return jsonify({"error": "Blog ID not found"}), 404

        texts = [preprocess_blog(blog) for blog in all_blogs]
        tfidf = TfidfVectorizer(stop_words="english")
        vectors = tfidf.fit_transform(texts)
        similarity = cosine_similarity(vectors)

        scores = list(enumerate(similarity[blog_index]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:11]

        recommendations = [str(all_blogs[i]["_id"]) for i, _ in scores]
        return jsonify({"recommended": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Blog Recommender API is Live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
