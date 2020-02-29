import os

from utils import get_thumbnail, get_thumbnail_url, download_youtube_video, resource_path

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFileDialog, QTreeWidgetItem, QApplication
from PyQt5.QtGui import QPixmap

from pytube import Playlist, extract
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search


class StreamLoader(QObject):

    sig_step = pyqtSignal(int, str)
    sig_done = pyqtSignal(int)
    sig_msg = pyqtSignal(str)
    sig_progress_status = pyqtSignal(int)
    sig_progress_total = pyqtSignal(int)
    sig_error = pyqtSignal(str)
    current_file_size = 0

    def __init__(self, id: int, download_manager):
        super().__init__()
        self.id = id
        self.__abort = False
        self.__download_manager = download_manager

    @pyqtSlot()
    def load_streams(self):
        while self.__download_manager.thread_count > 1:
            self.sig_step.emit(self.id, 'Waiting for threads to clear...')
        thread_name = QThread.currentThread().objectName()
        thread_id = int(QThread.currentThreadId())
        self.sig_step.emit(self.id, f'{thread_id}: {thread_name} thread starting...')
        self.__download_manager.videos = []
        self.__download_manager.streams = []
        proxies = self.__download_manager.get_proxies()
        top_level_item_count = self.__download_manager.stream_tree.topLevelItemCount()
        for i in range(top_level_item_count):
            self.__download_manager.stream_tree.takeTopLevelItem(i)
        self.__download_manager.stream_tree.clear()
        self.__download_manager.streams_to_download = {}
        try:
            print('get video id')
            print(extract.video_id(self.__download_manager.url.text()))
            self.sig_step.emit(self.id, f'Loading video')
            loaded_url = YouTube(self.__download_manager.url.text(), proxies=proxies)
            self.sig_step.emit(self.id, f'Loaded video: {loaded_url.title}')
            self.sig_msg.emit(f'Found {loaded_url.title}')
            if self.__abort:
                self.sig_progress_status.emit(f'Aborted!')
                self.sig_done.emit(self.id)
                return
            self.__download_manager.videos.append(loaded_url)

        except RegexMatchError:
            print('playlist')
            if 'playlist' in self.__download_manager.url.text():
                regex_search(r'(?:list=|\/)([0-9A-Za-z_-]{11}).*', self.__download_manager.url.text(), group=1)
                loaded_url = Playlist(self.__download_manager.url.text())
                self.sig_msg.emit(f'Loaded playlist. Discovering videos...')
                loaded_url.populate_video_urls()
                i = 0
                self.sig_progress_status.emit(0)

                for video_url in loaded_url.video_urls:
                    self.sig_step.emit(self.id, f'Loading video {i}')
                    if self.__abort:
                        self.sig_progress_status.emit(f'Aborted!')
                        self.sig_done.emit(self.id)
                        return
                    self.sig_progress_total.emit(int((i / (len(loaded_url.video_urls) * 2)) * 100))
                    vid = YouTube(video_url, proxies=proxies)
                    self.sig_step.emit(self.id, f'Loaded video: {vid.title}')
                    if self.__abort:
                        self.sig_progress_status.emit(f'Aborted!')
                        self.sig_done.emit(self.id)
                        return
                    self.sig_msg.emit(f'Found {vid.title}')

                    self.__download_manager.videos.append(vid)
                    self.sig_progress_status.emit(int((i / len(loaded_url.video_urls)) * 100))
                    i += 1
                self.sig_progress_total.emit(50)
            else:
                self.sig_error.emit('Could not determine Video '
                                    'or Playlist ID from provided URL!\n'
                                    'Please check input!')
                self.sig_done.emit(self.id)
                return
        except Exception as e:
            self.sig_error.emit(str(e))
            self.sig_done.emit(self.id)
            return

        self.sig_msg.emit(f'Loading Streams..')
        print('loading streams')
        i = 0
        for video in self.__download_manager.videos:
            self.sig_progress_status.emit(0)
            self.sig_step.emit(self.id, f'Loading streams for video {i}')
            if self.__abort:
                self.sig_progress_status.emit(f'Aborted!')
                self.sig_done.emit(self.id)
                return
            audio_streams = QTreeWidgetItem(['Audio Only'])
            tree_item = StreamTreeWidgetItem([video.title], f'video_{i}',
                                             self.__download_manager, video, None)
            self.__download_manager.streams = video.streams.all()
            x = 0
            for stream in self.__download_manager.streams:
                self.sig_step.emit(self.id, f'Loading stream {x}')
                if self.__abort:
                    self.sig_progress_status.emit(f'Aborted!')
                    self.sig_done.emit(self.id)
                    return
                self.sig_msg.emit(f'Video {i + 1}/{len(self.__download_manager.videos)}: '
                                  f'Loading Stream ITAG ID: {stream.itag}')
                if stream.video_codec is None:
                    stream_item = StreamTreeWidgetItem([
                        f'Codec: {stream.audio_codec}, '
                        f'ABR: {stream.abr}, '
                        f'File Type: {stream.mime_type.split("/")[1]}, '
                        f'Size: {stream.filesize // 1024} KB'
                    ], f'video_{i}_stream{x}',
                       self.__download_manager, video, stream)
                    self.sig_step.emit(self.id, f'Loaded stream {x}')
                    if self.__abort:
                        self.sig_progress_status.emit(f'Aborted!')
                        self.sig_done.emit(self.id)
                        return
                    audio_streams.addChild(stream_item)
                else:
                    stream_item = StreamTreeWidgetItem([
                        f'Res: {stream.resolution}, FPS: {stream.fps}, '
                        f' Video Codec: {stream.video_codec}, Audio Codec: {stream.audio_codec}, '
                        f'File Type: {stream.mime_type.split("/")[1]}, '
                        f'Size: {stream.filesize // 1024} KB'
                    ], f'video_{i}_stream{x}',
                       self.__download_manager, video, stream)
                    self.sig_step.emit(self.id, f'Loaded stream {x}')
                    if self.__abort:
                        self.sig_progress_status.emit(f'Aborted!')
                        self.sig_done.emit(self.id)
                        return
                    tree_item.addChild(stream_item)
                stream_item.setCheckState(0, Qt.Unchecked)
                x += 1
                self.sig_progress_status.emit(int((x / len(self.__download_manager.streams)) * 100))
            tree_item.addChild(audio_streams)
            self.sig_step.emit(self.id, f'Adding video {i} to tree')
            if self.__abort:
                self.sig_progress_status.emit(f'Aborted!')
                self.sig_done.emit(self.id)
                return
            self.__download_manager.stream_tree.addTopLevelItem(tree_item)
            i += 1
            self.sig_progress_status.emit(100)
            self.sig_progress_total.emit(int((i / (len(self.__download_manager.videos) * 2)) * 100) + 50)
        self.sig_msg.emit(f'Streams Loaded!')
        self.sig_done.emit(self.id)

    @pyqtSlot()
    def download_streams(self):
        while self.__download_manager.thread_count > 1:
            self.sig_step.emit(self.id, 'Waiting for threads to clear...')
        i = 0
        self.sig_progress_total.emit(0)
        for item_id, stream_item in self.__download_manager.streams_to_download.items():
            self.sig_step.emit(self.id, f'Downloading stream {i}')
            self.sig_msg.emit(f'Downloading Stream ({i + 1}/{len(self.__download_manager.streams_to_download)})...')
            if self.__abort:
                self.sig_progress_status.emit(f'Aborted!')
                self.sig_done.emit(self.id)
                break
            self.current_file_size = stream_item.stream.filesize
            filename_override = self.__download_manager.filename_override.text()
            filename = ''
            if len(self.__download_manager.streams_to_download) > 1:
                if filename_override != '':
                    filename += f'{filename_override}_'
                filename += f'{stream_item.video.title}'
                if stream_item.stream.video_codec is not None:
                    filename += f'_{stream_item.stream.resolution}_{stream_item.stream.fps}'
                    filename += f'_vc{stream_item.stream.video_codec}'
                if stream_item.stream.audio_codec is not None:
                    filename += f'_ac{stream_item.stream.audio_codec}'
                    filename += f'_abr{stream_item.stream.abr}'
                filename += f'_{i + 1}'
            else:
                if filename_override != '':
                    filename = filename_override
                else:
                    filename = stream_item.video.title
            download_youtube_video(itag=stream_item.stream.itag,
                                   output_path=os.path.abspath(self.__download_manager.output_path.text()),
                                   filename=filename, progress_callback=self.update_progress_bar,
                                   video_and_stream=(stream_item.video, stream_item.stream),
                                   proxies=self.__download_manager.get_proxies())
            self.sig_step.emit(self.id, f'Download finished')
            if self.__abort:
                self.sig_progress_status.emit(f'Aborted!')
                self.sig_done.emit(self.id)
                break
            i += 1
            self.sig_progress_total.emit(int((i / len(self.__download_manager.streams_to_download)) * 100))
        self.sig_msg.emit('Finished Download(s)')
        self.sig_done.emit(self.id)

    def update_progress_bar(self, stream, chunk, bytes_remaining):
        percentage = int(((self.current_file_size - bytes_remaining) / self.current_file_size) * 100)
        self.sig_progress_status.emit(percentage)

    def abort(self):
        if self.__abort:
            return
        # self.sig_msg.emit('Received Abort Message...')
        self.__abort = True


