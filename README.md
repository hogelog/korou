# korou

korou is a simple script for connecting esa and ChatGPT.

korou is forked from [Scrapbox ChatGPT Connector](https://github.com/nishio/scrapbox_chatgpt_connector).

## How to install

Clone the GitHub repository.

Run the following commands to install the required libraries.

```console
$ pip install -r requirements.txt
```

## How to use
1. Obtain an OpenAI API token and save it in an .env file.

```
 OPENAI_API_KEY=sk-...
```
2. Export esa data and expand it under to data/esa/ directory.

3. Make index.

```console
$ python make_index.py
```

4. Run ask.py or launch chat.py.

```console
$ python ask.py
or
$ python chat.py
```

License
korou is distributed under the MIT License. See the LICENSE file for more information.
