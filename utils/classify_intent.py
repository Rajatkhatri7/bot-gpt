


async def classify_intent(llm, message: str) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "You are an intent classifier. "
                "Return ONLY one of these labels:\n"
                "OPEN_CHAT\nDOCUMENT_QA\nDOCUMENT_SUMMARY"
            )
        },
        {
            "role": "user",
            "content": message
        }
    ]

    response = await llm.generate(
        messages=prompt,
        temperature=0.1,
        max_tokens=20
    )

    return response.strip()