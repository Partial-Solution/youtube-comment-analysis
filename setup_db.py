import utils
import pandas as pd


if __name__ == "__main__":
    utils.delete_db()
    utils.create_db()
    # df = pd.read_csv("data/channels.csv")

    # youtube = utils.build_youtube_client()
    # names = df['name'].tolist()
    # ids = df['id'].tolist()

    # for name, id in zip(names, ids):
    #     utils.insert_channel_from_user(id)



# del video_ids
# video_ids = pd.read_sql

# for video_id in video_ids:
#     utils.insert_video(conn, id, video_id)
#     print(video_id)
#     comments = get_comments(video_id, youtube)
#     for comment in comments:
#         utils.insert_comment(conn, comment)
#         print(comment)
    # channel_id = get_channel_id(youtube, name)
    # print(channel_id)
    # insert_channel(connect_db(), channel_id, name)
    # print(name, channel_id)
    # print()