class StreamTreeWidgetItem(QTreeWidgetItem, QObject):
    UserType = 1000
    added_to_download_list = False

    def __init__(self, tree_strings, id, download_manager, video_object, stream_object):
        super().__init__(tree_strings)
        self.id = id
        self.video = video_object
        self.stream = stream_object
        self.download_manager = download_manager
        self.video_title = self.video.title

    def __repr__(self):
        return 'Mine'


# noinspection PyArgumentList
class DownloadTab(QWidget):

    display_name = 'Downloader'
    videos = None
    streams = None
    sig_abort_workers = pyqtSignal()
    sig_error = pyqtSignal(str)
    current_thumbnail = None
    streams_to_download = {}
    threads = []
    thread_count = 0
    error_dialog = None

    def __init__(self, main_window):
        super().__init__()
        QThread.currentThread().setObjectName('tab_downloader')
        loadUi(resource_path('qt_assets/tabs/tab_download.ui'), self)
        self.main_window = main_window
        self.init_ui()
        self.show()

    def init_ui(self):
        self.sig_error.connect(self.main_window.show_error)
        self.btn_load_url.clicked.connect(self.load_streams)
        self.btn_browse.clicked.connect(self.browse_folder)
        self.btn_download.clicked.connect(self.download_streams)

        self.output_path.setText(os.path.abspath(os.getcwd()))

        self.stream_tree.setHeaderLabel('Stream List')
        self.stream_tree.itemClicked.connect(self.check_for_checked)

    def start_worker(self, job_id):
        worker = StreamLoader(len(self.threads), self)
        thread = QThread()
        self.threads.append((thread, worker))
        worker.moveToThread(thread)

        worker.sig_step.connect(self.on_worker_step)
        worker.sig_done.connect(self.on_worker_done)
        worker.sig_msg.connect(self.status_text.setText)
        worker.sig_error.connect(self.show_error)
        worker.sig_progress_status.connect(self.progress_status.setValue)
        worker.sig_progress_total.connect(self.progress_total.setValue)
        self.sig_abort_workers.connect(worker.abort)

        self.btn_load_url.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.btn_download.setEnabled(False)
        self.url.setEnabled(False)
        self.output_path.setEnabled(False)
        self.filename_override.setEnabled(False)
        self.proxies.setEnabled(False)
        self.stream_tree.setEnabled(False)

        if job_id is 'load_streams':
            thread.started.connect(worker.load_streams)
            self.btn_download.setText(f'Select Streams to Download')
        elif job_id is 'download_streams':
            thread.started.connect(worker.download_streams)
        thread.start()
        self.thread_count += 1

    def load_streams(self):
        self.abort_workers()
        self.start_worker('load_streams')

    def download_streams(self):
        self.abort_workers()
        self.start_worker('download_streams')

    def browse_folder(self):
        self.output_path.setText(os.path.abspath(str(QFileDialog.getExistingDirectory(self,
                                                                                      'Select Output Directory'))))

    @pyqtSlot(QTreeWidgetItem, int)
    def check_for_checked(self, item, column):
        if item.stream is not None and item.checkState(0) == Qt.Checked and not item.added_to_download_list:
            self.streams_to_download[item.id] = item
            item.added_to_download_list = True
        elif item.stream is not None and item.checkState(0) == Qt.Unchecked and item.added_to_download_list:
            del self.streams_to_download[item.id]
            item.added_to_download_list = False

        if len(self.streams_to_download) > 0:
            self.btn_download.setEnabled(True)
            self.btn_download.setText(f'Download {len(self.streams_to_download)} Stream(s)')
        else:
            self.btn_download.setEnabled(False)
            self.btn_download.setText(f'Select Streams to Download')
        self.set_thumbnail(item, column)

    def get_proxies(self):
        proxies = self.proxies.text().replace(' ', '')
        if proxies != '':
            proxies = proxies.split(',')
            return {proxy.split(':')[0]: proxy for proxy in proxies}
        else:
            return None

    @pyqtSlot(QTreeWidgetItem, int)
    def set_thumbnail(self, item, column):
        self.current_thumbnail = QPixmap()
        self.current_thumbnail.loadFromData(get_thumbnail(get_thumbnail_url(video=item.video)).read())
        self.thumbnail_preview.setPixmap(self.current_thumbnail)

    @pyqtSlot(int, str)
    def on_worker_step(self, worker_id: int, data: str):
        QApplication.instance().processEvents()
        print(f'Worker {worker_id}: {data}')

    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        print(f'Worker {worker_id} done')
        self.thread_count -= 1

        if self.thread_count == 0:
            self.btn_load_url.setEnabled(True)
            self.btn_browse.setEnabled(True)
            self.btn_download.setEnabled(True)
            self.url.setEnabled(True)
            self.output_path.setEnabled(True)
            self.filename_override.setEnabled(True)
            self.proxies.setEnabled(True)
            self.stream_tree.setEnabled(True)

    @pyqtSlot()
    def abort_workers(self):
        self.sig_abort_workers.emit()
        for thread, worker in self.threads:
            worker.abort()
            thread.quit()
            thread.wait()

    def show_error(self, error_msg):
        self.sig_error.emit(error_msg)
