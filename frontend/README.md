# PRIMAX AI - React Web App

## 🎨 Beautiful Chat Interface + Repo Dashboard

### Features
- Chat with PRIMAX AI
- Analyze GitHub repositories
- Generate code with AI
- View organization analytics
- **Your artwork here!**

### Quick Start

```bash
# Create Next.js app
npx create-next-app@latest primax-web --typescript --tailwind --app

cd primax-web

# Install dependencies
npm install axios recharts lucide-react

# Start development
npm run dev
```

### Integration

```typescript
// API client
const API_URL = "https://primax-ai.onrender.com/api/v1"
const API_KEY = "your-api-key"

// Chat
const chat = await fetch(`${API_URL}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ message: "Hello PRIMAX!" })
})

// Scan organization
const analysis = await fetch(`${API_URL}/scan-organization`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
  },
  body: JSON.stringify({ org_name: "Bakery-street-project" })
})
```

### Your Artwork

Place images in `public/artwork/`:
- `logo.png` - PRIMAX logo
- `background.jpg` - Hero background
- `avatar.png` - Chat avatar

---

**Watermark:** PRIMAX-AI-BSP-2025
