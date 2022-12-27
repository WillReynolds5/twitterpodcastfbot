
import scrapetube
from pytube import YouTube
import json
import requests
import subprocess
import os


api_key = "AIzaSyBXEXOJe-qP_NS6-OjB4i7J59eNp83swL8"

channel_key = {"lexfridman": "UCJIfeSCssxSC_Dhc5s7woww"}

def get_channel_id(username):
    """
    returns the youtube id of a given channel
    :param username:
    :return:
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={username}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    channel_id = data['items'][0]['id']
    return channel_id


def get_new_videos(channel_id):
    f = open(f'{channel_id}.json')
    channel_vids = json.load(f)
    videos = scrapetube.get_channel(channel_id=channel_key[channel_id])
    for video in videos:
        if video['videoId'] in channel_vids.keys():
            continue
        channel_vids[video['videoId']] = video

    with open(f"{channel_id}.json", "w") as outfile:
        json.dump(channel_vids, outfile)

    return channel_vids

def download_video(id):
    yt = YouTube(f'https://www.youtube.com/watch?v={id}')
    mp4_file = yt.streams.filter(only_audio=True).all()[0]
    # mp4_369p_files = mp4_files.get_by_resolution("360p")
    fn = mp4_file.default_filename
    mp4_file.download(f'audio/')
    os.rename(f'audio/{fn}', f'audio/{fn.replace(" ", "")}')
    fn = fn.replace(" ", "")
    # subprocess.run(f"ffmpeg -i videos/{fn} -vn -acodec copy output.mp3", shell=True, check=True)
    # subprocess.run(f"ffmpeg -i videos/{fn} -vn -acodec copy audio/output-audio.mp3", shell=True, check=True)

    print(yt)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # get_channel_id('UCJIfeSCssxSC_Dhc5s7woww')
    # vids = get_new_videos("lexfridman")
    video_id = "zxqjlWNVGNM"
    download_video(video_id)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
