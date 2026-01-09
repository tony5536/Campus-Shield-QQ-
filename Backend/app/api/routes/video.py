"""
Video streaming endpoint for CampusShield AI demo.
Provides a simulated live camera feed with AI detection overlay.
"""

import asyncio
import io
import time
from typing import AsyncGenerator
import base64
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Mock cv2 to prevent NameError in VideoStreamSimulator
    class MockCV2:
        FONT_HERSHEY_SIMPLEX = 1
        IMWRITE_JPEG_QUALITY = 1
        
        @staticmethod
        def putText(*args, **kwargs): pass
        
        @staticmethod
        def rectangle(*args, **kwargs): pass
        
        @staticmethod
        def imencode(ext, img, params=None):
            # Return a simple blank JPEG-like byte sequence or try using PIL
            try:
                from PIL import Image
                import io
                # Convert numpy array to PIL Image
                # Handle BGR to RGB if needed (assuming RGB for simplicity here)
                pil_img = Image.fromarray(img)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG")
                return True, buf.getvalue()
            except ImportError:
                # Absolute fallback - return 1x1 empty jpeg bytes
                return True, b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xbf\xff\xd9'

    cv2 = MockCV2()

from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class VideoStreamSimulator:
    """Simulates a live video feed with AI detections."""
    
    def __init__(self):
        self.frame_count = 0
        self.fps = settings.video_stream_fps or 30
        self.resolution = self._parse_resolution(settings.video_stream_resolution or "1280x720")
        self.detection_probability = 0.3  # 30% chance of detection per frame
        self.enabled = settings.enable_video_stream
    
    def _parse_resolution(self, res_str: str):
        """Parse resolution string like '1280x720' to tuple (width, height)."""
        try:
            parts = res_str.split('x')
            return (int(parts[0]), int(parts[1]))
        except:
            return (1280, 720)
    
    def _generate_frame(self) -> np.ndarray:
        """Generate a synthetic frame with optional detections."""
        width, height = self.resolution
        
        # Create a frame with gradient background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient effect (simulate camera lighting)
        for i in range(height):
            frame[i, :] = [30 + int(i * 50 / height), 50, 80]
        
        # Add timestamp
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add location label
        cv2.putText(frame, "Campus Building A - Entrance", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Randomly add detections
        import random
        if random.random() < self.detection_probability:
            self._add_detection_box(frame)
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {self.frame_count}", (width - 300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Add AI status
        cv2.putText(frame, "AI: ACTIVE", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        self.frame_count += 1
        return frame
    
    def _add_detection_box(self, frame: np.ndarray):
        """Add a random detection bounding box."""
        height, width = frame.shape[:2]
        
        # Random detection area
        x1 = np.random.randint(50, width - 300)
        y1 = np.random.randint(100, height - 200)
        x2 = x1 + np.random.randint(100, 200)
        y2 = y1 + np.random.randint(100, 200)
        
        # Red bounding box for detection
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # Label
        confidence = np.random.randint(75, 99)
        label = f"Person - {confidence}%"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    async def stream_frames(self) -> AsyncGenerator[bytes, None]:
        """Generator that yields JPEG frames as bytes."""
        if not self.enabled:
            raise RuntimeError("Video streaming is disabled")
        
        frame_delay = 1.0 / self.fps
        
        try:
            while True:
                frame = self._generate_frame()
                
                # Encode frame as JPEG
                success, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not success:
                    logger.warning("Failed to encode frame")
                    continue
                
                # Yield frame in MJPEG format
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-length: ' + str(len(encoded_frame)).encode() + b'\r\n\r\n'
                    + encoded_frame + b'\r\n'
                )
                
                # Sleep to maintain FPS
                await asyncio.sleep(frame_delay)
        
        except asyncio.CancelledError:
            logger.info("Video stream cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in video stream: {e}")
            raise


# Initialize simulator
simulator = VideoStreamSimulator() if CV2_AVAILABLE else None


@router.get("/stream")
async def video_stream():
    """
    Stream live video feed as Motion JPEG (MJPEG).
    
    Returns MJPEG stream that can be displayed with:
    <img src="/api/video/stream" />
    """
    if not CV2_AVAILABLE:
        raise HTTPException(status_code=503, detail="OpenCV not available. Install with: pip install opencv-python")
    
    if not settings.enable_video_stream:
        raise HTTPException(status_code=503, detail="Video streaming is disabled (ENABLE_VIDEO_STREAM=false)")
    
    if simulator is None:
        raise HTTPException(status_code=503, detail="Video simulator not initialized")
    
    try:
        return StreamingResponse(
            simulator.stream_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
    except Exception as e:
        logger.error(f"Error starting video stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start video stream: {str(e)}")


@router.get("/health")
async def video_health():
    """Check video streaming service health."""
    return {
        "status": "ok" if settings.enable_video_stream else "disabled",
        "streaming_enabled": settings.enable_video_stream,
        "opencv_available": CV2_AVAILABLE,
        "fps": settings.video_stream_fps,
        "resolution": settings.video_stream_resolution,
    }


@router.post("/trigger-incident")
async def trigger_incident(body: dict = None):
    """
    Trigger a fake incident from video analysis (demo feature).
    Frontend can call this when user clicks "Report Incident" on video feed.
    """
    try:
        incident_data = {
            "incident_type": "video_detection",
            "description": body.get("description", "Automated detection from video feed") if body else "Automated detection from video feed",
            "severity": body.get("severity", 0.7) if body else 0.7,
            "source": "video_stream",
            "location": body.get("location", "Building A Entrance") if body else "Building A Entrance",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Video-triggered incident: {incident_data}")
        
        return {
            "status": "created",
            "incident": incident_data,
            "message": "Incident created from video detection"
        }
    except Exception as e:
        logger.error(f"Error triggering incident: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating incident: {str(e)}")
