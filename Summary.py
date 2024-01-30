import streamlit as st
import pandas as pd
import utils
import plotly.express as px

st.title("Channel Sentiment Analysis")
st.subheader("Sentiment Analysis of YouTube Channels")
st.markdown("This application is a Streamlit dashboard to analyze the sentiment of YouTube channels")
st.write("Follow the navigation on the left to see different breakdowns or submit a new channel to be added to the database.")

st.sidebar.title("Sentiment Analysis of YouTube Channels")

# @st.cache_resource
# def db_connection():
#     conn = utils.connect_db()
#     return conn
# conn = utils.connect_db()

# @st.cache_data
def load_data(name):
    data = pd.read_sql(utils.get_scores(name))
    return data

# @st.cache_data
def get_channels():
    conn = utils.connect_db()
    result = utils.query_channel_info(conn)
    df = pd.DataFrame(result, columns=['id', 'name'])
    # data = pd.read_sql(utils.get_channel_names(conn))
    conn.close()
    return df
    # return data

# def get_scores_by_channel(id):

def get_all_scores():
    result = utils.query_all_score_summaries()
    df = pd.DataFrame(result, columns=['positive', 'neutral', 'negative'])
    avg_pos = df['positive'][0]
    avg_neu = df['neutral'][0]
    avg_neg = df['negative'][0]
    return df, avg_pos, avg_neu, avg_neg

# @st.cache_data
def get_scores_by_channel(id):
    result = utils.query_scores_by_channel(id)
    df = pd.DataFrame(result, columns=['id', 'label', 'positive', 'neutral', 'negative'])
    avg_pos = df['positive'].mean()
    avg_neu = df['neutral'].mean()
    avg_neg = df['negative'].mean()
    return df, avg_pos, avg_neu, avg_neg

# @st.cache_data
def get_videos(id):
    result = utils.query_videos(id)
    df = pd.DataFrame(result, columns=['id', 'title', 'channel_id'])
    return df

# @st.cache_data
def get_video_summary(id):
    result = utils.query_scores_by_video(id)
    df = pd.DataFrame(result, columns=['id', 'label', 'positive', 'neutral', 'negative'])
    avg_pos = df['positive'].mean()
    avg_neu = df['neutral'].mean()
    avg_neg = df['negative'].mean()
    return df, avg_pos, avg_neu, avg_neg

def get_comments(video_id):
    result = utils.query_comments_by_video(video_id)
    df = pd.DataFrame(result, columns=['id', 'text', 'video_id'])
    return df

def get_all_scores_grouped_by_channel():
    result = utils.query_all_scores_grouped_by_channel()
    df = pd.DataFrame(result, columns=['channel_name', 'positive', 'neutral', 'negative'])
    return df

# conn = db_connection()
# st.write(utils.get_channel_names(conn))
# df = load_data()
channels_df = get_channels()
channels_df["link"] = channels_df["id"].apply(lambda x: f"https://www.youtube.com/channel/{x}")
# with st.expander("Channels List"):
#     st.dataframe(
#         channels_df,
#         column_config={
#             "name": "Channel Name", 
#             # "id": st.column_config.LinkColumn("Channel ID", link="https://www.youtube.com/channel/{id}")
#             "id": None,
#             "link": st.column_config.LinkColumn("Link")
#         },
#         hide_index=True,)

# selected_channel_name =st.selectbox("Select a channel", channels_df['name'].unique())

# channel_id = channels_df[channels_df['name'] == selected_channel_name]['id'].iloc[0]

st.write("# All Scores Currently in Database")
df, avg_pos, avg_neu, avg_neg = get_all_scores()
# st.write(df)
# avg_scores_df = df.groupby('label')['positive', 'neutral', 'negative'].mean().reset_index()
avg_scores_df = pd.DataFrame(
    [
        ["positive", avg_pos],
        ["neutral", avg_neu],
        ["negative", avg_neg]
    ],
    columns=["label", "score"]
)

fig2 = px.pie(
    avg_scores_df,
    values="score",
    names="label",
    title="Average Comment Scores",
    # color_discrete_sequence=["green", "blue", "red"]
    color="label",
    color_discrete_map={"positive": "green", "neutral": "blue", "negative": "red"}

)
st.plotly_chart(fig2)

st.write("## Channel Scores")
channel_scores_df = get_all_scores_grouped_by_channel()
final_df = pd.merge(channels_df, channel_scores_df, left_on='name', right_on='channel_name')
st.dataframe(
    final_df,
    column_config={
        "channel_name": "Channel Name",
        "positive": "Positive Score",
        "neutral": "Neutral Score",
        "negative": "Negative Score",
        "id": None,
        "link": st.column_config.LinkColumn("Link")
    },
    column_order=["channel_name", "positive", "neutral", "negative", "link"],
    hide_index=True
)

