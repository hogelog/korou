import os
import sys

import openai
from make_index import VectorStore, get_size
from IPython import embed

ESA_TEAM = os.getenv("ESA_TEAM")

PROMPT = """
You are virtual character. Read sample output of the character in the following sample section. Then reply to the input.
## Sample
{text}
## Input
{input}
""".strip()


MAX_PROMPT_SIZE = 4096
RETURN_SIZE = 250


def ask_raw(query, vs, prompt=PROMPT):
    PROMPT_SIZE = get_size(prompt)
    rest = MAX_PROMPT_SIZE - RETURN_SIZE - PROMPT_SIZE
    input_size = get_size(query)
    if rest < input_size:
        raise RuntimeError("too large input!")
    rest -= input_size

    samples = vs.get_sorted(query)

    to_use = []
    metadata = {}
    for _sim, number, title, body, updated_at in samples:
        size = get_size(body)
        if rest < size:
            break
        to_use.append(body)
        if number not in metadata:
            metadata[number] = (title, updated_at)
        rest -= size

    text = "\n\n".join(to_use)
    prompt = prompt.format(input=query, text=text)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=RETURN_SIZE,
        temperature=0.0,
    )

    content = response['choices'][0]['message']['content']
    links = []
    for number, (title, updated_at) in metadata.items():
        url = f"https://{ESA_TEAM}.esa.io/posts/{number}"
        links.append((url, title, updated_at))

    return (content, links)

def ask(query, vs, prompt=PROMPT):
    content, links = ask_raw(query, vs, prompt)
    print("\n", content, "\n")

    for url, title, updated_at in links:
        print(f"- [{title} {updated_at.strftime('%Y-%m-%d')}]({url})")


if __name__ == "__main__":
    vs = VectorStore("esa.pickle")
    ask("AIサービスにはどこまでの情報を入れてよいですか", vs)
