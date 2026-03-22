import { useState } from 'react'
import { Search, Activity, DollarSign, BarChart2, TrendingUp, Layers } from 'lucide-react'
import './App.css'

import MetricCard from './components/MetricCard'
import SentimentGauge from './components/SentimentGauge'
import PredictionCard from './components/PredictionCard'
import NewsList from './components/NewsList'

function App() {
  const [ticker, setTicker] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    const symbol = searchQuery.trim().toUpperCase();
    setTicker(symbol);
    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetch(`http://localhost:8000/api/predict?ticker=${symbol}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const jsonData = await response.json();
      setData(jsonData);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch data. Ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container animate-fade-in">
      {/* Header Section */}
      <header className="flex-between" style={{ marginBottom: '40px' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Activity className="text-gradient" size={36} />
            <span className="text-gradient">Nova Predictor</span>
          </h1>
          <p className="text-secondary" style={{ marginTop: '8px', fontSize: '1.1rem' }}>
            AI-Powered Market Intelligence
          </p>
        </div>

        <form onSubmit={handleSearch} className="search-input-wrapper">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            className="search-input"
            placeholder="Search ticker (e.g. AAPL, TSLA)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </header>

      {isLoading && (
        <div className="flex-center animate-fade-in" style={{ height: '400px', flexDirection: 'column', gap: '16px' }}>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: '50%',
            border: '3px solid rgba(255,255,255,0.1)',
            borderTopColor: 'var(--accent-blue)',
            animation: 'spin 1s linear infinite'
          }} />
          <div className="text-gradient" style={{ fontSize: '1.2rem', fontWeight: 600 }}>Analyzing {ticker}...</div>
          <style dangerouslySetInnerHTML={{
            __html: `
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          `}} />
        </div>
      )}

      {error && !isLoading && (
        <div className="glass-card animate-fade-in flex-center" style={{ minHeight: '100px', color: 'var(--status-bearish)' }}>
          {error}
        </div>
      )}

      {!isLoading && !error && data && (
        <div className="dashboard-grid animate-fade-in">
          {/* Top Metrics Row */}
          <div className="col-span-3">
            <MetricCard
              title="Current Price"
              value={`$${data.currentPrice.toFixed(2)}`}
              icon={DollarSign}
              trend={data.ensemble?.change_pct >= 0 ? 'up' : 'down'}
              trendValue={`${Math.abs(data.ensemble?.change_pct || 0).toFixed(2)}% expected`}
            />
          </div>
          <div className="col-span-3">
            <MetricCard title="52-Week High" value={`$${data.high52.toFixed(2)}`} icon={TrendingUp} />
          </div>
          <div className="col-span-3">
            <MetricCard title="Avg Volume" value={`${(data.avgVolume / 1000000).toFixed(1)}M`} icon={BarChart2} />
          </div>
          <div className="col-span-3">
            <MetricCard title="Models Active" value="2 / 2" icon={Layers} trend="up" trendValue="Online" />
          </div>

          {/* Main Dashboard Area */}
          <div className="col-span-8" style={{ minHeight: '400px' }}>
            <PredictionCard ensemble={data.ensemble} rf={data.rf} lstm={data.lstm} />
          </div>

          <div className="col-span-4" style={{ minHeight: '400px' }}>
            <SentimentGauge score={data.sentiment} />
          </div>

          <div className="col-span-12" style={{ minHeight: '300px' }}>
            <NewsList articles={data.articles} />
          </div>
        </div>
      )}

      {!isLoading && !error && !data && (
        <div className="flex-center animate-fade-in" style={{ minHeight: '400px', color: 'var(--text-tertiary)', flexDirection: 'column', gap: '16px' }}>
          <Search size={48} />
          <p style={{ fontSize: '1.2rem' }}>Enter a ticker symbol to start analysis</p>
        </div>
      )}
    </div>
  )
}

export default App
