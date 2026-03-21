from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

class SentimentEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_score(self, news_items: list) -> dict:
        """
        Calculates an average sentiment score from a list of news headlines.
        Returns a dict with score and label.
        """
        if not news_items:
            return {"score": 0.0, "label": "Neutral", "count": 0}
        
        scores = []
        for item in news_items:
            title = item.get("title", "")
            if title:
                scores.append(self.analyzer.polarity_scores(title)["compound"])
        
        if not scores:
            return {"score": 0.0, "label": "Neutral", "count": 0}
            
        avg_score = float(np.mean(scores))
        
        if avg_score > 0.15:
            label = "Positive"
        elif avg_score < -0.15:
            label = "Negative"
        else:
            label = "Neutral"
            
        return {
            "score": round(avg_score, 3),
            "label": label,
            "count": len(scores)
        }
