import machine

class LED:

    def __init__(self, id):
        self.id = id
        machine.Pin(id, machine.Pin.OUT)
        machine.Pin(id).value(0)

    def on(self):
        machine.Pin(self.id).value(1)

    def off(self):
        machine.Pin(self.id).value(0)

    def value(self):
        return machine.Pin(self.id).value()

    def toggle(self):
        if self.value():
            self.off()
        else:
            self.on()

