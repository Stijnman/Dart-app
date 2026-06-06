import cv2
import numpy as np

class PerspectiveCalibrator:
    """
    Transforms skewed camera coordinates of a dartboard into a normalized 2D system.
    Matches standard OpenCV homography matrices.
    """
    def __init__(self, target_radius_px: int = 400):
        self.target_radius = target_radius_px
        self.homography_matrix = None

    def compute_calibration(self, src_points: np.ndarray):
        """
        Accepts 4 coordinate points mapping to standard boundaries: 
        North (Double 20), East (Double 6), South (Double 3), West (Double 11).
        """
        if len(src_points) != 4:
            raise ValueError("Exactly four perspective source points are required.")

        d = self.target_radius
        dst_points = np.float32([
            [d, d - 300],  # Sector 20 Peak
            [d + 300, d],  # Sector 6 Outer Boundary
            [d, d + 300],  # Sector 3 Lowest Point
            [d - 300, d]   # Sector 11 Outer Boundary
        ])
        
        self.homography_matrix, _ = cv2.findHomography(np.float32(src_points), dst_points)

    def map_coordinate(self, cam_x: float, cam_y: float) -> tuple:
        if self.homography_matrix is None:
            raise ValueError("Calibration homography matrix is not calculated.")
            
        point = np.array([[[cam_x, cam_y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.homography_matrix)
        return float(transformed[0][0][0]), float(transformed[0][0][1])
