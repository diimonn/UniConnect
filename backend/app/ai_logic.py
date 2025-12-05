def recommend_universities(universities, user_score):
    result = []

    for uni in universities:
        probability = (user_score / uni.min_score)

        if probability > 1:
            probability = 1

        result.append({
            "name": uni.name,
            "city": uni.city,
            "score_required": uni.min_score,
            "your_score": user_score,
            "probability": round(probability * 100, 1)
        })

    result.sort(key=lambda x: x["probability"], reverse=True)
    return result
