from openai import OpenAI

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text)