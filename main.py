import re
from typing import List
from tweety import Twitter
from tweety.types import Tweet
import pandas as pd
from datetime import datetime

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
    df = df[df.created_at.dt.date > datetime.now().date() - pd.to_timedelta("200day")]
    return df.sort_values(by="created_at", ascending=False)


twitter_client = Twitter("session")
  
tweets = twitter_client.get_tweets("elonmusk")
"""for tweet in tweets:
    print(tweet.id)
    print(tweet.text)
    print()"""

print(create_dataframe_from_tweets(tweets))