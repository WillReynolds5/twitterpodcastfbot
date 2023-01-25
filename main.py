import scrapetube
from pytube import YouTube
import json
import requests
import subprocess
import os
import whisper
import openai
import nltk
import re
import time
import math
import subprocess
from twilio_util import send_message, listen, clear_messages
from tweet import tweet

nltk.download('punkt')

api_key = "AIzaSyBXEXOJe-qP_NS6-OjB4i7J59eNp83swL8"
channel_key = {"lexfridman": "UCJIfeSCssxSC_Dhc5s7woww"}
openai.api_key = "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"


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

def download_video(yt):
    mp4_file = yt.streams.filter(only_audio=True)[0]
    fn = mp4_file.default_filename

    if not os.path.exists(f'audio/{fn.replace(" ", "").replace("&", "")}'):
        mp4_file.download(f'audio/')
        os.rename(f'audio/{fn}', f'audio/{fn.replace(" ", "").replace("&", "")}')
        print("Downloading")

    fn = fn.replace(" ", "").replace("&", "")
    return f"audio/{fn}", mp4_file.title, yt.description

def transcribe_audio(local_path):

    model = whisper.load_model("base")
    result = model.transcribe(local_path)
    return result

def chatgpt(prompt):
    from revChatGPT.ChatGPT import Chatbot
    chatbot = Chatbot({"session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..rx_gKXoTOyqS-525.x0qrqKzUDWyY7aNecbA7hHEnwMwIu83CDEkW4XNzE70twJ8-6Z7ob2QXrBYVORbrhEcACCpmH1zM-3Kr5w8J-pNpm0OgQx1mjrpKnKJCeiwb_1bKYVqvVUFCK3l4a93UGhiyNgIAebPJ_8hVdh9B4rJqFSkvq9EfjgjSO7k2FQBbvsUjZ6_2OI-p4GjVJtBnYVDpa25sR0ElgcXNil3Mmom89SXDNcxb7EvFrjkPWn5rgCnn2QaPW4_-D_JbLHoOlBVW_D-v-AVpJ4nIy2a3_QpMz_otIfIe8i-BAOoiLZLgZpQF81VGtirYy1wzlV5QgusULKzK53M58YZaV5UU5_NoXq59R7BC8-tMiAtS4DAkZRJmiKN3oz-PGOFdd2MyGny05KsBx-ZsiUx8zscJK4angOJcD9MYz4-QYVYetPJwVTi065peqK_50_E-xJ3Ox33przPgCElsxiZZWHGEW786xNwgD-Amo0PVuPZc459PkSEuzye6Z8AIa1EaTRPA3zirIEo1tPN_CfD1Udk3EtKOrdJgu2ZvlPw0Q8ydXW4uOIwx4J0u-QxJ_WfqudmlKwv7usE-Rlrqen_TailTjI3BDI4qLQPoLAAf791P8sxqLRbmqFgbwCaJqNiAmHz-Yd2AAEGhJXT7BKXwLPLtr_vjcP5fqWq6GKmA41uw3aQiIFglYHIRljdb5Hx2A1ULcYpvBcdikHORVQxHnTmu9by47NFzJaeP09MEU-OhhpWJAylcd4x-uhX2-_1Ub4W3NHIcnT6wUJGjrlgkmq1877iA18mS6-2Q4kRyRV4ScqGg6LpY30hMyFqpxF1KzAonnznbNhaNVwlvWDDA-wZhJQf_-EXwPwm49vRsb7mDW0AZwRzz76oF05r74ZfouzP_fSxABMFbqQsd1NvPuvcZc5ULL6dRtFzy8gYUCBBa-MH72tigui1HSN9dLC1Ej7FavyM6k4DVTFiPtgQGc5iypQt0tSZEKxqIt6r9TcWh_SK1Or24nwDtfmVNNsluOVa41DE6Q3ixs0cCFcJlcimXsPBs0erVUYYuUUq4BTTaDSrZaWzuRbYpMkHTIZUrcrQBLNMP_3waEozDEd5ttQoSK1H-uKQO7Qtu1QuXBhwvAvrczyMu30bfFkXxd4vbrIFsjmWL6boj5iWfEWwaru9kFPCyn8uWeVVKYMkJfCJoYFEAq0y63A5e8WqauNDTC5OSBiev8XZ7xQeEPVYphi4y8HhAJeCCXVEqtCI-1PnByUwTefKFSbUoH8xVjITzuhaNdZ5EmnOx678xW8T4a6t32-dGT1A_BfF5jb0smVlRI7tYtl4w5lGaCwFTExmc1G_hlQv7pbuKU0VvhmWnaXlF8WL6Vn_jKGkOm5N3xr--PqCe8ENbkmN98s1iw9O2a-Sp3xB4C7KeUirfG1lqKBWTrz8EbyKnXtQEjUut0rsRgl61flC8l4Q6-I5yrOChZaKgZkt_1B4WNHENEAG3R8j_Q9LKaBi2ViS28AzkpkqWr3XCunPbUUyI0qk4MXcIf1RQuYrs_r9J304d9GY-CqVcaXUOccEkQ-8bCUaGKPKmLk3nJX-xlLTL8rqEGbAmG0BZh6_bxE-oZIyzzIdUoe0AguNFKviIvFLGr3txxMwAbzK5yENSW6l-WJ_KHvqGjU6x0d90YPBQzv-X6UFGLgdJyVZWaqZFt55gXVy1628WRiIiyo3CXI1fKjsVzPtIs3nf1j3XUtHe607H7W34MShMD75ojRdwhYK8k7afcMQt2idY0Ro_peuCId0ElbP0uaiUZKCFp2VDp14LiJXodwWT1Af2cYYnnfxvg4m4joyIbIbL8AYb9zPMNMmwRU9sRD_5vkn2u74o1QQia5sAe-TVqqPit0dN7FYcqu6sqKy17dAw7sd5h4yiKxU0PF2HwTl5kJ06GHu7PPxMadSNxx5iFE2-5zXSnvUScBBWmUhtVdSek_SAdt9lp3LrwcojTo-ihZeKcW29I-77t1D-OHs7h92Bu4OC8zcNScFAYKsI1te9bdXD0wyCOLQfFEd-EqihIUMSKUAgteWbn3r7gc9O7Tc0-xkoAVALSdr1vFWsC8-508NU8R0ezdFTUQvBM5J9B1E6e5TEPqB_QU_RzRW5acI_VQueRt0GeM6BNJhVWW8VSkV1ljy--Cg_8WPG9hWBuOOIUCIJfiIySZ6Ng6z7pJgywj9q0f-92lJ2QbrmKu2z0fdVQuaS-ZXT_wMvcA9fqPfxWnY2ZOfgtvxKIRwlWDNysiHBF0g3ibKqCS7H4sHENUPJEtMDlYTB4rjI9XMMwlVeP5JVbtSDvutYYiX0Y3-vPZdZ6_rmGE-xHLZghO8ZkZk1cIvF_LhQSBGcs0WZlOOiRUmhnnJEGKcNMPeH_Wo20yvoiz1HdgY.53cVLPZysIXJpaAn2Fi5bA"},
                      conversation_id=None, parent_id=None)  # You can start a custom conversation
    response = chatbot.ask(prompt, conversation_id=None, parent_id=None) # You can specify custom conversation and parent ids. Otherwise it uses the saved conversation (yes. conversations are automatically saved)
    return response

