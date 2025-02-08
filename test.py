import openai

client = openai.OpenAI(api_key="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")

models = client.models.list()

for model in models:
    print(model.id)