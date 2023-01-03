
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

def create_batches(text):

    sentences = nltk.tokenize.sent_tokenize(text['text'].replace("\n", ""))
    chunks = []
    chunk = ""
    for s in sentences:
        if len(chunk) < 16000:
            chunk += f" {s}"
        else:
            chunks.append(chunk)
            chunk = f"{s}"

    chunks.append(chunk)
    return chunks


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
    mp4_file = yt.streams.filter(only_audio=True)[0]
    fn = mp4_file.default_filename
    mp4_file.download(f'audio/')
    os.rename(f'audio/{fn}', f'audio/{fn.replace(" ", "")}')
    fn = fn.replace(" ", "")
    return f"audio/{fn}", mp4_file.title

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

def summerize_text(title, text):

    prompt = "summarize the key take aways as bullet points in the following format 1. first point \n 2. second point \n t3. third point: "
    print(f"Length of Text: {len(text['text'])}")
    batches = create_batches(text)
    summaries = []
    for i in range(10):
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

def summarize_title(title):
    prompt = f"turn this into a catchy title: {title}"
    return gpt3(prompt)["choices"][0]['text']

def get_relevant_hashtags(summary):
    return gpt3(f"create twitter hashtags for the following test: {summary}")["choices"][0]['text']

def text_options():



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    from test import test
    # vids = get_new_videos("lexfridman")
    video_id = "H64KAkM0wF4"
    local_path, title = download_video(video_id)
    # local_path = "audio/TheScienceofCreativity&HowtoEnhanceCreativeInnovationHubermanLabPodcast103.mp4"
    text = transcribe_audio(local_path)
    summerize_text(title, text)

    text_options()
