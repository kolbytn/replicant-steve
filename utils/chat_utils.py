from typing import List
import os
import time
import openai
from openai.error import ServiceUnavailableError, RateLimitError, APIError, InvalidRequestError

if "OPENAI_ORG_ID" in os.environ: 
    openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


def send_chat(turns: List[str], max_len: int = 128, max_tries: int = 20, system_message: str = "") -> str:

    num_tries = 0
    while True:
        try:
            messages = [dict(role="system", content=system_message)] if system_message else []
            for i, content in enumerate(turns):
                messages.append(dict(role="user" if i % 2 == 0 else "assistant", content=content))
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=.7,
                max_tokens=max_len,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content
        except ServiceUnavailableError as e:
            print("ServiceUnavailableError:", e)
            time.sleep(2)
        except RateLimitError as e:
            print("RateLimitError:", e)
            time.sleep(60)
        except APIError as e:
            print("APIError:", e)
            time.sleep(2)
        except InvalidRequestError as e:
            print("InvalidRequestError:", e)
            if len(turns) > 2:
                turns = turns[2:]
        num_tries += 1
        if num_tries >= max_tries:
            raise Exception()
