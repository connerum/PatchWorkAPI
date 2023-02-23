import openai


openai.api_key = ("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")


def main():
    chatGPT()

def chatGPT():
    quantity = 2
    category = "nosleep"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write me " + str(quantity) + " TikTok captions for a story from the subreddit " + category + ". Make these captions as if they are reacting to the story itself, and do not use first-person speech. Keep the captions original, but do not present any bias.",
        max_tokens=500,
        temperature=0.6
    )
    print(response["choices"][0]["text"])

if __name__ == "__main__":
    main()