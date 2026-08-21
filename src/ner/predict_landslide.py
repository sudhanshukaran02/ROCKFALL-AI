import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import torch

from src.ner.config import Config
from src.ner.unet import UNet


class LandslidePredictor:
    """
    Inference Engine for Spatial Landslide Segmentation using trained U-Net.
    Accepts 4-channel satellite image tile or path and returns binary mask, probability map, and area estimates.
    """
    def __init__(self, checkpoint_path=Config.MODEL_CHECKPOINT_PATH, device=None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")
            
        self.model = UNet(in_channels=Config.IN_CHANNELS, num_classes=Config.NUM_CLASSES).to(self.device)
        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.eval()

    @torch.no_grad()
    def predict(self, image_input, threshold=0.5, pixel_resolution_m=10.0):
        """
        Predicts landslide segmentation mask for a 4-channel image tile.
        
        Args:
            image_input: File path (str) or NumPy array of shape (H, W, 4) or PIL Image.
            threshold: Probability threshold for binary classification (default 0.5).
            pixel_resolution_m: Pixel spatial resolution in meters (default 10m = 100m^2/pixel).
            
        Returns:
            dict containing:
                - 'probability_map': (128, 128) float array [0, 1]
                - 'binary_mask': (128, 128) uint8 array [0, 1]
                - 'landslide_pixel_count': int
                - 'landslide_area_m2': float
                - 'landslide_coverage_pct': float
        """
        if isinstance(image_input, str):
            image_pil = Image.open(image_input).convert("RGBA")
            image_np = np.array(image_pil, dtype=np.float32) / 255.0
        elif isinstance(image_input, Image.Image):
            image_np = np.array(image_input.convert("RGBA"), dtype=np.float32) / 255.0
        elif isinstance(image_input, np.ndarray):
            if image_input.dtype == np.uint8:
                image_np = image_input.astype(np.float32) / 255.0
            else:
                image_np = image_input.astype(np.float32)
        else:
            raise TypeError("Unsupported image_input type.")

        if image_np.ndim == 3 and image_np.shape[2] == 4:
            pass
        elif image_np.ndim == 3 and image_np.shape[2] == 3:
            # Add synthetic 4th channel if only RGB is provided
            alpha = np.ones((image_np.shape[0], image_np.shape[1], 1), dtype=np.float32)
            image_np = np.concatenate([image_np, alpha], axis=2)
        else:
            raise ValueError(f"Invalid image array shape: {image_np.shape}")

        # Convert to tensor (1, 4, H, W)
        tensor = torch.from_numpy(image_np).permute(2, 0, 1).unsqueeze(0).float().to(self.device)
        
        logits = self.model(tensor)
        probs = torch.sigmoid(logits).cpu().numpy().squeeze()
        mask = (probs >= threshold).astype(np.uint8)
        
        landslide_pixels = int(np.sum(mask))
        total_pixels = mask.size
        coverage_pct = (landslide_pixels / total_pixels) * 100.0
        area_m2 = landslide_pixels * (pixel_resolution_m ** 2)
        
        return {
            "probability_map": probs,
            "binary_mask": mask,
            "landslide_pixel_count": landslide_pixels,
            "landslide_area_m2": area_m2,
            "landslide_coverage_pct": coverage_pct
        }


if __name__ == "__main__":
    import glob
    test_file = glob.glob("data/dataset/test/images/*.png")[0]
    predictor = LandslidePredictor()
    result = predictor.predict(test_file)
    print("Sample Inference Result:")
    print(f"File: {test_file}")
    print(f"Landslide Pixels: {result['landslide_pixel_count']}")
    print(f"Landslide Area: {result['landslide_area_m2']:.2f} m^2")
    print(f"Coverage: {result['landslide_coverage_pct']:.2f}%")
