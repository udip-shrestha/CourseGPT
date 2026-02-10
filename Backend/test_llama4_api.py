from huggingface_hub import InferenceClient

model_id = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
client = InferenceClient(model=model_id, token=True)

prompt = "Explain the A* search algorithm in simple words."

response = client.chat.completions.create(
    model=model_id,
    messages=[
        {"role": "system", "content": "You are an expert AI tutor who explains concepts clearly."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=250,
    temperature=0.7
)

print("\n--- Model Response ---\n")
print(response.choices[0].message["content"])