def gpt3(prompt):
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

def extract_section_data(desc):

    timestamps = re.findall(r'\d\d:\d\d:\d\d|\d:\d\d:\d\d|\d\d:\d\d|\d:\d\d', desc)
    lines = desc.split('\n')

    # Initialize a dictionary to store the timestamps and names
    data = []

    # Iterate through the lines
    for line in lines:
        # Check if the line starts with a timestamp
        if line.startswith(tuple(timestamps)) or line.replace("[", "").startswith(tuple(timestamps)):
            # Extract the timestamp and name
            timestamp, name = line.split(' ', 1)
            name = name.replace('-', '').strip()
            # Add the timestamp and name to the dictionary
            data.append([timestamp, name])
        elif line.replace("]", "").endswith(tuple(timestamps)):
            # Extract the timestamp and name
            timestamp, name = line.split(' ', -1)
            name = name.replace('-', '').strip()
            # Add the timestamp and name to the dictionary
            data.append([timestamp, name])

    return data


def timestamp_to_seconds(ts):
    ts_lst = ts.split(":")
    if len(ts_lst) == 2:
        seconds = int(ts_lst[0]*60) + int(ts_lst[1])
    elif len(ts_lst) == 3:
        seconds = int(ts_lst[0])*3600 + int(ts_lst[1])*60 + int(ts_lst[2])
    else:
        raise ValueError("Invalid timestamp")

    return seconds

def split_sections(local_path, timestamps):

    try:
        for i in range(len(timestamps)-1):
            print(i)
            start_time = timestamps[i][0]
            start_time_duration = timestamp_to_seconds(start_time)
            clip_name = timestamps[i][1]
            duration = calculate_duration(start_time_duration, timestamp_to_seconds(timestamps[i + 1][0]))
            fn = f'{str(i).zfill(4)}_{clip_name.replace(",", "").replace("(", "").replace("/", "").replace(";", "").replace(")", "").replace("&", "").replace(" ", "_")}'
            subprocess.Popen(f'ffmpeg -ss {start_time_duration} -t {duration} -i {local_path} clips/{fn}.mp4', shell=True, stdout=subprocess.PIPE)
    except Exception as e:
        print(e)

def calculate_duration(start, end):
    return (end - start)


