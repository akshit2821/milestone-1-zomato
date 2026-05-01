import { submitFeedback } from "../phases/phase4/api";

function RecommendationCard({ item, userId, onFeedback }) {
  const handleFeedback = async (scoreDelta) => {
    if (!userId) {
      onFeedback("Enter user ID to submit feedback.");
      return;
    }
    try {
      await submitFeedback({
        user_id: userId,
        restaurant_name: item.restaurant_name,
        score_delta: scoreDelta,
      });
      onFeedback(`✅ Feedback saved for ${item.restaurant_name}.`);
    } catch (error) {
      onFeedback(error.message);
    }
  };

  return (
    <article className="result-card animate-fadeInUp">
      <div className="result-header">
        <h3>🍴 {item.restaurant_name}</h3>
        <span className="rating">⭐ {item.rating.toFixed(1)}</span>
      </div>
      <p className="muted">🥘 {item.cuisine}</p>
      <p className="cost">💰 Estimated cost for two: INR {item.estimated_cost}</p>
      <p className="explanation">💭 {item.explanation}</p>
      <div className="feedback-actions">
        <button type="button" onClick={() => handleFeedback(0.5)} className="pulse-on-hover">
          👍 Helpful
        </button>
        <button type="button" className="ghost pulse-on-hover" onClick={() => handleFeedback(-0.5)}>
          👎 Not relevant
        </button>
      </div>
    </article>
  );
}

export default RecommendationCard;
