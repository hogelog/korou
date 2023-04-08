import time
import glob
import tiktoken
import openai
import pickle
import numpy as np
import yaml
from IPython import embed
from tqdm import tqdm
import dotenv
import os

BLOCK_SIZE = 500
EMBED_MAX_SIZE = 8150

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    "take text, return number of tokens"
    return len(enc.encode(text))


def embed_text(text, sleep_after_success=1):
    "take text, return embedding vector"
    text = text.replace("\n", " ")
    tokens = enc.encode(text)
    if len(tokens) > EMBED_MAX_SIZE:
        text = enc.decode(tokens[:EMBED_MAX_SIZE])

    while True:
        try:
            res = openai.Embedding.create(
                input=[text],
                model="text-embedding-ada-002")
            time.sleep(sleep_after_success)
        except Exception as e:
            # print stacktrace
            print(e)
            time.sleep(1)
            continue
        break

    return res["data"][0]["embedding"]

def update_from_esa(md_files, index):
    """
    md_files: 入力Markdownファイル名 (esa からの)
    index: 出力インデックスファイル名

    # usage
    ## create/update index
    update_from_scrapbox("data/esa/*.md", "esa.pickle")
    """

    vs = VectorStore(index)

    for md_file in tqdm(glob.glob(md_files, recursive=True)):
        try:
            md = open(md_file, encoding="utf8").read()
            metadata = yaml.load(md.split("---")[1], Loader=yaml.FullLoader)
            number = metadata["number"]
            title = metadata["full_name"]
            updated_at = metadata["updated_at"]

            md_body = "".join(md.split("---")[2:])
            buf = [title]
            for line in md_body.split("\n"):
                buf.append(line)
                body = " ".join(buf)
                if get_size(body) > BLOCK_SIZE:
                    vs.add_record(number, title, body, updated_at)
                    buf = buf[len(buf) // 2:]
            body = " ".join(buf).strip()
            if body:
                vs.add_record(number, title, body, updated_at)
        except Exception as e:
            print(e)
            embed()
            exit(1)
        vs.save()

class VectorStore:
    def __init__(self, name, create_if_not_exist=True):
        self.name = name
        if os.path.exists(name):
            self.cache = pickle.load(open(self.name, "rb"))
        else:
            self.cache = {}

    def add_record(self, number, title, body, updated_at):
        if number not in self.cache:
            self.cache[number] = []
        self.cache[number].append((embed_text(body), title, body, updated_at))

    def get_sorted(self, query):
        q = np.array(embed_text(query, sleep_after_success=0))
        buf = []
        for number, texts in self.cache.items():
            for v, title, body, updated_at in texts:
                buf.append((q.dot(v), number, title, body, updated_at))
        buf.sort(reverse=True)
        return buf

    def save(self):
        pickle.dump(self.cache, open(self.name, "wb"))


if __name__ == "__main__":
    update_from_esa("data/esa/**/*.md", "esa.pickle")
