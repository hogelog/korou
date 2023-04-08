import os

import openai
from make_index import VectorStore, get_size
from IPython import embed


PROMPT = """
You are virtual character. Read sample output of the character in the following sample section. Then reply to the input.
## Sample
{text}
## Input
{input}
""".strip()
ESA_TEAM = os.getenv("ESA_TEAM")


MAX_PROMPT_SIZE = 4096
RETURN_SIZE = 250


def ask(query, vs):
    PROMPT_SIZE = get_size(PROMPT)
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
    prompt = PROMPT.format(input=query, text=text)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=RETURN_SIZE,
        temperature=0.0,
    )

    # show question and answer
    content = response['choices'][0]['message']['content']
    print("\n", content, "\n")

    for number, (title, updated_at) in metadata.items():
        url = f"https://{ESA_TEAM}.esa.io/posts/{number}"
        print(f"- [{title} {updated_at.strftime('%Y-%m-%d')}]({url})")


if __name__ == "__main__":
    vs = VectorStore("esa.pickle")
    ask("AIサービスにはどこまでの情報を入れてよいですか", vs)
