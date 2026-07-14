# Aegis Cloud Icon Usage Guide

## Overview

Square logo icons optimized for Windows applications, setup executables, and website use.

---

## Icon Files

### Windows Application Icons
Located in: `assets/logo/icons/`

| File | Size | Use Case |
|------|------|----------|
| `aegis-cloud.ico` | Multi-size | **Main Windows application icon** (contains all sizes) |
| `icon-256x256.png` | 256x256 | High-res app icon, app stores |
| `icon-512x512.png` | 512x512 | Ultra high-res, marketing materials |
| `icon-dark-256x256.png` | 256x256 | Dark mode variant |
| `icon-128x128.png` | 128x128 | Medium size applications |
| `icon-64x64.png` | 64x64 | Taskbar, window icons |
| `icon-48x48.png` | 48x48 | Windows Explorer, file associations |
| `icon-32x32.png` | 32x32 | Desktop shortcuts, taskbar |
| `icon-16x16.png` | 16x16 | Title bar, small UI elements |

### Website Icons
Located in: `assets/logo/`

| File | Use Case |
|------|----------|
| `favicon.ico` | **Main website favicon** (browser tab icon) |
| `favicon.svg` | Modern browsers (scalable vector) |
| `favicon.png` | Legacy browsers, social media |

### Square Logo
Located in: `assets/logo/`

| File | Use Case |
|------|----------|
| `aegis-cloud-square-logo.svg` | **Main square logo** (vector, infinitely scalable) |
| `aegis-cloud-square-logo.png` | Raster version (512x512) |

---

## Usage Instructions

### 1. Windows Setup Executable (.exe)

#### For Rust Agent (using `tauri` or similar):
```toml
# In your Cargo.toml or Tauri config
[package.metadata.windows]
icon = "assets/logo/icons/aegis-cloud.ico"
```

#### For Electron/NW.js:
```json
{
  "build": {
    "win": {
      "icon": "assets/logo/icons/icon-256x256.png"
    }
  }
}
```

#### For Inno Setup (Windows installer):
```iss
[Setup]
SetupIconFile=assets\logo\icons\aegis-cloud.ico
UninstallDisplayIcon={app}\aegis-cloud.exe
```

#### For NSIS (Nullsoft Scriptable Install System):
```nsis
!define MUI_ICON "assets\logo\icons\aegis-cloud.ico"
!define MUI_UNICON "assets\logo\icons\aegis-cloud.ico"
```

### 2. Website Integration

#### Favicon (add to `<head>` in Next.js):
```jsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        {/* Modern browsers - SVG */}
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        
        {/* Legacy browsers - ICO */}
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        
        {/* Apple devices */}
        <link rel="apple-touch-icon" href="/icons/icon-180x180.png" />
        
        {/* Android/Chrome */}
        <link rel="icon" type="image/png" sizes="192x192" href="/icons/icon-192x192.png" />
        <link rel="icon" type="image/png" sizes="512x512" href="/icons/icon-512x512.png" />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

#### Next.js Image Component:
```jsx
import Image from 'next/image'
import squareLogo from '@/assets/logo/aegis-cloud-square-logo.png'

export function Logo() {
  return (
    <Image
      src={squareLogo}
      alt="Aegis Cloud"
      width={128}
      height={128}
      priority
    />
  )
}
```

### 3. Mobile App Icons

#### React Native:
```javascript
// Place icons in your app's assets folder
// iOS: AppIcon.appiconset (various sizes)
// Android: mipmap folders (ic_launcher.png)
```

#### Flutter:
```yaml
# pubspec.yaml
flutter_icons:
  image_path: "assets/logo/icons/icon-512x512.png"
  android: true
  ios: true
