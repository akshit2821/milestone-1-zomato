import { useMemo, useState } from "react";
import RecommendationCard from "./components/RecommendationCard";
import { fetchRecommendations } from "./phases/phase4/api";
import { QUICK_MOODS, applyMood, surpriseMe } from "./phases/phase5/interaction";
import "./App.css";

// Add premium animations
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }
  
  .animate-fadeInUp {
    animation: fadeInUp 0.6s ease-out;
  }
  
  .shimmer {
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
  }
  
  .pulse-on-hover:hover {
    animation: pulse 0.3s ease-in-out;
  }
`;
if (!document.head.querySelector('style[data-premium-animations]')) {
  style.setAttribute('data-premium-animations', 'true');
  document.head.appendChild(style);
}

const initialForm = {
  user_id: "user-001",
  location: "Delhi",
  budget: "medium",
  cuisine: "chinese",
  min_rating: 4.0,
  optional_preferences: "quick service",
  top_n: 5,
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [feedbackToast, setFeedbackToast] = useState("");
  const [result, setResult] = useState(null);
  const [streak, setStreak] = useState(0);

  const fallbackMessage = useMemo(() => {
    if (!result?.meta?.fallback_used) return "";
    return result.meta.fallback_reason || "Fallback was applied to find useful alternatives.";
  }, [result]);

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setFeedbackToast("");
    setLoading(true);
    try {
      const payload = {
        user_id: form.user_id || undefined,
        location: form.location.trim(),
        budget: form.budget.trim(),
        cuisine: form.cuisine.trim(),
        min_rating: Number(form.min_rating),
        optional_preferences: form.optional_preferences
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        top_n: Number(form.top_n),
      };
      const response = await fetchRecommendations(payload);
      setResult(response);
      setStreak((prev) => prev + 1);
    } catch (requestError) {
      setError(requestError.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page animate-fadeInUp">
      <section className="hero shimmer">
        <div>
          <p className="pill">✨ AI Powered Recommendations</p>
          <h1>🍽️ Find your next meal in seconds</h1>
          <p className="hero-subtitle">
            Modern, explainable recommendations powered by deterministic filtering, LLM reasoning,
            and phase-wise personalization.
          </p>
          <div className="hero-stats">
            <span>🔥 Discovery streak: {streak}</span>
            <span>⚡ {result ? `${result.meta.processing_time_ms} ms` : "Ready"}</span>
          </div>
        </div>
      </section>

      <section className="panel animate-fadeInUp">
        <h2>🎯 Preference Form</h2>
        <div className="mood-row">
          {QUICK_MOODS.map((mood) => (
            <button
              key={mood.label}
              type="button"
              className="chip pulse-on-hover"
              onClick={() => setForm((prev) => applyMood(prev, mood))}
            >
              {mood.emoji} {mood.label}
            </button>
          ))}
          <button
            type="button"
            className="chip surprise pulse-on-hover"
            onClick={() => setForm((prev) => surpriseMe(prev))}
          >
            🎲 Surprise Me
          </button>
        </div>
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            User ID
            <input name="user_id" value={form.user_id} onChange={onChange} placeholder="user-001" />
          </label>
          <label>
            Location
            <input name="location" value={form.location} onChange={onChange} required />
          </label>
          <label>
            Budget
            <input name="budget" value={form.budget} onChange={onChange} required />
          </label>
          <label>
            Cuisine
            <input name="cuisine" value={form.cuisine} onChange={onChange} required />
          </label>
          <label>
            Min Rating
            <input
              name="min_rating"
              type="number"
              min="0"
              max="5"
              step="0.1"
              value={form.min_rating}
              onChange={onChange}
              required
            />
          </label>
          <label>
            Top N
            <input name="top_n" type="number" min="1" max="10" value={form.top_n} onChange={onChange} />
          </label>
          <label className="full-width">
            Optional Preferences (comma separated)
            <input
              name="optional_preferences"
              value={form.optional_preferences}
              onChange={onChange}
              placeholder="quick service, family-friendly"
            />
          </label>
          <button type="submit" disabled={loading} className="pulse-on-hover">
            {loading ? "🔄 Finding matches..." : "🚀 Get Recommendations"}
          </button>
        </form>
        {error ? <p className="status error">{error}</p> : null}
        {feedbackToast ? <p className="status">{feedbackToast}</p> : null}
      </section>

      <section className="panel animate-fadeInUp">
        <div className="results-header">
          <h2>⭐ Recommendations</h2>
          <p className="muted-small">
            {result
              ? `${result.recommendations.length} results | ${result.meta.processing_time_ms} ms`
              : "Submit your preferences to view recommendations."}
          </p>
        </div>

        {fallbackMessage ? <p className="status fallback">{fallbackMessage}</p> : null}
        <div className="results-grid">
          {result?.recommendations?.map((item) => (
            <RecommendationCard
              key={item.restaurant_name}
              item={item}
              userId={form.user_id}
              onFeedback={setFeedbackToast}
            />
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
