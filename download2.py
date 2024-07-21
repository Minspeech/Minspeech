import yt_dlp
import time, argparse, os, json
from tqdm import tqdm
import multiprocessing as mp
from multiprocessing import Manager
import random, logging, sys
import zhconv
import re

logging.basicConfig(level=logging.INFO)  # configure logging level to INFO

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--base_dir', 
                    default='SourceData', 
                    type=str,
                    help="where to save audio files")
parser.add_argument('--num_workers', 
                    default=1, 
                    type=int,
                    help="Multi-Process to facilitate download process")
args = parser.parse_args()

# Convert Traditional Chinese to Simplified Chinese
def traditional_to_simplified(traditional_text):
    return zhconv.convert(traditional_text, 'zh-hans')

# Remove all punctuation
def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

# Convert subtitle file from Traditional to Simplified Chinese and remove punctuation
def convert_subtitle_to_simplified(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    simplified_lines = []
    for line in lines:
        simplified_line = traditional_to_simplified(line)
        if '-->' not in simplified_line and not simplified_line.startswith(('WEBVTT', 'Kind:', 'Language:')):
            simplified_line = remove_punctuation(simplified_line)
        simplified_lines.append(simplified_line)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(simplified_lines)
    print(f"Converted and cleaned {file_path} to simplified Chinese without punctuation.")

# Download audio and subtitles from YouTube
def job_audio(urls, series):
    base_dir = os.path.join(os.getcwd(), args.base_dir, series)
    os.makedirs(base_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(base_dir) if f.endswith('.wav')]
    file_num = len(existing_files) + 1
    
    for url in urls:
        file_num_str = f"{file_num:03}"
        output_template = os.path.join(base_dir, f"{series}{file_num_str}")
        wav_file = f"{output_template}.wav"
        vtt_file = f"{output_template}.vtt"
        
        # Check if files already exist to support resumable download
        if os.path.exists(wav_file) and os.path.exists(vtt_file):
            print(f"Files {wav_file} and {vtt_file} already exist. Skipping download.")
            file_num += 1
            continue

        ydl_opts_audio = {
            'format': 'bestaudio[height<=720]+bestaudio',
            'outtmpl': wav_file,
            'noplaylist': True,
            'ignoreerrors': True,
            'max_sleep_interval': 0.2,
            'verbose': False,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegaudioConvertor',
                'preferedformat': 'wav',
            }],
            'postprocessor_args': [
                '-ar', '16000',
                '-strict', '-2',
                '-async', '1', '-r', '25'
            ],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            error_code = ydl.download([url])
        
        ydl_opts_sub = {
            'writesubtitles': True,
            'subtitleslangs': ['zh-TW'],
            'skip_download': True,
            'outtmpl': vtt_file
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_sub) as ydl:
            error_code = ydl.download([url])
        
        file_num += 1
        
        if os.path.exists(vtt_file):
            convert_subtitle_to_simplified(vtt_file)

# Split dictionary into multiple chunks
def split_dict(data, num_splits):
    keys = list(data.keys())
    random.shuffle(keys)
    split_keys = [keys[i::num_splits] for i in range(num_splits)]
    return [{k: data[k] for k in subset} for subset in split_keys]

# Download
def download(episodeaudio):
    for series, audio in episodeaudio.items():
        os.makedirs(os.path.join(os.getcwd(), args.base_dir, series), exist_ok=True)
        err_codes = job_audio(audio, series)

if __name__ == '__main__':
    print("*" * 15)
    print("* Download Starts *")
    print("*" * 15)
    os.makedirs(os.path.join(os.getcwd(), args.base_dir), exist_ok=True)
    episodeaudio_loc = "resource/minspeech/label/list"
    if not os.path.exists(episodeaudio_loc):
        logging.error("audio list not exist!!")
        sys.exit()
    # Load audio
    episodeaudio = {line.split()[0]: line.strip().split()[1:] for line in open(episodeaudio_loc)}
    workers = min(args.num_workers, len(episodeaudio))
    episodeaudio_slices = split_dict(episodeaudio, workers)
    pool = mp.Pool(processes=workers)
    pool.map(download, episodeaudio_slices)
    pool.close()
    pool.join()
