from os import makedirs
from pytube import YouTube
from urllib.request import urlopen
from pytube.helpers import safe_filename
from pytube.extract import video_id as get_video_id


THUMBNAIL_QAULITY_LOW = 'sddefault'
THUMBNAIL_QAULITY_MED = 'mqdefault'
THUMBNAIL_QAULITY_HI = 'hqdefault'
THUMBNAIL_QAULITY_MAX = 'maxresdefault'


def get_thumbnail_url(url=None, video=None, quality=THUMBNAIL_QAULITY_MED):
    if url is None and video is None:
        raise ValueError('You must provide either a url or YouTube object.')
    if video:
        return f'{video.thumbnail_url.rsplit("/", 1)[0]}/{quality}.jpg'
    if 'http' in url:
        video_id = get_video_id(url)
        return f'https://i.ytimg.com/vi/{video_id}/{quality}.jpg'
    return f'https://i.ytimg.com/vi/{url}/{quality}.jpg'


def get_thumbnail(url):
    response = urlopen(url)
    return response


def download_youtube_video(url=None, itag=None, audio_only=False, output_path=None,
                           filename=None, filename_prefix=None,
                           proxies=None, progress_callback=None, video_and_stream=None):
    """
    Download a YouTube Video.
    :param url: Full URL to YouTube Video or YouTube Video ID
    :type url: str
    :param itag: YouTube Stream ITAG to Download
    :type itag: int
    :param audio_only: Download only the audio for the video. Takes longer than video.
    :type audio_only: bool
    :param output_path: Path to folder to output file.
    :type output_path: str
    :param filename: Filename override. Does not override extension.
    :type filename: str
    :param filename_prefix: Currently Does Not Work on pytube
    :type filename_prefix: str
    :param proxies: Dictionary containing protocol (key) and address (value) for the proxies
    :type proxies: dict
    :return: Filename of downloaded video/audio
    :rtype: str
    """
    if url is None and video_and_stream is None:
        raise ValueError('You must provide either a url or video/stream object tuple')
    if output_path:
        makedirs(output_path, exist_ok=True)
    if video_and_stream is None:
        if 'http' not in url:
            url = 'https://www.youtube.com/watch?v=%s' % url
        video = YouTube(url, proxies=proxies)
        if itag:
            itag = int(itag)
            stream = video.streams.get_by_itag(itag)
        else:
            stream = video.streams.filter(only_audio=audio_only).first()
    else:
        video, stream = video_and_stream
    if progress_callback:
        video.register_on_progress_callback(progress_callback)
    print('Download Started: %s' % video.title)
    if filename:
        filename = safe_filename(filename)
    stream.download(output_path=output_path, filename=filename)
    file_type = '.' + stream.mime_type.split('/')[1]
    filename = stream.default_filename if filename is None else filename + file_type
    print('Download Complete! Saved to file: %s' % filename)
    return filename


def resource_path(relative_path):
    import sys
    import os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
