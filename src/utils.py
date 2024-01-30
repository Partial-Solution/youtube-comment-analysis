import os
from googleapiclient.discovery import build
import psycopg2 as sql
from transformers import pipeline
import pandas as pd
import streamlit as st

def build_youtube_client():
    api_key = os.environ.get('API_KEY')

    youtube = build('youtube', 'v3', developerKey=api_key)
    return youtube


def connect_db():
    conn = sql.connect(
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT'),
    )
    return conn

def create_db():
    conn = connect_db()
    create_channel_table(conn)
    create_videos_table(conn)
    create_comments_table(conn)
    create_score_table(conn)
    conn.close()

def delete_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS score")
    c.execute("DROP TABLE IF EXISTS comments")
    c.execute("DROP TABLE IF EXISTS videos")
    c.execute("DROP TABLE IF EXISTS channel")
    conn.commit()
    conn.close()


def create_channel_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS channel
                 (id text PRIMARY KEY, name text)''')
    conn.commit()


def create_videos_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id text PRIMARY KEY, title text, channel_id text, FOREIGN KEY(channel_id) REFERENCES channel(id))''')
                #  (id text PRIMARY KEY, title text, views integer, likes integer, comments integer, channel_id text, FOREIGN KEY(channel_id) REFERENCES channel(id))''')
    conn.commit()


def create_comments_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id text PRIMARY KEY, text text, video_id text, FOREIGN KEY(video_id) REFERENCES videos(id))''')
    conn.commit()


def create_score_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS score
                 (id text, label text, positive real, neutral real, negative real, FOREIGN KEY(id) REFERENCES comments(id))''')
    conn.commit()


def insert_channel(conn, channel_id, channel_name):
    c = conn.cursor()
    c.execute("INSERT INTO channel VALUES (%s, %s)", (channel_id, channel_name))
    conn.commit()


# def insert_video(conn, channel_id, video_id, title, views, likes, comments):
def insert_video(conn, channel_id, video_id, title):
    c = conn.cursor()
    c.execute("INSERT INTO videos VALUES (%s, %s, %s)", (video_id, title, channel_id))
    conn.commit()

def insert_videos(conn, channel_id, video_ids, titles):
    c = conn.cursor()
    query = "INSERT INTO videos VALUES (%s, %s, %s)" + (", (%s, %s, %s)"*(len(video_ids)-1))
    values = zip(video_ids, titles, [channel_id]*len(video_ids))
    flattened_values = [item for sublist in values for item in sublist]
    c.execute(query, flattened_values)
    conn.commit()


def insert_comment(conn, video_id, comment_id, text):
    c = conn.cursor()
    c.execute("INSERT INTO comments VALUES (%s, %s, %s)", (comment_id, text, video_id))
    conn.commit()

def insert_comments(conn, video_ids, comment_ids, texts):
    c = conn.cursor()
    query = "INSERT INTO comments VALUES (%s, %s, %s)" + (", (%s, %s, %s)"*(len(comment_ids)-1))
    values = zip(comment_ids, texts, video_ids)
    flattened_values = [item for sublist in values for item in sublist]
    c.execute(query, flattened_values)
    conn.commit()

def insert_scores(conn, comment_ids, labels, positives, neutrals, negatives):
    c = conn.cursor()
    query = "INSERT INTO score VALUES (%s)" + (", (%s)"*(len(comment_ids)-1))
    c.execute(query, list(zip(comment_ids, labels, positives, neutrals, negatives)))
    conn.commit()

def insert_score(conn, comment_id, label, positive, neutral, negative):
    c = conn.cursor()
    c.execute("INSERT INTO score VALUES (%s, %s, %s, %s, %s)", (comment_id, label, positive, neutral, negative))
    conn.commit()

def query_channel_id(conn, channel_name):
    c = conn.cursor()
    c.execute("SELECT id FROM channel WHERE name=%s", (channel_name,))
    channel_id = c.fetchone()
    conn.close()
    return channel_id

