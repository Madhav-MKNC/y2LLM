# youtube videos to text

import googleapiclient.discovery
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi


def get_channel_videos(channel_id, api_key):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)

    video_ids = []
    page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Fetch 50 videos at a time
            pageToken=page_token  # Add pagination
        )
        response = request.execute()

        video_ids += [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']
        
        # Check if there are more videos to fetch
        if 'nextPageToken' in response:
            page_token = response['nextPageToken']
        else:
            break

    return video_ids

def get_transcripts(video_ids):
    transcripts = []
    for video_id in tqdm(video_ids):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts.append(transcript)
        except Exception as ex:
            print(f"An error occurred for video: {video_id} [{ex}]")
    return transcripts

def write_to_file(transcripts, output_file):
    with open(output_file, 'w') as f:
        for transcript in transcripts:
            for item in transcript:
                f.write(item['text'] + '\n')

def get_transcript_from_ytchannel(api_key, channel_id, no_of_videos, output_file):
    video_ids = get_channel_videos(channel_id, api_key)[:no_of_videos]
    transcripts = get_transcripts(video_ids)
    write_to_file(transcripts, output_file)



if __name__ == "__main__":
        
    import os
    from dotenv import load_dotenv
    load_dotenv()

    API_KEY = os.getenv('Y2_API_KEY')
    CHANNEL_ID = "UCdEF3_EFTu78zA7u8JMTk3A" # Get your channel ID here https://www.youtube.com/channel/[CHANNEL_ID]

    try:
        get_transcript_from_ytchannel(
            api_key=API_KEY,
            channel_id=CHANNEL_ID,
            no_of_videos=1,
            output_file="youtube.txt"
        )
    except KeyboardInterrupt:
        print("[PROGRAM STOPPED]")
