class CameraAgent:
    def __init__(self, camera_id, stream_url):
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.is_streaming = False

    def start_stream(self):
        if not self.is_streaming:
            # Logic to start streaming from the camera
            self.is_streaming = True
            print(f"Camera {self.camera_id} started streaming.")

    def stop_stream(self):
        if self.is_streaming:
            # Logic to stop streaming from the camera
            self.is_streaming = False
            print(f"Camera {self.camera_id} stopped streaming.")

    def capture_frame(self):
        if self.is_streaming:
            # Logic to capture a frame from the camera
            print(f"Capturing frame from camera {self.camera_id}.")
            # Return the captured frame (placeholder)
            return None
        else:
            print(f"Camera {self.camera_id} is not streaming.")

    def get_status(self):
        return {
            "camera_id": self.camera_id,
            "is_streaming": self.is_streaming,
            "stream_url": self.stream_url
        }