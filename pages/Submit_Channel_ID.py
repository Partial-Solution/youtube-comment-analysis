import streamlit as st
import utils as utils
from multiprocessing import Process

@st.cache_data
def does_channel_exist(id):
    # NOTE this will not catch new channels
    return utils.get_channel_exist(id)

def already_in_db(id):
    return utils.query_channel_exist(id)



st.write("# Submit a Channel ID")
st.write("Enter a channel ID to add to the database. It will take a few minutes to populat.")
with st.form(key='my_form'):
    id = st.text_input(label='Enter a channel id')

    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        if already_in_db(id):
            st.warning(f'Channel {id} already exists in database')
        elif does_channel_exist(id):
            p = Process(target=utils.insert_channel_from_user, args=(id,))
            p.daemon = True
            p.start()
            st.success(f'Channel {id} is being added to the database!')
        else:
            st.warning(f'Channel {id} does not exist')
        

