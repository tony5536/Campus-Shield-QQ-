class IoTGateway:
    def __init__(self):
        self.devices = []

    def register_device(self, device):
        self.devices.append(device)
        print(f"Device {device} registered.")

    def deregister_device(self, device):
        self.devices.remove(device)
        print(f"Device {device} deregistered.")

    def send_data(self, device, data):
        if device in self.devices:
            print(f"Sending data from {device}: {data}")
        else:
            print(f"Device {device} not registered.")

    def receive_data(self, device):
        if device in self.devices:
            print(f"Receiving data from {device}.")
            # Simulate receiving data
            return {"status": "data received"}
        else:
            print(f"Device {device} not registered.")
            return None

    def get_registered_devices(self):
        return self.devices