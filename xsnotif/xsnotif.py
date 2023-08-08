from typing import List, ClassVar, Optional
import socket
from dataclasses import dataclass
from threading import Thread, Event
import json
from enum import IntEnum
import re

re_word = re.compile(r'\w+')

class MessageType(IntEnum):
    NOTIFICATION = 1
    MEDIA_PLAYER = 2

DEFAULT_HEIGHT:  float = 175
DEFAULT_OPACITY: float = 1
DEFAULT_TIMEOUT: float = 3
DEFAULT_VOLUME:  float = 0.7

@dataclass
class Notification:
    title: str
    content: str
    source_app: str = ''
    icon: str = 'default'
    audio_path: str = 'default'
    message_type: MessageType = MessageType.NOTIFICATION
    height: float = DEFAULT_HEIGHT
    opacity: float = DEFAULT_OPACITY
    timeout: float = DEFAULT_TIMEOUT
    volume: float = DEFAULT_VOLUME
    index: int = 0
    use_base64_icon: bool = False

    def as_json(self) -> str:
        return json.dumps({
            'title': self.title,
            'content': self.content,
            'sourceApp': self.source_app,
            'icon': self.icon,
            'audioPath': self.audio_path,
            'messageType': self.message_type,
            'height': self.height,
            'opacity': self.opacity,
            'timeout': self.timeout,
            'index': self.index,
            'volume': self.volume,
            'useBase64Icon': self.use_base64_icon
        })

    def as_json_bytes(self) -> bytes:
        return bytes(self.as_json(), 'UTF-8')

class Notifier:
    def worker(notifier: 'Notifier'):
        notifier.client_socket.connect(('localhost', notifier.port))
        while not notifier.stop_event.isSet():
            if len(notifier.queue):
                notif: Notification = notifier.queue.pop(0)
                if notif.timeout == 0:
                    notif.timeout = notifier.reading_time(notif.title, notif.content)
                if notif.volume == 0:
                    notif.audio_path = ''
                notifier.client_socket.send(notif.as_json_bytes())
            notifier.stop_event.wait(notifier.polling_rate)
        notifier.client_socket.close()

    def __init__(self, port: int = 42069, *,
                 polling_rate: float = 5,
                 reading_time_wpm: float = 255,
                 default_opacity: float = DEFAULT_OPACITY,
                 default_height: float = DEFAULT_HEIGHT,
                 default_volume: float = DEFAULT_VOLUME,
                 default_timeout: float = 0,
                 default_audio_path: str = 'default',
                 default_icon_path: str = 'default'
                 ):
        self.port: int = port
        self.stop_event: Event = Event()
        self.queue: List[Notification] = []
        self.worker_thread = Thread(target=Notifier.worker, args=(self,))
        self.worker_thread.daemon = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1)
        self.polling_rate = polling_rate
        self.reading_time_wpm = reading_time_wpm
        self.default_opacity = default_opacity
        self.default_height = default_height
        self.default_volume = default_volume
        self.default_timeout = default_timeout
        self.default_audio_path = default_audio_path
        self.default_icon_path = default_icon_path

    def reading_time(self, *text: str) -> float:
        text = ' '.join(text)
        count = len(re_word.findall(text))
        seconds = count / (self.reading_time_wpm / 60)
        return max(seconds, 2)

    def start(self):
        self.stop_event.clear()
        self.worker_thread.start()

    def stop(self):
        self.stop_event.set()
        self.worker_thread.join()

    def send(self, notif: Notification):
        self.queue.append(notif)

    def send_notification(self,
            title: str,
            content: str,
            source_app: str = '',
            icon: Optional[str] = None,
            audio_path: Optional[str] = None,
            height: Optional[float] = None,
            opacity: Optional[float] = None,
            timeout: Optional[float] = None,
            volume: Optional[float] = None,
            *,
            message_type: MessageType = MessageType.NOTIFICATION,
            index: int = 0,
            use_base64_icon: bool = False
        ):
        self.queue.append(Notification(
            title=title,
            content=content,
            source_app=source_app,
            icon=self.default_icon_path if icon is None else icon,
            audio_path=self.default_audio_path if audio_path is None else audio_path,
            height=self.default_height if height is None else height,
            opacity=self.default_opacity if opacity is None else opacity,
            timeout=self.default_timeout if timeout is None else timeout,
            volume=self.default_volume if volume is None else volume,
            message_type=message_type,
            index=index,
            use_base64_icon=use_base64_icon
        ))

    def send_warning(self,
            title: str,
            content: str,
            source_app: str = '',
            height: Optional[float] = None,
            opacity: Optional[float] = None,
            timeout: Optional[float] = None,
            volume: Optional[float] = None,
            index: int = 0
        ):
        self.send_notification(
            title=title,
            content=content,
            source_app=source_app,
            icon='warning',
            audio_path='warning',
            height=height,
            opacity=opacity,
            timeout=timeout,
            volume=volume,
            index=index
        )
        
    def send_error(self,
            title: str,
            content: str,
            source_app: str = '',
            height: Optional[float] = None,
            opacity: Optional[float] = None,
            timeout: Optional[float] = None,
            volume: Optional[float] = None,
            index: int = 0
        ):
        self.send_notification(
            title=title,
            content=content,
            source_app=source_app,
            icon='error',
            audio_path='error',
            height=height,
            opacity=opacity,
            timeout=timeout,
            volume=volume,
            index=index
        )