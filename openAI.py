# from openai import OpenAI
# from pathlib import Path

# OPENAI_API_KEY = "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"

# # client = OpenAI(api_key="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")

# # audio_file= open("./static/audio_test.mp3", "rb")
# # transcript = client.audio.transcriptions.create(
# #     model="whisper-1", 
# #     file=audio_file,
# #     response_format="text"
# # )

# # print(transcript)

# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[],
#   temperature=0.5,
#   max_tokens=1024
# )

# completion = client.chat.completions.create(
# model="gpt-3.5-turbo",
# messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
# ]
# )

# print(completion.choices[0].message)


# import openai

# # Your API key
# openai.api_key = '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'

# # Define a conversation
# conversation = [
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
# ]

# # Make the API call
# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=conversation,
#     max_tokens=150,
#     temperature=0.7
# )

# # Get the assistant's reply
# assistant_reply = response['choices'][0]['message']['content']
# print(assistant_reply)

# from openai import OpenAI
# client = OpenAI()

# openai.api_key = "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"

# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )

from openai import OpenAI

OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

# audio_file= open("./static/audio_test.mp3", "rb")
# transcript = client.audio.transcriptions.create(
#     model="whisper-1", 
#     file=audio_file,
#     response_format="text"
# )

# return transcript

completion = client.chat.completions.create(
model="gpt-3.5-turbo",
messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
]
)

print(completion.choices[0].message)