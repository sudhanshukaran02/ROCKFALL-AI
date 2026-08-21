import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    """(Convolution => BatchNorm => ReLU) * 2"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # Pad x1 if shapes mismatch slightly
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]
        if diffY != 0 or diffX != 0:
            x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    """
    Lightweight 4-Channel U-Net Architecture for Landslide Segmentation.
    Specifically designed for 128x128 4-channel (RGBA/Multispectral) remote sensing inputs.
    """
    def __init__(self, in_channels=4, num_classes=1, feature_scale=32):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        
        f = feature_scale  # 32 channels base
        
        self.inc = DoubleConv(in_channels, f)        # (B, f, 128, 128)
        self.down1 = Down(f, f * 2)                  # (B, f*2, 64, 64)
        self.down2 = Down(f * 2, f * 4)              # (B, f*4, 32, 32)
        self.down3 = Down(f * 4, f * 8)              # (B, f*8, 16, 16)
        self.down4 = Down(f * 8, f * 16)             # Bottleneck: (B, f*16, 8, 8)
        
        self.up1 = Up(f * 16, f * 8)                 # (B, f*8, 16, 16)
        self.up2 = Up(f * 8, f * 4)                  # (B, f*4, 32, 32)
        self.up3 = Up(f * 4, f * 2)                  # (B, f*2, 64, 64)
        self.up4 = Up(f * 2, f)                      # (B, f, 128, 128)
        self.outc = OutConv(f, num_classes)          # (B, num_classes, 128, 128)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


if __name__ == "__main__":
    model = UNet(in_channels=4, num_classes=1)
    dummy_input = torch.randn(2, 4, 128, 128)
    output = model(dummy_input)
    print(f"U-Net Input shape: {dummy_input.shape}")
    print(f"U-Net Output shape: {output.shape}")
    print(f"Total model parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
