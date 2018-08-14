#!/usr/bin/env python3.6
# A simple Python Script that will allow you download video
import argparse


from pytube import YouTube
from download_youtube_video import download_youtube_video


def get_header():
    return """\
      $$\     $$\                $$$$$$$$\        $$\                        $$$$$$\                      $$\            $$\     
      \$$\   $$  |               \__$$  __|       $$ |                      $$  __$$\                     \__|           $$ |    
       \$$\ $$  /$$$$$$\  $$\   $$\ $$ |$$\   $$\ $$$$$$$\   $$$$$$\        $$ /  \__| $$$$$$$\  $$$$$$\  $$\  $$$$$$\ $$$$$$\   
        \$$$$  /$$  __$$\ $$ |  $$ |$$ |$$ |  $$ |$$  __$$\ $$  __$$\       \$$$$$$\  $$  _____|$$  __$$\ $$ |$$  __$$\\_$$  _|  
         \$$  / $$ /  $$ |$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$$$$$$$ |       \____$$\ $$ /      $$ |  \__|$$ |$$ /  $$ | $$ |    
          $$ |  $$ |  $$ |$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$   ____|      $$\   $$ |$$ |      $$ |      $$ |$$ |  $$ | $$ |$$\ 
          $$ |  \$$$$$$  |\$$$$$$  |$$ |\$$$$$$  |$$$$$$$  |\$$$$$$$\       \$$$$$$  |\$$$$$$$\ $$ |      $$ |$$$$$$$  | \$$$$  |
          \__|   \______/  \______/ \__| \______/ \_______/  \_______|       \______/  \_______|\__|      \__|$$  ____/   \____/ 
                                                                                                              $$ |               
                                                                                                              $$ |               
                                                                                                              \__|               
    """


def get_footer():
    return """\n
    $$$$$$$$\ $$\                           $$\                       $$$$$$$$\                        $$\   $$\           $$\                     
    \__$$  __|$$ |                          $$ |                      $$  _____|                       $$ |  $$ |          \__|                    
       $$ |   $$$$$$$\   $$$$$$\  $$$$$$$\  $$ |  $$\  $$$$$$$\       $$ |    $$$$$$\   $$$$$$\        $$ |  $$ | $$$$$$$\ $$\ $$$$$$$\   $$$$$$\  
       $$ |   $$  __$$\  \____$$\ $$  __$$\ $$ | $$  |$$  _____|      $$$$$\ $$  __$$\ $$  __$$\       $$ |  $$ |$$  _____|$$ |$$  __$$\ $$  __$$\ 
       $$ |   $$ |  $$ | $$$$$$$ |$$ |  $$ |$$$$$$  / \$$$$$$\        $$  __|$$ /  $$ |$$ |  \__|      $$ |  $$ |\$$$$$$\  $$ |$$ |  $$ |$$ /  $$ |
       $$ |   $$ |  $$ |$$  __$$ |$$ |  $$ |$$  _$$<   \____$$\       $$ |   $$ |  $$ |$$ |            $$ |  $$ | \____$$\ $$ |$$ |  $$ |$$ |  $$ |
       $$ |   $$ |  $$ |\$$$$$$$ |$$ |  $$ |$$ | \$$\ $$$$$$$  |      $$ |   \$$$$$$  |$$ |            \$$$$$$  |$$$$$$$  |$$ |$$ |  $$ |\$$$$$$$ |
       \__|   \__|  \__| \_______|\__|  \__|\__|  \__|\_______/       \__|    \______/ \__|             \______/ \_______/ \__|\__|  \__| \____$$ |
                                                                                                                                         $$\   $$ |
                                                                                                                                         \$$$$$$  |
                                                                                                                                          \______/ 
    \n\n\n
    """


def interactive_mode():
    print(get_header())
    while True:
        user = input('To Download Video/Audio Y/n: ')
        if user.lower() in ['yes', 'y']:
            url = input('Enter Url: ')
            form = input('Do you want to download video or audio: ')
            if form.lower() in ['video', 'v']:
                download_youtube_video(url, output_path='videos/')

            elif form.lower() in ['audio', 'a']:
                warn = input('Audio Downloads take longer Do you want to Continue Y/n: ')
                if warn.lower() in ['yes', 'y']:
                    download_youtube_video(url, audio_only=True, output_path='audio/')

                elif warn.lower() in ['no', 'n']:
                    vid = input('To Download Vid Y/n ')
                    if vid.lower() in ['yes', 'y']:
                        download_youtube_video(url, output_path='videos/')

                    elif vid.lower() in ['no', 'n']:
                        exit()
        if user.lower() in ['no', 'n']:
            print(get_footer())
            exit()


def list_streams(url, audio_only=False, proxies=None):
    if 'https' not in url:
        url = 'https://www.youtube.com/watch?v=%s' % url
    if proxies:
        video = YouTube(url, proxies=proxies)
    else:
        video = YouTube(url)
    print(f'{video.title}')
    for stream in video.streams.filter(only_audio=audio_only).all():
        if audio_only:
            print(f'ITAG: {stream.itag}, Codec: {stream.audio_codec}, '
                  f'ABR: {stream.abr}, File Type: {stream.mime_type.split("/")[1]}')
        else:
            if stream.video_codec is None:
                continue
            print(f'ITAG: {stream.itag}, Res: {stream.resolution}, FPS: {stream.fps}, '
                  f'Video Codec: {stream.video_codec}, Audio Codec: {stream.audio_codec}, '
                  f'File Type: {stream.mime_type.split("/")[1]}')

    print('\n\nTo download a specific stream, use the -i/--itag argument and provide the ITAG ID.')


def parse_args():
    parser = argparse.ArgumentParser(description='YouTube Video/Audio Downloader')
    parser.add_argument('-u', '--url', help='YouTube URL or YouTube Video ID to download', default=None)
    parser.add_argument('-l', '--list-streams', help='List available streams for this YouTube Video '
                                                     'instead of download. Use -a/--audio-only to list audio streams. '
                                                     'Download specific stream with the '
                                                     'itag ID and -i/--itag argument.',
                        action='store_true', default=False)
    parser.add_argument('-i', '--itag', help='Stream ITAG to download for given YouTube Video/ID. '
                                             'List streams with -l/--list-streams argument. '
                                             'If ITAG is not provided, default stream will be downloaded. '
                                             'Downloading with ITAG ignores -a/--audio-only.', type=int, default=None)
    parser.add_argument('-o', '--output-path', help='Output Directory Path', default=None)
    parser.add_argument('-f', '--filename', help='Override the output filename. Does not override file extension',
                        default=None)
    parser.add_argument('-p', '--proxy', help='Proxy to use. Ex http://xxx.xxx.xxx:8080 '
                                              'NOTE: You need https proxy for https URL!', default=None)
    parser.add_argument('-a', '--audio-only', help='Download Audio Only', action='store_true', default=False)

    parsed_args = parser.parse_args()
    if parsed_args.proxy:
        parsed_args.proxy = {parsed_args.proxy.split(':')[0]: parsed_args.proxy}

    return parsed_args


if __name__ == '__main__':
    args = parse_args()
    if args.url:
        if args.list_streams:
            list_streams(args.url, audio_only=args.audio_only, proxies=args.proxy)
        else:
            download_youtube_video(args.url, itag=args.itag, audio_only=args.audio_only,
                                   output_path=args.output_path, filename=args.filename,
                                   proxies=args.proxy)
    else:
        interactive_mode()
