#!/usr/bin/env python3.6
import tkinter as tk
import os.path


from pytube import YouTube
from threading import Thread
from tkinter import filedialog, messagebox, ttk
from download_youtube_video import download_youtube_video
from pytube.exceptions import PytubeError, RegexMatchError


class YouTubeDownloadGUI(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.label_video_title = None
        self.btn_download = None
        self.btn_output_browse = None
        self.btn_check_id = None
        self.text_url = None
        self.text_output_path = None
        self.text_filename_override = None
        self.text_proxy = None
        self.radio_video_audio = []
        self.audio_only = tk.BooleanVar(self)
        self.output_path = tk.StringVar(self)
        self.filename_override = tk.StringVar(self)
        self.proxy = tk.StringVar(self)
        self.video = None
        self.stream = tk.IntVar(self)
        self.streams = []
        self.stream_widgets = []
        self.file_size = 0
        self.progress_bar = None

        self.last_row = 0

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text='YouTube URL/ID').grid(row=0, column=0)
        self.text_url = tk.Entry(self, width=60)
        self.text_url.grid(row=0, column=1, columnspan=2)
        self.btn_check_id = tk.Button(self)
        self.btn_check_id['text'] = 'Check Video'
        self.btn_check_id['command'] = self.check_video
        self.btn_check_id.grid(row=0, column=3)

        tk.Label(self, text='Output Directory').grid(row=1, column=0)
        self.text_output_path = tk.Entry(self, width=60, textvariable=self.output_path)
        self.text_output_path.grid(row=1, column=1, columnspan=2)
        self.btn_output_browse = tk.Button(self)
        self.btn_output_browse['text'] = 'Browse...'
        self.btn_output_browse['command'] = self.browse_output_path
        self.btn_output_browse.grid(row=1, column=3)

        tk.Label(self, text='Filename Override').grid(row=2, column=0)
        self.text_filename_override = tk.Entry(self, width=60, textvariable=self.filename_override)
        self.text_filename_override.grid(row=2, column=1, columnspan=2)

        tk.Label(self, text='Proxy').grid(row=3, column=0)
        self.text_proxy = tk.Entry(self, width=60, textvariable=self.proxy)
        self.text_proxy.grid(row=3, column=1, columnspan=2)

        tk.Label(self, text='Media Type').grid(row=4, column=0)
        self.radio_video_audio.append(tk.Radiobutton(self, text='Video', variable=self.audio_only,
                                                     value=False, command=self.check_video))
        self.radio_video_audio.append(tk.Radiobutton(self, text='Audio (Takes Longer)', variable=self.audio_only,
                                                     value=True, command=self.check_video))
        self.radio_video_audio[0].grid(row=4, column=1)
        self.radio_video_audio[1].grid(row=4, column=2)

        self.label_video_title = tk.Label(self)
        self.label_video_title.grid(row=5, column=0, columnspan=4)
        self.last_row = 5

    def browse_output_path(self):
        self.output_path.set(filedialog.askdirectory(initialdir='/', title='Select Output Folder'))

    def check_video(self):
        self.btn_check_id['text'] = 'Checking...'
        self.btn_check_id.config(state=tk.DISABLED)
        Thread(target=self.threaded_check_video).start()

    def threaded_check_video(self):
        self.last_row = 5
        self.stream.set(0)
        [radio_button.destroy() for radio_button in self.stream_widgets]
        if self.btn_download:
            self.progress_bar.destroy()
            self.btn_download.destroy()
        url = self.text_url.get()
        if 'https' not in url:
            url = 'https://www.youtube.com/watch?v=%s' % url
        try:
            if self.proxy.get() != '':
                self.video = YouTube(url, proxies={self.proxy.get().split(':')[0]: self.proxy.get()})
            else:
                self.video = YouTube(url)
            self.label_video_title['text'] = self.video.title
            self.streams = self.video.streams.filter(only_audio=self.audio_only.get()).all()

            for stream in self.streams:
                if self.audio_only.get():
                    text = f'Codec: {stream.audio_codec}, ' \
                           f'ABR: {stream.abr} ' \
                           f'File Type: {stream.mime_type.split("/")[1]}, Size: {stream.filesize // 1024} KB'
                else:
                    if stream.video_codec is None:
                        continue
                    text = f'Res: {stream.resolution}, FPS: {stream.fps},' \
                           f' Video Codec: {stream.video_codec}, Audio Codec: {stream.audio_codec}, ' \
                           f'File Type: {stream.mime_type.split("/")[1]}, Size: {stream.filesize // 1024} KB'
                radio_button = tk.Radiobutton(self, text=text, variable=self.stream, value=stream.itag)
                self.last_row += 1
                radio_button.grid(row=self.last_row, column=0, columnspan=4)
                self.stream_widgets.append(radio_button)
            self.last_row += 1
            self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=350, mode='determinate')
            self.progress_bar.grid(row=self.last_row, column=1, columnspan=2)

            self.progress_bar['value'] = 0
            self.progress_bar['maximum'] = 100

            self.last_row += 1
            self.btn_download = tk.Button(self)
            self.btn_download['text'] = 'Download'
            self.btn_download['command'] = self.download
            self.btn_download.config(state=tk.NORMAL)
            self.btn_download.grid(row=self.last_row, column=1, columnspan=2)
        except PytubeError as e:
            messagebox.showerror('Something went wrong...', e)
        except RegexMatchError as e:
            messagebox.showerror('Something went wrong...', e)
        finally:
            self.btn_check_id['text'] = 'Check Video'
            self.btn_check_id.config(state=tk.NORMAL)

    def download(self):
        self.btn_download['text'] = 'Downloading...'
        self.btn_download.config(state=tk.DISABLED)
        self.btn_check_id.config(state=tk.DISABLED)
        self.btn_output_browse.config(state=tk.DISABLED)
        [radio_button.config(state=tk.DISABLED) for radio_button in self.radio_video_audio]
        Thread(target=self.threaded_download).start()

    def update_progress_bar(self, stream, chunk, file_handle, bytes_remaining):
        percentage = ((self.file_size - bytes_remaining) / self.file_size) * 100
        self.progress_bar['value'] = percentage

    def threaded_download(self):
        try:
            if self.proxy.get() != '':
                proxy = {self.proxy.get().split(':')[0]: self.proxy.get()}
            else:
                proxy = None
            for search_stream in self.streams:
                if int(search_stream.itag) == int(self.stream.get()):
                    self.file_size = search_stream.filesize
                    break
            filename = download_youtube_video(self.text_url.get(), itag=self.stream.get(),
                                              output_path=self.output_path.get(),
                                              filename=self.filename_override.get()
                                              if self.filename_override.get() != '' else None,
                                              proxies=proxy, progress_callback=self.update_progress_bar)
            messagebox.showinfo('Download Complete!', 'Download Complete!\n%s' % filename)
        except PytubeError as e:
            messagebox.showerror('Something went wrong...', e)
        except RegexMatchError as e:
            messagebox.showerror('Something went wrong...', e)
        except Exception as e:
            messagebox.showerror('Something went wrong',
                                 'Something unknown went wrong. Is this a live stream? Wait until the stream ends.'
                                 '\n\n%s' % e)
        finally:
            self.btn_download['text'] = 'Download'
            self.btn_download.config(state=tk.NORMAL)
            self.btn_check_id.config(state=tk.NORMAL)
            self.btn_output_browse.config(state=tk.NORMAL)
            [radio_button.config(state=tk.NORMAL) for radio_button in self.radio_video_audio]


def resource_path(relative_path):
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


if __name__ == '__main__':
    root = tk.Tk()
    app = YouTubeDownloadGUI(master=root)
    app.master.title('YouTube Video/Audio Downloader')
    app.master.tk.call('wm', 'iconphoto', app.master._w, tk.PhotoImage(file=resource_path('assets/ytdl.png')))
    app.mainloop()