```

### 4. Social Media & Marketing

| Platform | Size | File |
|----------|------|------|
| Twitter/X Profile | 400x400 | `icon-512x512.png` (resized) |
| LinkedIn Company | 400x400 | `icon-512x512.png` (resized) |
| GitHub Organization | 512x512 | `icon-512x512.png` |
| Discord Server | 512x512 | `icon-512x512.png` |
| Product Hunt | 640x640 | `icon-512x512.png` (resized) |

---

## File Format Details

### ICO File (aegis-cloud.ico)
- **Contains**: 6 sizes (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- **Format**: Windows icon format with alpha transparency
- **Size**: ~100KB
- **Use**: Windows executables, installers, file associations

### PNG Files
- **Format**: 32-bit RGBA (alpha transparency)
- **Compression**: Lossless
- **Quality**: High-resolution, sharp edges
- **Use**: Web, mobile, documentation

### SVG File
- **Format**: Scalable Vector Graphics
- **Size**: ~3KB
- **Quality**: Infinite scalability without loss
- **Use**: Web, documentation, print materials

---

## Design Specifications

### Color Palette
```
Primary Gradient: #4F46E5 → #7C3AED
Network Nodes: #22D3EE (cyan), #A78BFA (purple)
Background: White (light mode), #1E1B4B (dark mode)
```

### Design Elements
- **Shield**: Protection, security, trust
- **Network Nodes**: AI intelligence, connectivity, endpoint management
- **Cloud Shape**: Cloud-based platform, remote access
- **Gradient**: Modern, professional, tech-forward

### Minimum Size
- **Readable**: 16x16 pixels (favicon)
- **Recommended**: 32x32 pixels minimum for clarity
- **Optimal**: 256x256 pixels for best quality

---

## Best Practices

### ✅ DO
- Use ICO format for Windows executables
- Use SVG for web (smaller file size, scalable)
- Keep original source files for future modifications
- Test icons at small sizes (16x16) to ensure readability
- Use dark mode variant for dark themes

### ❌ DON'T
- Don't stretch or distort the icon
- Don't use low-resolution PNGs for large displays
- Don't forget to include all required sizes for mobile apps
- Don't use the rectangular logo for app icons (only square)

---

## Regenerating Icons

If you need to regenerate icons from the source:

```bash
# From 512x512 source
convert aegis-cloud-square-logo.png -resize 16x16 icon-16x16.png
convert aegis-cloud-square-logo.png -resize 32x32 icon-32x32.png
convert aegis-cloud-square-logo.png -resize 48x48 icon-48x48.png
convert aegis-cloud-square-logo.png -resize 64x64 icon-64x64.png
convert aegis-cloud-square-logo.png -resize 128x128 icon-128x128.png
convert aegis-cloud-square-logo.png -resize 256x256 icon-256x256.png

# Combine into ICO
convert icon-16x16.png icon-32x32.png icon-48x48.png \
      icon-64x64.png icon-128x128.png icon-256x256.png \
      aegis-cloud.ico
```

---

## Testing

### Test the ICO file on Windows:
1. Right-click `aegis-cloud.ico`
2. Open with Windows icon viewer
3. Verify all sizes display correctly

### Test favicon in browser:
1. Open your website
2. Check browser tab shows icon
3. Clear cache and reload if needed

---

## Need Different Sizes?

If you need additional sizes not included:

```bash
# Example: Create 192x192 for Android
convert icon-512x512.png -resize 192x192 icon-192x192.png

# Example: Create 180x180 for Apple
convert icon-512x512.png -resize 180x180 icon-180x180.png
```

---

## File Organization

```
assets/
└── logo/
    ├── icons/
    │   ├── aegis-cloud.ico          # Windows app icon (multi-size)
    │   ├── icon-512x512.png         # Source high-res
    │   ├── icon-256x256.png         # Large app icon
    │   ├── icon-128x128.png         # Medium size
    │   ├── icon-64x64.png           # Taskbar
    │   ├── icon-48x48.png           # Explorer
    │   ├── icon-32x32.png           # Desktop
    │   ├── icon-16x16.png           # Title bar
    │   └── icon-dark-256x256.png    # Dark mode
    ├── aegis-cloud-square-logo.svg  # Square logo (vector)
    ├── aegis-cloud-square-logo.png  # Square logo (raster)
    ├── favicon.ico                  # Website favicon
    ├── favicon.svg                  # Modern favicon
    ├── favicon.png                  # Legacy favicon
    └── ICON_USAGE_GUIDE.md          # This file
```

---

## Support

For questions about icon usage or to request additional variants:
- Check the brand guide: `BRAND_GUIDE.md`
- Review logo variants: See other logo files in `assets/logo/`

---

**Created**: July 13, 2026  
**Version**: 1.0  
**Compatible with**: Windows 7+, macOS, Linux, iOS, Android, Web
