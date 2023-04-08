import readline

from ask import ask
from make_index import VectorStore

vs = VectorStore("esa.pickle")

while True:
    try:
        input_str = input(">> ")
    except EOFError:
        break
    except Exception as e:
        print(e)
        continue
    if not input_str:
        continue
    ask(input_str, vs)
