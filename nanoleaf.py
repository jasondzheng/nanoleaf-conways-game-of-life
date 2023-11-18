from dataclasses import dataclass

import requests
import socket
import threading

# Nanoleaf OpenAPI Documentation: https://forum.nanoleaf.me/docs/openapi

API_PORT = 16021 # Default port (per Nanoleaf docs)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_lock = threading.Lock()

@dataclass
class PanelUpdate():
    panel_id: int
    r: int
    g: int
    b: int
    w: int = 0
    t: int = 0

class NanoleafCluster:
    def __init__(self, ip, key):
        self.ip = ip
        self.key = key
        self.layout = self._request_layout()

    def _request_layout(self):
        return requests.get(f'http://{self.ip}:{API_PORT}/api/v1/{self.key}/panelLayout/layout').json()

    def init_streaming(self):
        pass

    def stream_updates(self, updates:list[PanelUpdate]):
        pass

class NanoleafCanvasGridCluster(NanoleafCluster):
    STREAMING_PORT = 60222
    PANEL_SIZE = 100

    def __init__(self, ip, key):
        super().__init__(ip, key)
        x_min = min([data['x'] for data in self.layout['positionData']])
        y_min = min([data['y'] for data in self.layout['positionData']])
        self.x_size = (max([data['x'] for data in self.layout['positionData']]) - x_min) // NanoleafCanvasGridCluster.PANEL_SIZE + 1
        self.y_size = (max([data['y'] for data in self.layout['positionData']]) - y_min) // NanoleafCanvasGridCluster.PANEL_SIZE + 1
        self._id_lookup = {((data['x'] - x_min) // NanoleafCanvasGridCluster.PANEL_SIZE, (data['y'] - y_min) // NanoleafCanvasGridCluster.PANEL_SIZE):data['panelId'] for data in self.layout['positionData'] }
    
    def lookup_panel_id(self, x, y):
        return self._id_lookup.get((x, y))

    def init_streaming(self):
        resp = requests.put(f'http://{self.ip}:{API_PORT}/api/v1/{self.key}/effects', json={'write': {'command': 'display', 'animType': 'extControl', 'extControlVersion': 'v2'}})
        print(resp.status_code)
        if resp.status_code != 204 and resp.status_code != 200:
            raise Exception("Could not init streaming")
    
    def stream_updates(self, updates:list[PanelUpdate]):
        msg = bytearray()
        # Build stream v2 message as defined in https://forum.nanoleaf.me/docs/openapi#_9gd8j3cnjaju
        msg.append((len(updates) & 0xFF00) >> 8)
        msg.append(len(updates) & 0xFF)
        for update in updates:
            msg.append((update.panel_id & 0xFF00) >> 8)
            msg.append(update.panel_id & 0xFF)
            msg.append(update.r & 0xFF)
            msg.append(update.g & 0xFF)
            msg.append(update.b & 0xFF)
            msg.append(update.w & 0xFF)  
            msg.append((update.t & 0xFF00) >> 8)
            msg.append(update.t & 0xFF)
        print(msg.hex())
        with sock_lock:
            sock.sendto(msg, (self.ip, NanoleafCanvasGridCluster.STREAMING_PORT))

