import readline

from ask import ask


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
    ask(input_str, "tiny_sample.pickle")
