from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_jobs(user_skills, jobs):

    texts = [user_skills]

    for job in jobs:
        texts.append(job["skills"])

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )

    scores = similarity[0]

    result = []

    for i in range(len(jobs)):
        job = jobs[i]
        job["score"] = float(scores[i])
        result.append(job)

    result.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return result