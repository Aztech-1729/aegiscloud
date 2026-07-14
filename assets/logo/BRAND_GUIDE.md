# Aegis Cloud Brand Guide

## Logo Files Created

### Primary Logo Files
- **`aegis-cloud-logo-primary.svg`** - Main logo with text (vector, scalable)
- **`aegis-cloud-logo-primary.png`** - Main logo with text (raster, 400x120px)
- **`aegis-cloud-logo-dark.svg`** - Dark mode variant (vector)
- **`aegis-cloud-logo-dark.png`** - Dark mode variant (raster)

### Icon-Only Variants
- **`aegis-cloud-icon-only.svg`** - Shield icon without text (vector)
- **`aegis-cloud-icon-only.png`** - Shield icon without text (raster)

### Favicon
- **`favicon.svg`** - Scalable vector favicon (modern browsers)
- **`favicon.png`** - Raster favicon (legacy browser support)

---

## Brand Colors

### Primary Gradient
```css
/* Main brand gradient */
background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);

/* Indigo */
#aegis-indigo-500: #6366F1
#aegis-indigo-600: #4F46E5
#aegis-indigo-700: #4338CA

/* Violet */
#aegis-violet-500: #8B5CF6
#aegis-violet-600: #7C3AED
#aegis-violet-700: #6D28D9
```

### Secondary Colors
```css
/* Cyan (network/cloud) */
#aegis-cyan-400: #22D3EE
#aegis-cyan-500: #06B6D4

/* Slate (text) */
#aegis-slate-900: #0F172A (dark background)
#aegis-slate-800: #1E1B4B (headings)
#aegis-slate-600: #475569 (body text)
#aegis-slate-400: #94A3B8 (muted text)
```

---

## Logo Usage Guidelines

