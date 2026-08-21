import os
import sys
import glob
import random
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import torch
from torch.utils.data import Dataset, DataLoader
from src.ner.config import Config


class LandslideSegmentationDataset(Dataset):
    """
    PyTorch Dataset loader for 4-channel satellite image tiles and binary landslide masks.
    Handles data loading, channel normalization, binary label extraction, and spatial augmentations.
    """
    def __init__(self, split_dir, transform=False, seed=Config.SEED):
        super().__init__()
        self.split_dir = split_dir
        self.transform = transform
        self.seed = seed
        
        self.images_dir = os.path.join(split_dir, "images")
        self.masks_dir = os.path.join(split_dir, "masks")
        
        self.image_paths = sorted(glob.glob(os.path.join(self.images_dir, "*.png")))
        self.mask_paths = sorted(glob.glob(os.path.join(self.masks_dir, "*.png")))
        
        if len(self.image_paths) == 0:
            raise FileNotFoundError(f"No image PNG files found in {self.images_dir}")
        if len(self.image_paths) != len(self.mask_paths):
            raise ValueError(f"Mismatch between images ({len(self.image_paths)}) and masks ({len(self.mask_paths)}) in {split_dir}")

    def __len__(self):
        return len(self.image_paths)

    def _apply_augmentations(self, image_np, mask_np):
        """
        Applies spatially sound terrain augmentations (Flips, 90-degree rotations).
        Maintains strict alignment between image and mask.
        """
        # Horizontal Flip
        if random.random() > 0.5:
            image_np = np.fliplr(image_np).copy()
            mask_np = np.fliplr(mask_np).copy()

        # Vertical Flip
        if random.random() > 0.5:
            image_np = np.flipud(image_np).copy()
            mask_np = np.flipud(mask_np).copy()

        # Random 90-degree rotations (0, 1, 2, or 3 times 90 degrees)
        k = random.randint(0, 3)
        if k > 0:
            image_np = np.rot90(image_np, k=k, axes=(0, 1)).copy()
            mask_np = np.rot90(mask_np, k=k, axes=(0, 1)).copy()

        return image_np, mask_np

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        mask_path = self.mask_paths[idx]
        filename = os.path.basename(img_path)
        
        # Load image (128, 128, 4) uint8 RGBA
        image_pil = Image.open(img_path).convert("RGBA")
        image_np = np.array(image_pil, dtype=np.float32) / 255.0  # Scale to [0, 1]
        
        # Load mask (128, 128, 4) uint8
        mask_pil = Image.open(mask_path)
        mask_np = np.array(mask_pil, dtype=np.float32)
        
        # Extract binary mask from first channel (0: background, 255: landslide)
        if mask_np.ndim == 3:
            mask_binary = (mask_np[:, :, 0] > 0.0).astype(np.float32)
        else:
            mask_binary = (mask_np > 0.0).astype(np.float32)

        # Apply augmentation if enabled (training set)
        if self.transform:
            image_np, mask_binary = self.apply_augmentations(image_np, mask_binary)

        # Convert to PyTorch Tensors
        # Image tensor shape: (C, H, W) = (4, 128, 128)
        image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).float()
        
        # Mask tensor shape: (1, H, W) = (1, 128, 128)
        mask_tensor = torch.from_numpy(mask_binary).unsqueeze(0).float()
        
        return image_tensor, mask_tensor, filename

    def apply_augmentations(self, image_np, mask_np):
        return self._apply_augmentations(image_np, mask_np)


def get_dataloader(split_dir, batch_size=Config.BATCH_SIZE, shuffle=False, transform=False, num_workers=Config.NUM_WORKERS):
    dataset = LandslideSegmentationDataset(split_dir=split_dir, transform=transform)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    return loader