def create_batches(text):

    num_batches = math.ceil(len(text['text'])/16000)
    batch_size = len(text['text']) // num_batches

    sentences = nltk.tokenize.sent_tokenize(text['text'].replace("\n", ""))
    chunks = []
    chunk = ""
    for s in sentences:
        if len(chunk) < batch_size:
            chunk += f" {s}"
        else:
            chunks.append(chunk)
            chunk = f"{s}"

    chunks.append(chunk)
    return chunks


def generate_summaries(prompt, title, text):

    print(f"Length of Text: {len(text['text'])}")
    batches = create_batches(text)
    summaries = []
    for i in range(5):
        summary = ""
        for batch in batches:

            new_prompt = prompt + batch
            response = gpt3(new_prompt)
            summary += response["choices"][0]['text']

        # Split the string on the newline character
        bullet_points = summary.split('\n')

        # Initialize an empty list to store the extracted bullet points
        extracted_bullet_points = []

        # Iterate through the bullet points
        for bullet_point in bullet_points:
            # Use a regex to match bullet points that start with a number and a period
            if re.match(r'^[0-9]\.', bullet_point):
                extracted_bullet_points.append(bullet_point[3:])

        summaries.append(extracted_bullet_points)

    return summaries

def generate_titles(title):
    title_arr = [[title]]
    for i in range(1):
        idea = summarize_title(title).replace("\n", "").replace('"', '').replace("'", "")
        title_arr.append([idea])
    return title_arr

def summarize_title(title):
    prompt = f"turn this into a catchy title: {title}"
    return gpt3(prompt)["choices"][0]['text']

def generate_hashtags(summary):
    hashtags = []
    for i in range(5):
        hashtags.append(gpt3(f"generate one twitter hashtags: {summary}")["choices"][0]['text'])
    return hashtags

def text_options(options):
    clear_messages()
    send_message("\n\n\n\n NEW PODCAST")
    for idx, option in enumerate(options):
        text = f"{idx + 1}. \n"
        for line in option:
            text += f"- {line}\n"
        send_message(text)

    # time.sleep(120)
    response = listen()
    send_message(options[int(response)-1])
    return options[int(response)-1]

def input_options(options):


    for idx, option in enumerate(options):
        text = f"{idx + 1}. "
        for line in option:
            text += f"- {line}\n"
        print(text)

    # time.sleep(120)
    # resp = input("select: ")
    # resp = input("Please Select Best Response: ")
    # if resp == 'skip':
    #     return
    # return options[int(resp)-1]
    return ''


def clear_dir(dir):
    import glob
    files = glob.glob(f'{dir}/*')
    for f in files:
        os.remove(f)


def create_thread_from_clip(prompt, video_id):
    yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')

    # Download Video from YouTube
    local_path, title, desc = download_video(yt)
    # local_path = "audio/BestExercisesforOverallHealth&LongevityDrPeterAttia&DrAndrewHuberman.mp4"
    # title = "Best Exercises for Overall Health & Longevity Dr Peter Attia & Dr Andrew Huberman"

    # Speech to TExt
    text = transcribe_audio(local_path)

    # Build Titles
    # titles = generate_titles(title)
    # new_title = input_options(titles)
    # new_title[0] += hashtag

    # Build Summaries
    summaries = generate_summaries(prompt, title, text)
    summary = input_options(summaries)
    # if summary:
    #     # Tweet
    #     tweet_dict = {'title': new_title[0], 'body': summary}
    #     tweet(tweet_dict)

def create_thread_from_clipped_podcast(prompt, video_id):

    yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')

    # Download Video from YouTube
    local_path, title, desc = download_video(yt)

    # Extract Sections from video
    section_data = extract_section_data(desc)
    # clear_dir('clips')
    split_sections(local_path, section_data)
    time.sleep(30)

    for idx, filename in enumerate(sorted(os.listdir('clips'))):
        if idx < 4:
            continue
        try:
            # Speech to Text
            text = transcribe_audio("clips/" + filename)
            # Build Summaries
            summaries = generate_summaries(prompt, title, text)
            print(f'{filename.replace("_", " ").replace(".mp4", "")}\n')
            # print(summaries)
            summary = input_options(summaries)
            print("\n\n\n")
            # if summary:
            #     print(summary)
            #     tweet_dict = {'title': "here is a summary of the podcast", 'body': summary}
                # tweet(tweet_dict)
        except Exception as e:
            continue

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    hashtag = " #health @drandrewhuberman"
    video_id = "CyDLbrZK75U"

    # prompt = "summarize the key take aways as bullet points like a philospher in the following format 1. first point \n 2. second point \n 3. third point: "
    # create_thread_from_clip(prompt, video_id)

    prompt = "summarize the text like a philospher in one sentence in the following format 1. first point "
    create_thread_from_clipped_podcast(prompt, video_id)
