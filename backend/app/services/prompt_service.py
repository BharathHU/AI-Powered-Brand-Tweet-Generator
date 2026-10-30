
def brand_analysis_prompt(request):
    return f"""
You are an expert brand strategist.

Analyze the following brand and return a valid JSON object.

Brand name: {request.brand_name or "Your brand"}
Industry: {request.industry or "General"}
Campaign objective: {request.campaign_objective}
Product description: {request.product_description}
Preferred tone: {request.preferred_tone}
Target audience: {request.target_audience}
Additional instructions: {request.additional_instructions or "None"}

Return exactly these fields:
{{
    "personality": "Short brand personality description",
    "tone": "Brand communication tone",
    "target_audience": "Target audience description",
    "content_themes": [
        "Theme 1",
        "Theme 2",
        "Theme 3",
        "Theme 4",
        "Theme 5"
    ],
    "writing_style": "Description of writing style",
    "voice_summary": [
        "Guideline 1",
        "Guideline 2",
        "Guideline 3"
    ]
}}

Rules:
- content_themes must contain 5 to 8 strings.
- voice_summary must contain 3 to 4 strings.
- Keep descriptions concise and useful.
- Return JSON only.
- Do not include Markdown or explanations.
"""


def tweet_generation_prompt(profile, request):
    return f"""
You are an expert social media content writer.

Generate exactly 10 unique tweets for this brand with a balanced content mix.

BRAND PROFILE:
{profile.model_dump_json()}

CAMPAIGN OBJECTIVE:
{request.campaign_objective}

PRODUCT DESCRIPTION:
{request.product_description}

PREFERRED TONE:
{request.preferred_tone}

TARGET AUDIENCE:
{request.target_audience}

ADDITIONAL INSTRUCTIONS:
{request.additional_instructions or "None"}

Allowed tweet categories:
- Conversational
- Promotional
- Witty / Meme-style
- Informative
- Engagement
- Community-focused

Return exactly this JSON structure:

{{
    "tweets": [
        {{
            "id": 1,
            "category": "Conversational",
            "text": "Tweet content here",
            "character_count": 18
        }}
    ]
}}

STRICT RULES:
1. Generate exactly 10 tweets.
2. Use IDs from 1 to 10.
3. Each tweet must be unique.
4. Each tweet must be no longer than 280 characters.
5. character_count must equal the exact length of text.
6. Use only the allowed categories.
7. Use exactly 2 Conversational tweets, 2 Promotional tweets, 2 Witty / Meme-style tweets, and 2 Informative tweets.
8. Use the remaining 2 tweets for Engagement and/or Community-focused content, choosing the categories that best fit the campaign objective.
9. Maintain the brand voice and vary hooks, ideas, and sentence structure.
10. Avoid unsupported claims.
11. Return valid JSON only.
12. Do not include Markdown or explanations.
"""
