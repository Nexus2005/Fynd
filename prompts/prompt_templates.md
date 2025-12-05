# LLM Prompt Templates

## Task 1: Rating Prediction Prompts

### 1. Zero-Shot Prompt
```
You are a Yelp review rating predictor. Given a review text, predict the star rating (1-5).

Review: {review_text}

Return your response in JSON format:
{
  "predicted_stars": <integer 1-5>,
  "explanation": "<brief explanation of your reasoning>"
}
```

### 2. Few-Shot Prompt
```
You are a Yelp review rating predictor. Given a review text, predict the star rating (1-5).

Examples:
Review: "Amazing food and service! Best restaurant in town!"
Response: {"predicted_stars": 5, "explanation": "Extremely positive language with superlatives"}

Review: "Food was okay, nothing special but not bad either."
Response: {"predicted_stars": 3, "explanation": "Neutral sentiment, average experience"}

Review: "Terrible service, cold food, will never come back!"
Response: {"predicted_stars": 1, "explanation": "Strongly negative with multiple complaints"}

Now predict for this review:
Review: {review_text}

Return your response in JSON format:
{
  "predicted_stars": <integer 1-5>,
  "explanation": "<brief explanation of your reasoning>"
}
```

### 3. Chain-of-Thought Prompt
```
You are a Yelp review rating predictor. Analyze the review step by step to predict the star rating (1-5).

Review: {review_text}

Analyze using these criteria:
1. Sentiment Analysis: Identify positive/negative language
2. Content Quality: Mention of food, service, atmosphere
3. Specific Details: Concrete examples vs general statements
4. Overall Tone: Enthusiastic, neutral, or disappointed
5. Recommendation Language: Would return, recommend, or avoid

Think through your analysis, then provide your final prediction.

Return your response in JSON format:
{
  "predicted_stars": <integer 1-5>,
  "explanation": "<detailed reasoning based on the criteria above>"
}
```

## Task 2: Dashboard Prompts

### User Response Prompt
```
You are a helpful AI assistant for Yelp reviews. 
A user has left a {rating}-star review with the following text:

"{review_text}"

Generate a friendly, professional response that:
1. Acknowledges their feedback
2. Shows appreciation for their review
3. Addresses any concerns if rating is low
4. Encourages future visits if appropriate

Keep the response concise (2-3 sentences) and personalized to their review.
```

### Summary Prompt
```
Analyze this Yelp review and provide a concise summary:

Rating: {rating} stars
Review: "{review_text}"

Provide a 1-2 sentence summary that captures the main points and sentiment.
Focus on what the user liked/disliked and their overall experience.
```

### Recommendation Prompt
```
Based on this Yelp review, what specific action should the business take?

Rating: {rating} stars
Review: "{review_text}"

Provide a specific, actionable recommendation for the business.
Examples: "Improve service speed", "Add more vegetarian options", "Train staff on customer service", etc.

Keep it to one clear, actionable item.
```

## Design Principles

1. **JSON Structure**: All Task 1 prompts must return valid JSON with `predicted_stars` and `explanation` fields
2. **Clarity**: Prompts should be clear and unambiguous
3. **Consistency**: Use consistent formatting and structure
4. **Context**: Provide sufficient context for the model to understand the task
5. **Examples**: Use concrete examples in few-shot prompting
6. **Reasoning**: Chain-of-thought prompts should guide systematic analysis

## Usage Notes

- Replace `{review_text}` and `{rating}` with actual values
- Ensure JSON responses are properly formatted
- Handle API failures gracefully with fallbacks
- Monitor response quality and adjust prompts as needed