### ✅ DO
- Use the SVG version whenever possible (infinitely scalable)
- Maintain minimum clear space around the logo (equal to shield height)
- Use dark version on dark backgrounds
- Use light version on light backgrounds
- Keep the logo proportional (don't stretch)

### ❌ DON'T
- Don't change the gradient colors
- Don't rotate or skew the logo
- Don't add drop shadows or effects
- Don't place on busy backgrounds without contrast
- Don't use smaller than 32px height

---

## Integration Instructions

### Website Integration

#### HTML (Add to `<head>`)
```html
<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/assets/logo/favicon.svg">
<link rel="icon" type="image/png" href="/assets/logo/favicon.png">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" href="/assets/logo/aegis-cloud-icon-only.png">

<!-- Open Graph / Social Media -->
<meta property="og:image" content="https://aegiscloud.in/assets/logo/aegis-cloud-logo-primary.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">

<!-- Twitter Card -->
<meta name="twitter:image" content="https://aegiscloud.in/assets/logo/aegis-cloud-logo-primary.png">
```

#### Next.js Integration
```jsx
// In app/layout.tsx
import Image from 'next/image'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" type="image/svg+xml" href="/assets/logo/favicon.svg" />
        <link rel="icon" type="image/png" href="/assets/logo/favicon.png" />
        <link rel="apple-touch-icon" href="/assets/logo/aegis-cloud-icon-only.png" />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}
```

#### Navbar Logo Component
```jsx
// In components/layout/Navbar.tsx
import Image from 'next/image'

export function Navbar() {
  return (
    <nav>
      <Image
        src="/assets/logo/aegis-cloud-logo-primary.svg"
        alt="Aegis Cloud"
        width={150}
        height={45}
        priority
      />
    </nav>
  )
}
```

---

## File Structure

```
assets/
└── logo/
    ├── aegis-cloud-logo-primary.svg      # Main logo (vector)
    ├── aegis-cloud-logo-primary.png      # Main logo (raster)
    ├── aegis-cloud-logo-dark.svg         # Dark mode (vector)
    ├── aegis-cloud-logo-dark.png         # Dark mode (raster)
    ├── aegis-cloud-icon-only.svg         # Icon only (vector)
    ├── aegis-cloud-icon-only.png         # Icon only (raster)
    ├── favicon.svg                       # Favicon (vector)
    ├── favicon.png                       # Favicon (raster)
    └── BRAND_GUIDE.md                    # This file
```

---

## Design Elements

### Shield Symbolism
- **Protection**: Aegis means shield/protection in Greek mythology
- **Security**: Represents enterprise-grade security
- **Trust**: Conveys reliability and safety

### Network Nodes
- **Connectivity**: Represents endpoint management
- **AI Intelligence**: Connected nodes symbolize AI processing
- **Scalability**: Multiple nodes show ability to manage many devices

### Cloud Element
- **Cloud Computing**: Modern infrastructure
- **Remote Access**: Cloud-based management
- **Scalability**: Elastic resources

### Color Psychology
- **Indigo/Violet**: Innovation, technology, premium quality
- **Cyan**: Trust, reliability, clarity
- **Gradient**: Modern, dynamic, forward-thinking

---

## Responsive Logo Usage

### Large Screens (>1200px)
Use full logo with text: `aegis-cloud-logo-primary.svg`

### Medium Screens (768-1200px)
Use full logo with text: `aegis-cloud-logo-primary.svg`

### Small Screens (<768px)
Use icon only: `aegis-cloud-icon-only.svg`

### Mobile Navigation
Use icon only: `aegis-cloud-icon-only.svg`

---

## Export Specifications

### PNG Versions
- **Primary Logo**: 400x120px @ 2x (800x240 actual)
- **Icon Only**: 200x220px @ 2x (400x440 actual)
- **Favicon**: 64x64px @ 2x (128x128 actual)

### SVG Versions
- Infinitely scalable
- File size: ~1-2KB each
- Perfect for web use

---

## Social Media Profile Images

### Recommended Sizes
- **Twitter/X**: 400x400px (use icon-only)
- **LinkedIn**: 400x400px (use icon-only)
- **GitHub**: 400x400px (use icon-only)
- **Product Hunt**: 640x640px (use icon-only)
- **Discord**: 512x512px (use icon-only)

### Cover/Banner Images
- **Twitter Header**: 1500x500px
- **LinkedIn Banner**: 1584x396px
- **Facebook Cover**: 820x312px

---

## Email Signature

```html
<table>
  <tr>
    <td>
      <img src="https://aegiscloud.in/assets/logo/aegis-cloud-logo-primary.png" 
           alt="Aegis Cloud" 
           width="150" 
           style="display:block;">
    </td>
  </tr>
  <tr>
    <td style="font-family: Arial, sans-serif; font-size: 12px; color: #64748B;">
      <strong>Your Name</strong><br>
      Your Title<br>
      <a href="https://aegiscloud.in" style="color: #4F46E5;">aegiscloud.in</a>
    </td>
  </tr>
</table>
```

---

## Favicon Implementation

### Modern Browsers (SVG)
```html
<link rel="icon" type="image/svg+xml" href="/assets/logo/favicon.svg">
```

### Legacy Browsers (PNG)
```html
<link rel="icon" type="image/png" sizes="32x32" href="/assets/logo/favicon.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/logo/favicon.png">
```

### Apple Devices
```html
<link rel="apple-touch-icon" href="/assets/logo/aegis-cloud-icon-only.png">
```

### Windows Tiles
```html
<meta name="msapplication-TileImage" content="/assets/logo/aegis-cloud-icon-only.png">
<meta name="msapplication-TileColor" content="#4F46E5">
```

---

## Printing Guidelines

### Minimum Size
- **With text**: 1 inch (25mm) wide minimum
- **Icon only**: 0.5 inch (12mm) wide minimum

### Print Colors
Use CMYK equivalents:
- Indigo: C:71 M:72 Y:0 K:0
- Violet: C:54 M:77 Y:0 K:0
- Cyan: C:71 M:0 Y:0 K:0

---

## Brand Voice & Messaging

### Tagline Options
1. "AI Endpoint Management" (technical)
2. "Manage Windows. Everywhere." (benefit-focused)
3. "Your Devices. Your Control." (empowerment)
4. "AI-Powered Windows Management" (descriptive)

### Elevator Pitch
"Aegis Cloud is an AI-powered endpoint management platform that lets you securely manage Windows devices from anywhere. Think TeamViewer meets ChatGPT meets Microsoft Intune—all controlled through natural language."

---

## Need More Variants?

If you need additional logo variants (horizontal, stacked, monochrome, etc.), let me know and I'll generate them.

---

**Brand created: July 13, 2026**  
**Brand version: 1.0**  
**Next review: 6 months**
