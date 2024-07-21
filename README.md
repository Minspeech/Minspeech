## Minspeech

A Corpus of Southern Min Dialect for Automatic Speech Recognition

[**Official website**](https://minspeech.github.io/)
| [**Paper**]()

## Resource
Let's start with obtaining the [resource](https://drive.google.com/drive/folders/1tGurSeeWALcBKKmmpKQQq7p4s-1o-Vce) files.

## File structure
```
% The file structure is summarized as follows:
|---- crop.py	# extract speech/video segments by timestamps from downloaded videos
|---- download.py	# download audios by audio_list
|---- LICENSE		# license
|---- README.md	
|---- requirement.txt			
|---- resource               # resource folder
      |---- label
            |---- list       # video_list for downloading audios
            |---- data       # [utt] train,dev,test
                  |---- train_text	
                  |---- train_wav.scp
                  |---- dev_text	
                  |---- dev_wav.scp
                  |---- test_text	
                  |---- test_wav.scp
       |---- unlabel
            |---- list       # video_list for downloading audios
```

## Download

### Install ffmpeg

``` bash
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install ffmpeg
``` 

### Clone Repo

``` bash
git clone https://github.com/Minspeech/minspeech.git
```

### Install Python library

``` bash
python3 -m pip install -r requirements.txt
```

### Download

``` bash
python download.py
```

### Crop

For labeled audio, use the script we provide to cut the audio, and for unlabeled audio, use the [silero-vad](https://github.com/snakers4/silero-vad) toolkit to cut it.

``` bash
python crop.py
```


