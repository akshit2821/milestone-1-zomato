export const QUICK_MOODS = [
  { label: "Date Night", emoji: "💕", cuisine: "italian", budget: "high", optional_preferences: "cozy ambience" },
  { label: "Family Dinner", emoji: "👨‍👩‍👧‍👦", cuisine: "north indian", budget: "medium", optional_preferences: "family-friendly" },
  { label: "Fast Lunch", emoji: "⚡", cuisine: "fast food", budget: "low", optional_preferences: "quick service" },
  { label: "Explore New", emoji: "🔍", cuisine: "chinese", budget: "medium", optional_preferences: "chef special" },
];

export function applyMood(currentForm, mood) {
  return {
    ...currentForm,
    cuisine: mood.cuisine,
    budget: mood.budget,
    optional_preferences: mood.optional_preferences,
  };
}

export function surpriseMe(currentForm) {
  const pick = QUICK_MOODS[Math.floor(Math.random() * QUICK_MOODS.length)];
  return applyMood(currentForm, pick);
}
