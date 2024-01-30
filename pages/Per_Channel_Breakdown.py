import streamlit as st
import pandas as pd
import utils
import plotly.express as px

st.title("Channel Sentiment Analysis")
st.subheader("Sentiment Analysis of YouTube Channels")
st.markdown("This application is a Streamlit dashboard to analyze the sentiment of YouTube channels")
st.markdown("The data is collected from the YouTube API and analyzed using the TextBlob library")

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

def get_comments_by_channel(channel_id):
    result = utils.query_comments_by_channel(channel_id)
    df = pd.DataFrame(result, columns=['id', 'text', 'video_id'])
    return df


# conn = db_connection()
# st.write(utils.get_channel_names(conn))
# df = load_data()
channels_df = get_channels()
channels_df["link"] = channels_df["id"].apply(lambda x: f"https://www.youtube.com/channel/{x}")
channels_df = channels_df.sort_values(by=['name'])
# st.dataframe(
#     channels_df,
#     column_config={
#         "name": "Channel Name", 
#         # "id": st.column_config.LinkColumn("Channel ID", link="https://www.youtube.com/channel/{id}")
#         "id": None,
#         "link": st.column_config.LinkColumn("Link")
#     },
#     hide_index=True,)

selected_channel_name =st.selectbox("Select a channel", channels_df['name'].unique())

channel_id = channels_df[channels_df['name'] == selected_channel_name]['id'].iloc[0]


st.write("## Channel Scores")
scores_df, avg_pos, avg_neu, avg_neg = get_scores_by_channel(channel_id)

# st.write(scores_df)
# st.write(f"Average Positive Score: {avg_pos}")
# st.write(f"Average Neutral Score: {avg_neu}")
# st.write(f"Average Negative Score: {avg_neg}")

avg_scores_df = pd.DataFrame({
    "label": ["positive", "neutral", "negative"],
    "score": [avg_pos, avg_neu, avg_neg]
})
fig2 = px.pie(
    avg_scores_df,
    values="score",
    names="label",
    title="Average Channel Scores",
    # color_discrete_sequence=["green", "blue", "red"]
    color="label",
    color_discrete_map={"positive": "green", "negative": "red", "neutral": "blue"}

)
st.plotly_chart(fig2)

st.write("Breakdown by Label")
fig = px.bar(
    scores_df,
    x="label",
    y=["positive", "neutral", "negative"],
    title="Channel Scores by Label",
    labels={
        "value": "Score",
        "variable": "Sentiment",
        "label": "Highest Sentiment"
    },
    barmode="group",
    height=400,
    width=600,
    # color="label",
    color_discrete_map={"positive": "green", "negative": "red", "neutral": "blue"}
)
fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
st.plotly_chart(fig)




# st.write("## Videos Summary")
vidoes_df = get_videos(channel_id)
vidoes_df["link"] = vidoes_df["id"].apply(lambda x: f"https://www.youtube.com/watch?v={x}")
vidoes_df = vidoes_df.sort_values(by=['title'])
# st.dataframe(
#     vidoes_df,
#     column_config={
#         "title": "Video Title",
#         "Link": st.column_config.LinkColumn("Link")
#     },
#     hide_index=True,
#     column_order=["title", "link"]
# )



st.write("## Video Scores")
df = pd.DataFrame(utils.query_video_scores(channel_id))
st.dataframe(
    df,
    column_config={
        "title": "Title",
        "positive": "Positive",
        "neutral": "Neutral",
        "negative": "Negative",
        "id": None,
        "link": st.column_config.LinkColumn("Link"),
    },
    column_order=["title", "positive", "neutral", "negative", "link"],
    hide_index=True
)

# selected_video = st.selectbox("Select a video", vidoes_df['title'].unique())
# selected_video_id = vidoes_df[vidoes_df['title'] == selected_video]['id'].iloc[0]
# st.write("Link to video: ", f"https://www.youtube.com/watch?v={selected_video_id}")
# video_summary, avg_pos, avg_neu, avg_neg = get_video_summary(selected_video_id)


# st.dataframe(
#     video_summary,
#     hide_index=True,
#     column_config={
#         "id": None
#     }
# )
# st.write(f"Average Positive Score: {avg_pos}")
# st.write(f"Average Neutral Score: {avg_neu}")
# st.write(f"Average Negative Score: {avg_neg}")



# scores = 

# st.write(df.groupby('name')['positive'].mean().sort_values(ascending=False))
# st.write(df.groupby('name')['positive'].mean().sort_values(ascending=False).index.tolist())

# channels = sorted(df['name'].unique())
# sort_str = st.sidebar.selectbox("Select a sort", ['Alphabetical', 'Positive', 'Neutral', 'Negative'])
# if sort_str == 'Alphabetical':
#     channels = sorted(channels)
# elif sort_str == 'Positive':
#     channels = df.groupby('name')['positive'].mean().sort_values(ascending=False)
#     channels = zip(channels.index.tolist(), channels.tolist())
#     channels = [f"{channel[1]:.2f}: {channel[0]}" for channel in channels]
# elif sort_str == 'Neutral':
#     channels = df.groupby('name')['neutral'].mean().sort_values(ascending=False)
#     channels = zip(channels.index.tolist(), channels.tolist())
#     channels = [f"{channel[1]:.2f}: {channel[0]}" for channel in channels]
# elif sort_str == 'Negative':
#     channels = df.groupby('name')['negative'].mean().sort_values(ascending=False)
#     channels = zip(channels.index.tolist(), channels.tolist())
#     channels = [f"{channel[1]:.2f}: {channel[0]}" for channel in channels]


# channel = st.sidebar.selectbox("Select a channel", channels)
# if sort_str == 'Alphabetical':
#     channel = channel
# elif sort_str == 'Positive':
#     channel = channel.split(': ')[1]
# elif sort_str == 'Neutral':
#     channel = channel.split(': ')[1]
# elif sort_str == 'Negative':
#     channel = channel.split(': ')[1]


# channel_df = df[df['name'] == channel]
# # st.write(channel_df)
# st.dataframe(
#     channel_df,
#     column_config={
#     })
# st.write(f"positive {channel_df['positive'].mean()}")
# st.write(channel_df['neutral'].mean())
# st.write(channel_df['negative'].mean())
# st.write(channel_df['positive'].mean() + channel_df['neutral'].mean() + channel_df['negative'].mean())
# st.write(channel_df['positive'].mean() - channel_df['negative'].mean())
# st.write(channel_df['positive'].mean() - channel_df['neutral'].mean())
# st.write(channel_df['neutral'].mean() - channel_df['negative'].mean())


# st.write("Most positive comments")
# channel_df = channel_df.sort_values(by=['positive'], ascending=False)
# st.dataframe(
#     channel_df.head(10),
#     column_config={
#     },
#     hide_index=True)

# st.write("Most negative comments")
# channel_df = channel_df.sort_values(by=['negative'], ascending=False)


# st.dataframe(
#     channel_df[["negative", "text"]].head(),
#     column_config={
#         "negative": "Negative Score",
#     },
#     hide_index=True)