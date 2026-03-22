'use client';

import { useState, useCallback } from 'react';
import { Activity, Lock, Unlock, TrendingUp, TrendingDown, Zap, BarChart2, BookMarked, RefreshCw } from 'lucide-react';
import {
    ComposedChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer, Area
} from 'recharts';
import AuthModal from '@/components/AuthModal';
import Watchlist from '@/components/Watchlist';
import SmartSearch from '@/components/SmartSearch';
import { API_BASE_URL } from '@/config';
import './globals.css';

export default function Home() {
    const [ticker, setTicker] = useState('');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [user, setUser] = useState<any>(null);
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [watchlistEntry, setWatchlistEntry] = useState<any>(null);
    const [lastUpdated, setLastUpdated] = useState<string>('');

    const analyze = useCallback(async (sym: string) => {
        const symbol = sym.trim().toUpperCase();
        if (!symbol) return;
        setTicker(symbol);
        setLoading(true);
        setError(null);
        setData(null);

        try {
            const resp = await fetch(`${API_BASE_URL}/api/analyze?ticker=${symbol}`);
            if (!resp.ok) {
                const errJson = await resp.json().catch(() => null);
                throw new Error(errJson?.detail || `Could not find data for "${symbol}". Please check the NSE symbol.`);
            }
            const json = await resp.json();
            setData(json);
            setLastUpdated(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }));
            setWatchlistEntry({
                symbol,
                name: json.company_name,
                price: json.current_price,
                change_pct: json.prediction?.change_pct ?? 0,
                status: json.gravity?.status ?? '',
            });
        } catch (err: any) {
            setError(err.message || 'Failed to analyze. Is the FastAPI backend running on port 8001?');
        } finally {
            setLoading(false);
        }
    }, []);

    const getGravityColor = (status: string) => {
        if (status === 'Antigravity Detected') return 'var(--status-antigravity)';
        if (status === 'Low Gravity') return 'var(--status-bullish)';
        return 'var(--status-neutral)';
    };
    const getGravityGlow = (status: string) => {
        if (status === 'Antigravity Detected') return 'glow-antigravity';
        if (status === 'Low Gravity') return 'glow-bullish';
        return 'glow-neutral';
    };
    const getGravityNeon = (status: string) => {
        if (status === 'Antigravity Detected') return 'text-neon-purple';
        if (status === 'Low Gravity') return 'text-neon-green';
        return 'text-neon-amber';
    };

    const isUp = data?.prediction?.change_pct >= 0;

    // Chart custom tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (!active || !payload?.length) return null;
        return (
            <div style={{
                background: 'rgba(5,6,10,0.97)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '10px', padding: '10px 14px', fontSize: '0.8rem'
            }}>
                <div style={{ color: 'var(--text-tertiary)', marginBottom: '6px' }}>{String(label).substring(0, 10)}</div>
                {payload.map((p: any) => (
                    <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: '20px', color: p.color }}>
                        <span>{p.name}</span>
                        <span style={{ fontWeight: 700 }}>₹{Number(p.value).toLocaleString('en-IN', { maximumFractionDigits: 1 })}</span>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div style={{ minHeight: '100vh' }}>

            {/* ═══ Sticky Header ═══ */}
            <header className="app-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        width: '38px', height: '38px', borderRadius: '10px', flexShrink: 0,
                        background: 'var(--accent-gradient)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 0 20px rgba(99,102,241,0.4)'
                    }}>
                        <Activity size={20} />
                    </div>
                    <div>
                        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.3px' }} className="text-gradient">
                            NSE Antigravity Predictor
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', marginTop: '1px' }}>
                            Real-time ML engine · All NSE listed stocks
                        </div>
                    </div>
                </div>

                <SmartSearch onSelect={analyze} />

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {lastUpdated && (
                        <div style={{ fontSize: '0.76rem', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <RefreshCw size={11} /> Updated {lastUpdated}
                        </div>
                    )}
                    {user ? (
                        <div onClick={() => setUser(null)} title="Click to logout" style={{
                            display: 'flex', alignItems: 'center', gap: '7px',
                            background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)',
                            padding: '7px 14px', borderRadius: '10px', cursor: 'pointer',
                            fontSize: '0.82rem', color: 'var(--status-bullish)'
                        }}>
                            <Unlock size={13} /> {user.email}
                        </div>
                    ) : (
                        <div onClick={() => setIsAuthModalOpen(true)} style={{
                            display: 'flex', alignItems: 'center', gap: '7px',
                            background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
                            padding: '7px 14px', borderRadius: '10px', cursor: 'pointer',
                            fontSize: '0.82rem', color: 'var(--text-secondary)'
                        }}>
                            <Lock size={13} /> Login
                        </div>
                    )}
                </div>
            </header>

            {/* ═══ Body ═══ */}
            <div style={{ display: 'flex', gap: '20px', padding: '24px 28px', alignItems: 'flex-start', maxWidth: '1600px', margin: '0 auto' }}>

                {/* ── Watchlist Sidebar ── */}
                <Watchlist onSelect={analyze} currentTicker={ticker} newEntry={watchlistEntry} />

                {/* ── Main Content ── */}
                <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '20px' }}>

                    {/* Loading */}
                    {loading && (
                        <div className="flex-center" style={{ flexDirection: 'column', gap: '20px', minHeight: '420px' }}>
                            <div style={{
                                width: '56px', height: '56px', borderRadius: '50%',
                                border: '3px solid rgba(99,102,241,0.15)',
                                borderTopColor: '#6366f1',
                                animation: 'spin 0.9s linear infinite'
                            }} />
                            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 600 }} className="text-gradient">
                                Analyzing {ticker} gravitational field…
                            </div>
                            <div style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)' }}>
                                Fetching live NSE data · Running ML models · Computing SHAP
                            </div>
                        </div>
                    )}

                    {/* Error */}
                    {error && !loading && (
                        <div className="glass-card animate-fade-in" style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', borderColor: 'rgba(239,68,68,0.25)' }}>
                            <div style={{ fontSize: '1.5rem' }}>⚠️</div>
                            <div>
                                <div style={{ fontWeight: 600, color: '#ef4444', marginBottom: '4px' }}>Analysis Failed</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{error}</div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginTop: '8px' }}>
                                    Tip: Use official NSE symbols like RELIANCE, TCS, INFY, ZOMATO, HDFCBANK
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ══ Results ══ */}
                    {data && !loading && (
                        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

                            {/* Hero card */}
                            <div className={`glass-card ${getGravityGlow(data.gravity.status)}`} style={{ position: 'relative', overflow: 'hidden' }}>
                                {/* Background accent */}
                                <div style={{
                                    position: 'absolute', top: '-40px', right: '-40px',
                                    width: '200px', height: '200px', borderRadius: '50%',
                                    background: `radial-gradient(circle, ${getGravityColor(data.gravity.status)}18 0%, transparent 70%)`,
                                    pointerEvents: 'none'
                                }} />

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '20px', flexWrap: 'wrap' }}>
                                    {/* Company & Price */}
                                    <div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>
                                            NSE: {data.ticker}
                                        </div>
                                        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 700, marginBottom: '12px', lineHeight: 1.2 }}>
                                            {data.company_name}
                                        </h2>
                                        <div style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '-2px', lineHeight: 1, fontFamily: 'var(--font-display)' }}>
                                            ₹{data.current_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                                        </div>

                                        {/* Stats row */}
                                        <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
                                            <div className="stat-box">
                                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Avg Volume</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{(data.avg_volume / 100000).toFixed(2)}L</div>
                                            </div>
                                            <div className="stat-box">
                                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>ML Model</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{data.prediction.model}</div>
                                            </div>
                                            <div className="stat-box">
                                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Analyzed At</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{new Date(data.analyzed_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Gravity Status */}
                                    <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px' }}>
                                        <div style={{
                                            display: 'inline-flex', alignItems: 'center', gap: '12px',
                                            background: `${getGravityColor(data.gravity.status)}12`,
                                            border: `1.5px solid ${getGravityColor(data.gravity.status)}40`,
                                            padding: '14px 22px', borderRadius: '16px'
                                        }}>
                                            <Zap size={28} color={getGravityColor(data.gravity.status)} />
                                            <div>
                                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>GRAVITY STATE</div>
                                                <div className={`${getGravityNeon(data.gravity.status)}`} style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-display)' }}>
                                                    {data.gravity.status}
                                                </div>
                                            </div>
                                        </div>
                                        <p style={{ maxWidth: '380px', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                                            {data.gravity.explanation}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Chart + Sidebar */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '20px' }}>
                                {/* Price Chart */}
                                <div className="glass-card" style={{ padding: '20px', minHeight: '360px', display: 'flex', flexDirection: 'column' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.95rem' }}>
                                            <BarChart2 size={17} className="text-gradient" /> Price Action &amp; Volatility Bands
                                        </h3>
                                        <div style={{ display: 'flex', gap: '12px', fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '16px', height: '2px', background: '#fff', display: 'inline-block' }} /> Price</span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '16px', height: '2px', background: '#f59e0b', display: 'inline-block' }} /> SMA20</span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '16px', height: '2px', background: '#ef4444', display: 'inline-block', borderTop: '1px dashed' }} /> BB Upper</span>
                                        </div>
                                    </div>
                                    <div style={{ width: '100%', height: '300px' }}>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <ComposedChart data={data.chart_data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
                                                <defs>
                                                    <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                                                <XAxis dataKey="Date" tickFormatter={(t) => String(t).substring(5, 10)} stroke="rgba(255,255,255,0.15)" tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.4)' }} axisLine={false} tickLine={false} />
                                                <YAxis domain={['auto', 'auto']} stroke="rgba(255,255,255,0.15)" tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.4)' }} axisLine={false} tickLine={false} width={65} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                                                <RechartsTooltip content={<CustomTooltip />} />
                                                <Area type="monotone" dataKey="Close" stroke="#6366f1" strokeWidth={0} fill="url(#priceGrad)" name="Price" dot={false} />
                                                <Line type="monotone" dataKey="Close" stroke="#ffffff" strokeWidth={2} dot={false} name="Price" />
                                                <Line type="monotone" dataKey="SMA_20" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="SMA 20" />
                                                <Line type="monotone" dataKey="BB_upper" stroke="#ef4444" strokeWidth={1} strokeDasharray="4 3" dot={false} name="BB Upper" />
                                                <Line type="monotone" dataKey="BB_lower" stroke="#10b981" strokeWidth={1} strokeDasharray="4 3" dot={false} name="BB Lower" />
                                            </ComposedChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                {/* Right column: Forecast + XAI */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

                                    {/* Forecast */}
                                    <div className="glass-card" style={{ padding: '20px' }}>
                                        <h3 style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            {isUp ? <TrendingUp size={16} color="var(--status-bullish)" /> : <TrendingDown size={16} color="var(--status-bearish)" />}
                                            ML Forecast (T+5 Days)
                                        </h3>
                                        <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Powered by {data.prediction.model}</div>
                                        <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-display)', letterSpacing: '-1px', marginBottom: '10px' }}>
                                            ₹{data.prediction.predicted_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                                        </div>
                                        <span className="badge" style={{
                                            background: isUp ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                                            border: `1px solid ${isUp ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                                            color: isUp ? 'var(--status-bullish)' : 'var(--status-bearish)',
                                            fontSize: '0.8rem', padding: '5px 12px'
                                        }}>
                                            {isUp ? '▲ UPSIDE' : '▼ DOWNSIDE'} {Math.abs(data.prediction.change_pct).toFixed(2)}%
                                        </span>

                                        <div style={{ marginTop: '16px' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-tertiary)', marginBottom: '6px' }}>
                                                <span>Current ₹{data.current_price.toFixed(0)}</span>
                                                <span>Target ₹{data.prediction.predicted_price.toFixed(0)}</span>
                                            </div>
                                            <div className="indicator-bar">
                                                <div className="indicator-bar-fill" style={{
                                                    width: `${Math.min(100, Math.max(5, 50 + data.prediction.change_pct * 3))}%`,
                                                    background: isUp ? 'var(--status-bullish)' : 'var(--status-bearish)'
                                                }} />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Sentiment */}
                                    <div className="glass-card" style={{ padding: '20px' }}>
                                        <h3 style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <Activity size={16} color="var(--accent-cyan)" /> News Sentiment
                                        </h3>
                                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px', marginBottom: '12px' }}>
                                            <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'var(--font-display)' }}>
                                                {data.sentiment.label}
                                            </div>
                                            <div style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                                                ({data.sentiment.score > 0 ? '+' : ''}{data.sentiment.score})
                                            </div>
                                        </div>
                                        <div className="indicator-bar" style={{ background: 'rgba(255,255,255,0.04)' }}>
                                            <div className="indicator-bar-fill" style={{
                                                width: `${50 + (data.sentiment.score * 50)}%`,
                                                background: data.sentiment.score > 0 ? 'var(--status-bullish)' : (data.sentiment.score < 0 ? 'var(--status-bearish)' : 'var(--accent-cyan)')
                                            }} />
                                        </div>
                                        <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', marginTop: '8px' }}>
                                            Based on {data.sentiment.count} recent news headlines
                                        </div>
                                    </div>

                                    {/* XAI */}
                                    <div className="glass-card" style={{ padding: '20px', flex: 1, borderColor: 'rgba(139,92,246,0.2)' }}>
                                        <h3 style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '12px', color: 'var(--accent-purple)' }}>
                                            ✦ XAI Signal Drivers
                                        </h3>
                                        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '14px', lineHeight: 1.6 }}>
                                            {data.xai_insights.insight}
                                        </p>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                            {Object.entries(data.xai_insights.feature_importance).map(([k, v]: any, i) => (
                                                <div key={i}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', marginBottom: '5px' }}>
                                                        <span style={{ color: 'var(--text-secondary)' }}>{k.replace(/_/g, ' ')}</span>
                                                        <span style={{ color: 'var(--accent-purple)', fontWeight: 600 }}>{(v * 100).toFixed(0)}%</span>
                                                    </div>
                                                    <div className="indicator-bar">
                                                        <div className="indicator-bar-fill" style={{
                                                            width: `${v * 100}%`,
                                                            background: `linear-gradient(90deg, #6366f1, #8b5cf6)`
                                                        }} />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Tech Grid */}
                                    <div className="glass-card" style={{ padding: '20px', borderColor: 'rgba(255,255,255,0.05)' }}>
                                        <h3 style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '12px' }}>
                                            Technical Health
                                        </h3>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                            <div className="stat-box" style={{ padding: '10px' }}>
                                                <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>RSI (14)</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: data.gravity.metrics.rsi > 70 ? 'var(--status-bearish)' : (data.gravity.metrics.rsi < 30 ? 'var(--status-bullish)' : 'white') }}>
                                                    {data.gravity.metrics.rsi.toFixed(1)}
                                                </div>
                                            </div>
                                            <div className="stat-box" style={{ padding: '10px' }}>
                                                <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>ROC (10)</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: data.gravity.metrics.roc_10 > 0 ? 'var(--status-bullish)' : 'var(--status-bearish)' }}>
                                                    {data.gravity.metrics.roc_10 > 0 ? '+' : ''}{data.gravity.metrics.roc_10.toFixed(2)}%
                                                </div>
                                            </div>
                                            <div className="stat-box" style={{ padding: '10px', gridColumn: 'span 2' }}>
                                                <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Distance to SMA20</div>
                                                <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                                                    {data.gravity.metrics.distance_to_sma20_pct > 0 ? '+' : ''}{data.gravity.metrics.distance_to_sma20_pct.toFixed(2)}%
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Empty state */}
                    {!loading && !error && !data && (
                        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '420px', gap: '24px' }}>
                            <div style={{
                                width: '80px', height: '80px', borderRadius: '24px',
                                background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <BookMarked size={36} color="rgba(99,102,241,0.6)" strokeWidth={1.5} />
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 700, marginBottom: '8px' }}>
                                    Search any Indian Stock
                                </div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-tertiary)', maxWidth: '380px', lineHeight: 1.6 }}>
                                    Type a company name or NSE symbol in the search bar above. All NSE-listed stocks supported with live data.
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center', maxWidth: '560px' }}>
                                {['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ZOMATO', 'ADANIENT', 'WIPRO', 'BAJFINANCE'].map((s) => (
                                    <button key={s} onClick={() => analyze(s)} style={{
                                        background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
                                        color: '#818cf8', padding: '7px 16px', borderRadius: '10px', cursor: 'pointer',
                                        fontSize: '0.85rem', fontWeight: 600, transition: 'all 0.15s',
                                    }}
                                        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(99,102,241,0.18)')}
                                        onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(99,102,241,0.08)')}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                            <div style={{ fontSize: '0.76rem', color: 'var(--text-tertiary)' }}>
                                Or select a stock from your watchlist →
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} onLogin={(email) => setUser({ email })} />
        </div>
    );
}
