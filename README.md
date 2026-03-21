# NSE Antigravity Predictor 🚀

A real-time, high-performance stock market prediction engine for the National Stock Exchange (NSE) using Next.js, FastAPI, and Advanced ML.

![Dashboard Preview](https://raw.githubusercontent.com/mayanksinghbro/Stockanalyser/main/frontend_next/public/preview.png)

## 🌐 Live Deployment

You can deploy this application to the cloud in minutes:

### 1. Backend (FastAPI)
Deploy the backend first to get your API URL.
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mayanksinghbro/Stockanalyser)

*Note: The backend is located in the `/backend` directory. Render will automatically detect the `render.yaml` blueprint.*

### 2. Frontend (Next.js)
Deploy the frontend and point it to your backend URL.
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fmayanksinghbro%2FStockanalyser&root-directory=frontend_next&env=NEXT_PUBLIC_API_URL)

---

## ✨ Features
- **Real-time Data**: Fetches live NSE equity data and YFinance prices.
- **Smart Search**: Typeahead search for 2,000+ Indian stocks.
- **ML Predictions**: Prophet-based price forecasting with confidence intervals.
- **XAI (Explainable AI)**: Understand the "why" behind every prediction.
- **News Sentiment**: VADER-powered sentiment scoring of live financial news.
- **Premium UI**: Glassmorphism design with Inter & Space Grotesk typography.

## 🛠️ Local Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python api.py` (Runs on http://localhost:8001)

### Frontend
1. `cd frontend_next`
2. `npm install`
3. `npm run dev` (Runs on http://localhost:3000)

## 📄 License
MIT
