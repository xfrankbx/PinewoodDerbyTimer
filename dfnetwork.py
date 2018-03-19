import network

class NET:
    def __init__(self, ssid, key):
        self.ssid = ssid
        self.key = key
        self.station = network.WLAN(network.STA_IF)

    def connect(self):
        if not self.station.isconnected():
            print('connecting to network...')
            self.station.active(True)
            self.station.connect(self.ssid, self.key)
            while not self.station.isconnected():
                pass
        print('network config:', self.station.ifconfig())

