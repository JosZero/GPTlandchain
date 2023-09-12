import re
from datetime import datetime
from typing import List, Dict
import pandas as pd
from tweety.types import Tweet
import json

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = """
Eres un analista de noticias con experiencia en la evaluación del sentimiento de noticias de diferentes fuentes. Siempre sigues las tendencias en noticias y comprendes profundamente los acontecimientos actuales.

Se te proporcionan titulares de noticias y sus resúmenes para fechas específicas:

{news}

Indica cuán positivas o negativas son las noticias para cada fecha. Utiliza números en una escala de 0 a 100, donde 0 indica una perspectiva extremadamente negativa y 100 indica una perspectiva extremadamente positiva.
Utiliza un JSON con el siguiente formato:

"date": "sentiment"

Cada entrada del JSON debe reflejar el sentimiento agregado para esa fecha. Proporciona solo el JSON, sin explicaciones adicionales.
"""


PROMPT_TEMPLATE2 = """
You're a cryptocurrency trader with 10+ years of experience. You always follow the trend
and follow and deeply understand crypto experts on Twitter. You always consider the historical predictions for each expert on Twitter.

You're given tweets and their view count from @{twitter_handle} for specific dates:

{tweets}

Tell how bullish or bearish the tweets for each date are. Use numbers between 0 and 100, where 0 is extremely bearish and 100 is extremely bullish.
Use a JSON using the format:

date: sentiment

Each record of the JSON should give the aggregate sentiment for that date. Return just the JSON. Do not explain.
"""

def clean_tweet(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www.\S+", "", text)
    return re.sub(r"\s+", " ", text)


def create_dataframe_from_tweets(tweets: List[Tweet]) -> pd.DataFrame:
    rows = []
    for tweet in tweets:
        clean_text = clean_tweet(tweet.text)
        if len(clean_text) == 0:
            continue
        rows.append(
            {
                "id": tweet.id,
                "text": clean_text,
                "author": tweet.author.username,
                "date": str(tweet.date.date()),
                "created_at": tweet.date,
                "views": tweet.views,
            }
        )
    
    df = pd.DataFrame(
        rows, columns=["id", "text", "author", "date", "views", "created_at"]
    )
    df.set_index("id", inplace=True)
    if df.empty:
        return df
    df = df[df.created_at.dt.date > datetime.now().date() - pd.to_timedelta("100day")]
    return df.sort_values(by="created_at", ascending=False)


def create_tweet_list_for_prompt(tweets: List[Tweet], twitter_handle: str) -> str:
    df = create_dataframe_from_tweets(tweets)
    user_tweets = df[df.author == twitter_handle]
    if user_tweets.empty:
        return ""
    if len(user_tweets) > 200:
        user_tweets = user_tweets.sample(n=200)

    text = ""

    for tweets_date, tweets in user_tweets.groupby("date"):
        text += f"{tweets_date}:"
        for tweet in tweets.itertuples():
            text += f"\n{tweet.views} - {tweet.text}"
            
    return text


def analyze_sentiment(twitter_handle: str, tweets: List[Tweet]) -> Dict[str, int]:
    chat_gpt = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    prompt = PromptTemplate(
        input_variables=["twitter_handle", "tweets"], template=PROMPT_TEMPLATE
    )

    sentiment_chain = LLMChain(llm=chat_gpt, prompt=prompt)
    response = sentiment_chain(
        {
            "twitter_handle": twitter_handle,
            "tweets": create_tweet_list_for_prompt(tweets, twitter_handle),
        }
    )
    return json.loads(response["text"])











#APIKEY
#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