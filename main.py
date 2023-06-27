#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" imports """
from youtube_to_txt import get_transcript_from_ytchannel
from clean_data import clean_data

""" env """
import os
from dotenv import load_dotenv
load_dotenv()

""" fetching transcripts from the youtube channel """
API_KEY = os.getenv('Y2_API_KEY')
CHANNEL_ID = "UCdEF3_EFTu78zA7u8JMTk3A"
try:
    get_transcript_from_ytchannel(
        api_key=API_KEY,
        channel_id=CHANNEL_ID,
        no_of_videos=1, 
        output_file='data.txt'
    )
except KeyboardInterrupt:
    print("[PROGRAM STOPPED]")
    exit()

""" clean the data fetched """
try:
    clean_data(
        input_file='data.txt',
        output_file='clean_data.txt'
    )
except KeyboardInterrupt:
    print("[PROGRAM STOPPED]")
    exit()