def query_channel_exist(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM channel WHERE id=%s", (id,))
    channel = c.fetchone()
    conn.close()
    return channel

def query_channel_info(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM channel")
    channel_names = c.fetchall()
    return channel_names

def query_videos(channel_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE channel_id=%s", (channel_id,))
    videos = c.fetchall()
    return videos

def query_scores_by_channel(channel_id):
    conn = connect_db()
    c = conn.cursor()
    # c.execute("SELECT * FROM score")
    # c.execute("SELECT * FROM videos")
    c.execute("SELECT * FROM score WHERE id IN (SELECT id FROM comments WHERE video_id IN (SELECT id FROM videos WHERE channel_id=%s))", (channel_id,))
    scores = c.fetchall()
    conn.close()
    return scores

def query_scores_by_video(video_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM score WHERE id IN (SELECT id FROM comments WHERE video_id=%s)", (video_id,))
    scores = c.fetchall()
    return scores

def query_comments():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM comments")
    comments = c.fetchall()
    conn.close()
    return comments

def query_comments_by_video(video_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM comments WHERE video_id=%s", (video_id,))
    comments = c.fetchall()
    conn.close()
    return comments


def query_comments_by_channel_id(channel_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM comments WHERE video_id IN (SELECT id FROM videos WHERE channel_id=%s)", (channel_id,))
    comments = c.fetchall()
    conn.close()
    return comments


def get_videos_info(channel_id, youtube):
    request = youtube.search().list(
        part='id,snippet',
        channelId=channel_id,
        maxResults=50,
        order="viewCount",
    )
    response = request.execute()
    try: 
        # video_ids = [item['id']['videoId'] for item in response['items']]
        video_ids = []
        videos_info = {
            'video_id': [],
            'title': [],
            'publishedAt': [],
            'channel_id': [],
        }
        for item in response['items']:
            if 'videoId' in item['id']:
                videos_info['video_id'].append(item['id']['videoId']),
                videos_info['title'].append(item['snippet']['title']),
                # video_info['publishedAt'].append(item['snippet']['publishedAt']),
                videos_info['channel_id'].append(item['snippet']['channelId']),
            elif 'playlistId' in item['id']:
                print(item)
                print("failed")
                # video_ids.extend(get_playlist_video_ids(item['id']['playlistId'], youtube))
            else:
                raise KeyError
    except KeyError as e:
        print("++++++++++++++++++++++++++++++++++")
        print(channel_id)
        print("++++++++++++++++++++++++++++++++++")
        print(item)
        print("++++++++++++++++++++++++++++++++++")
        print(response)
        print("++++++++++++++++++++++++++++++++++")
        raise e

    return videos_info

def get_comments(video_id):
    youtube = build_youtube_client()
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,
        order="relevance", # now we're basically just asking if youtube relvent comments for channel are toxic
    )
    try: 
        response = request.execute()
    except Exception as e:
        print(video_id)
        print(e)
        return [], []
    comment_text = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
    comment_id = [item['snippet']['topLevelComment']['id'] for item in response['items']]
    return comment_text, comment_id

@st.cache_resource
def get_pipeline():
    distilled_student_sentiment_classifier = pipeline(
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
        return_all_scores=True
    )
    return distilled_student_sentiment_classifier

def get_channel_exist(id):
    response = get_channel(id)
    return response['pageInfo']['totalResults'] > 0

def query_channel_exist(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM channel WHERE id=%s", (id,))
    channel = c.fetchone()
    conn.close()
    return channel != None

def get_channel(id):
    youtube = build_youtube_client()
    request = youtube.channels().list(
        part='snippet',
        id=id,
    )
    response = request.execute()
    return response


def insert_channel_from_user(id):
    response = get_channel(id)
    channel_name = response['items'][0]['snippet']['title']
    conn = connect_db()
    insert_channel(conn, id, channel_name)

    comments = []
    youtube = build_youtube_client()
    videos_info = get_videos_info(id, youtube)
    channel_ids = videos_info['channel_id']
    videos_ids = videos_info['video_id']
    titles = videos_info['title']

    insert_videos(conn, id, videos_ids, titles)

    for video_id in videos_ids:
        # insert_video(
            # conn, 
            # videos_info["channel_id"][idx],
            # videos_info["video_id"][idx], 
            # videos_info["title"][idx], 
        # )
        # video_id = videos_info["video_id"][idx]
        comments_text, comments_id = get_comments(video_id)
        insert_comments(conn, [video_id]*len(comments_text), comments_id, comments_text)
        
    comment_info = query_comments_by_channel_id(id)
    comment_df = pd.DataFrame(comment_info, columns=['id', 'text', 'video_id'])
    comments = comment_df['text'].tolist()
    ids = comment_df['id'].tolist()
    max_length = 512
    comments = [comment[:max_length] for comment in comments]
    # comments = comments[:10]

    distilled_student_sentiment_classifier = get_pipeline()
    # english
    results = distilled_student_sentiment_classifier(comments, batch_size=1)
    # print(results[0])
    assert results[0][0]['label'] == 'positive'
    assert results[0][1]['label'] == 'neutral'
    assert results[0][2]['label'] == 'negative'

    for i in range(len(results)):
        pos_score = results[i][0]['score']
        neu_score = results[i][1]['score']
        neg_score = results[i][2]['score']
        if pos_score > neu_score and pos_score > neg_score:
            label = 'positive'
        elif neu_score > pos_score and neu_score > neg_score:
            label = 'neutral'
        else:
            label = 'negative'
        insert_score(
            conn, 
            ids[i], 
            label,
            pos_score,
            neu_score,
            neg_score,
        )
    conn.close()

def query_all_scores():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM score")
    scores = c.fetchall()
    return scores

def query_all_score_summaries():
    conn = connect_db()
    c = conn.cursor()
    # c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score GROUP BY id")
    c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score")
    scores = c.fetchall()
    return scores

def query_all_score_summaries_by_channel():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score GROUP BY id")
    scores = c.fetchall()
    return scores

def query_all_scores_grouped_by_channel():
    conn = connect_db()
    c = conn.cursor()

    # get_channel_ids 
    c.execute("SELECT id, name FROM channel")
    results = c.fetchall()
    channel_ids = [result[0] for result in results]
    channel_names = [result[1] for result in results]
    scores = {"channel_name": [], "positive": [], "neutral": [], "negative": []}
    for channel_id, channel_name in zip(channel_ids, channel_names):
        c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score WHERE id IN (SELECT id FROM comments WHERE video_id IN (SELECT id FROM videos WHERE channel_id=%s))", (channel_id,))
        results = c.fetchone()
        print(results)
        scores["channel_name"].append(channel_name)
        scores["positive"].append(results[0])
        scores["neutral"].append(results[1])
        scores["negative"].append(results[2])
    conn.close()
    return scores

def query_video_scores(channel_id):
    conn = connect_db()
    c = conn.cursor()

    # TODO could group by channel id maybe and do it one query%s
    # get_channel_ids 
    c.execute("SELECT id, title FROM videos WHERE channel_id=%s", (channel_id,))
    results = c.fetchall()
    video_ids = [result[0] for result in results]
    titles = [result[1] for result in results]
    scores = {"title": [], "positive": [], "neutral": [], "negative": []}
    for video_id, title in zip(video_ids, titles):
        c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score WHERE id IN (SELECT id FROM comments WHERE video_id=%s)", (video_id,))
        results = c.fetchone()
        # print(results)
        scores["title"].append(title)
        scores["positive"].append(results[0])
        scores["neutral"].append(results[1])
        scores["negative"].append(results[2])
    conn.close()
    return scores
    # c = conn.cursor()
    # c.execute("SELECT AVG(positive) as positive, AVG(neutral) as neutral, AVG(negative) as negative FROM score GROUP BY id")
    # scores = c.fetchall()
    # return scores
