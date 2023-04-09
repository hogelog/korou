import io
import os
import threading

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from ask import ask_raw
from make_index import VectorStore

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

PROMPT = """
You are virtual character. Read information section. Then reply to the input in Slack mrkdwn format.
## Information
{text}
## Input
{input}
""".strip()

vs = VectorStore("esa.pickle")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

@app.command("/korou")
def command(ack, say, command):
    ack("", response_type="in_channel")
    threading.Thread(target=response, args=(say, command["text"])).start()

def response(say, query):
    content, links = ask_raw(query, vs, PROMPT)
    link_text = "\n".join(f"• <{url}|{title} ({updated_at.strftime('%Y-%m-%d')})>" for url, title, updated_at in links)

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": content,
            },
        },
        {
            "type": "divider",
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": link_text,
                }
            ]
        }
    ]
    say(text=content, blocks=blocks)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
