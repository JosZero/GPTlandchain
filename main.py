

import streamlit as st
from typing import Dict
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

from tweety import Twitter

import os

from sentiment_analyzer import create_dataframe_from_tweets, analyze_sentiment, create_tweet_list_for_prompt


def on_add_author():
    twitter_handle = st.session_state.twitter_handle
    if twitter_handle.startswith("@"):
        twitter_handle = twitter_handle[1:]
    if twitter_handle in st.session_state.twitter_handles:
        return

    all_tweets = twitter_client.get_tweets(twitter_handle)
    if len(all_tweets) == 0:
        return
    st.session_state.twitter_handles[twitter_handle] = all_tweets[0].author.name
    st.session_state.tweets.extend(all_tweets)
    st.write(create_tweet_list_for_prompt(st.session_state.tweets, twitter_handle))
    #st.session_state.author_sentiment[twitter_handle] = analyze_sentiment(twitter_handle, st.session_state.tweets) 

    st.session_state.author_sentiment[twitter_handle] = {
"2023-06-06": "35",
"2023-06-09": "20",
"2023-06-10": "10",
"2023-06-11": "5",
"2023-06-12": "15",
"2023-06-13": "25",
"2023-06-15": "50",
"2023-06-16": "10",
"2023-06-17": "10",
"2023-06-18": "20",
"2023-06-20": "5",
"2023-06-21": "20",
"2023-07-02": "35",
"2023-07-03": "15",
"2023-07-05": "10",
"2023-07-07": "30",
"2023-07-08": "15",
"2023-07-13": "5",
"2023-07-15": "10",
"2023-07-17": "15",
"2023-07-19": "10",
"2023-07-22": "5",
"2023-07-24": "20",
"2023-07-25": "15",
"2023-07-26": "15",
"2023-07-27": "10",
"2023-07-28": "10",
"2023-07-29": "15",
"2023-07-31": "20",
"2023-08-06": "20",
"2023-08-09": "5",
"2023-08-11": "10",
"2023-08-15": "10",
"2023-08-21": "15",
"2023-08-22": "10",
"2023-08-26": "5",
"2023-08-28": "5",
"2023-08-29": "10",
"2023-08-31": "15"}


def create_sentiment_dataframe(sentiment_data: Dict[str, int]) -> pd.DataFrame:
    date_list = pd.date_range(
        datetime.now().date() - timedelta(days=200), periods=200, freq="D"
        #datetime.now().date() - timedelta(days=6), periods=7, freq="D"
    )
    dates = [str(date) for date in date_list.date]
    chart_data = {"date": dates}

    for author, sentiment_data in sentiment_data.items():
        author_sentiment = []
        for date in dates:
            if date in sentiment_data:
                author_sentiment.append(sentiment_data[date])
            else:
                author_sentiment.append(None)
        chart_data[author] = author_sentiment

    sentiment_df = pd.DataFrame(chart_data)
    sentiment_df.set_index("date", inplace=True)

    if not sentiment_df.empty:
        sentiment_df["Overall"] = sentiment_df.mean(skipna=True, axis=1)
    return sentiment_df



twitter_client = Twitter("session")

st.set_page_config(
    layout="wide",
    page_title="CryptoGPT",
    page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4c8.png",

)
st.markdown(
    "<h1 style='text-align: center'>CryptoGPT: Crypto Twitter Sentiment Analysis</h1>",
    unsafe_allow_html=True,
)

st.title("CryptoGPT")

if not "tweets" in st.session_state:
    st.session_state.tweets = []
    st.session_state.api_key = ""
    st.session_state.twitter_handles = {}
    st.session_state.author_sentiment = {}

os.environ["OPENAI_API_KEY"] = st.session_state.api_key


print(st.session_state.api_key)

col1, col2 = st.columns(2)

with col1:
    st.text_input("OpenAI API key",
                  type="password",
                  key="api_key",
                  placeholder="sk-...4224",
                  help="Get your API key: https://platform.openai.com/account/api-keys")

    with st.form(key="twitter_handle_form", clear_on_submit=True):
        st.subheader("Add Twitter Account")
        st.text_input("Twitter Handler", key="twitter_handle", placeholder="@saylor")
        submit = st.form_submit_button(label="Add Tweets", on_click=on_add_author)

    if st.session_state.twitter_handles:
        st.subheader("Twitter Accounts", anchor=False)
        for handle, name in st.session_state.twitter_handles.items():
            handle = "@"+handle
            st.markdown(f"{name} ([{handle}](https://twitter.com/{handle}))")

    st.subheader("Tweets", anchor=False)
    st.dataframe(
        create_dataframe_from_tweets(st.session_state.tweets)
    )
    st.markdown(st.session_state.author_sentiment)

with col2:
    sentiment_df = create_sentiment_dataframe(st.session_state.author_sentiment)
    if not sentiment_df.empty:
        fig = px.line(
            sentiment_df,
            x=sentiment_df.index,
            y=sentiment_df.columns,
            labels={"date": "Date", "value": "Sentiment Analitics"},
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        st.dataframe(sentiment_df, use_container_width=True)


