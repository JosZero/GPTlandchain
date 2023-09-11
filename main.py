

import streamlit as st

from tweety import Twitter

import os

from sentiment_analyzer import create_dataframe_from_tweets ,analyze_sentiment, create_tweet_list_for_prompt

  
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
    st.markdown(create_tweet_list_for_prompt(st.session_state.tweets, twitter_handle))
    st.session_state.author_sentiment[twitter_handle] = analyze_sentiment(
        twitter_handle, st.session_state.tweets
    )


twitter_client = Twitter("session")

st.set_page_config(
    layout="wide",
    page_title="CryptoGPT"
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
            create_dataframe_from_tweets(st.session_state.tweets), use_container_width=True
        )
        st.markdown(st.session_state.author_sentiment)

