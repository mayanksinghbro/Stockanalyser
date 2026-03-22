'use client';

import { useState, useEffect } from 'react';
import { Star, Plus, Trash2, TrendingUp, ChevronRight } from 'lucide-react';

interface WatchlistEntry {
    symbol: string;
    name: string;
    price: number;
    change_pct: number;
    status: string;
}

interface WatchlistProps {
    onSelect: (symbol: string) => void;
    currentTicker: string;
    newEntry?: { symbol: string; name: string; price: number; change_pct?: number; status: string } | null;
}

const STATUS_COLORS: Record<string, string> = {
    'Antigravity Detected': '#f59e0b',
    'Low Gravity': '#10b981',
    'Stable Gravity': '#6b7280',
};

const DEFAULT_WATCHLIST: WatchlistEntry[] = [
    { symbol: 'RELIANCE', name: 'Reliance Industries', price: 0, change_pct: 0, status: '' },
    { symbol: 'TCS', name: 'Tata Consultancy', price: 0, change_pct: 0, status: '' },
    { symbol: 'INFY', name: 'Infosys Limited', price: 0, change_pct: 0, status: '' },
    { symbol: 'HDFCBANK', name: 'HDFC Bank', price: 0, change_pct: 0, status: '' },
];

export default function Watchlist({ onSelect, currentTicker, newEntry }: WatchlistProps) {
    const [list, setList] = useState<WatchlistEntry[]>([]);
    const [addInput, setAddInput] = useState('');
    const [adding, setAdding] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem('nse_watchlist');
        if (stored) {
            setList(JSON.parse(stored));
        } else {
            setList(DEFAULT_WATCHLIST);
            localStorage.setItem('nse_watchlist', JSON.stringify(DEFAULT_WATCHLIST));
        }
    }, []);

    // Whenever a stock is analyzed, update its entry in the list automatically
    useEffect(() => {
        if (!newEntry) return;
        setList((prev) => {
            const exists = prev.find((e) => e.symbol === newEntry.symbol);
            let updated: WatchlistEntry[];
            if (exists) {
                updated = prev.map((e) =>
                    e.symbol === newEntry.symbol
                        ? { ...e, name: newEntry.name, price: newEntry.price, change_pct: newEntry.change_pct ?? 0, status: newEntry.status }
                        : e
                );
            } else {
                updated = [
                    { symbol: newEntry.symbol, name: newEntry.name, price: newEntry.price, change_pct: newEntry.change_pct ?? 0, status: newEntry.status },
                    ...prev,
                ];
            }
            localStorage.setItem('nse_watchlist', JSON.stringify(updated));
            return updated;
        });
    }, [newEntry]);

    const remove = (symbol: string) => {
        const updated = list.filter((e) => e.symbol !== symbol);
        setList(updated);
        localStorage.setItem('nse_watchlist', JSON.stringify(updated));
    };

    const addSymbol = (e: React.FormEvent) => {
        e.preventDefault();
        const sym = addInput.trim().toUpperCase();
        if (!sym || list.find((e) => e.symbol === sym)) { setAddInput(''); setAdding(false); return; }
        const entry: WatchlistEntry = { symbol: sym, name: sym, price: 0, change_pct: 0, status: '' };
        const updated = [entry, ...list];
        setList(updated);
        localStorage.setItem('nse_watchlist', JSON.stringify(updated));
        setAddInput('');
        setAdding(false);
        // Auto-analyze it
        onSelect(sym);
    };

    return (
        <aside style={{
            width: '260px', flexShrink: 0,
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: '20px',
            padding: '20px 16px',
            display: 'flex', flexDirection: 'column', gap: '12px',
            height: 'fit-content',
            position: 'sticky', top: '24px'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '1rem' }}>
                    <Star size={16} color="#f59e0b" fill="#f59e0b" />
                    Watchlist
                </div>
                <button
                    onClick={() => setAdding(true)}
                    title="Add symbol"
                    style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', padding: '4px 8px', cursor: 'pointer', color: '#818cf8', display: 'flex', alignItems: 'center' }}
                >
                    <Plus size={16} />
                </button>
            </div>

            {adding && (
                <form onSubmit={addSymbol} style={{ display: 'flex', gap: '6px' }}>
                    <input
                        autoFocus
                        value={addInput}
                        onChange={(e) => setAddInput(e.target.value)}
                        placeholder="NSE Symbol"
                        style={{
                            flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.15)',
                            padding: '6px 10px', borderRadius: '8px', color: 'white', fontSize: '0.85rem', outline: 'none'
                        }}
                    />
                    <button type="submit" style={{ background: '#6366f1', border: 'none', borderRadius: '8px', padding: '6px 10px', color: 'white', cursor: 'pointer', fontSize: '0.85rem' }}>+</button>
                </form>
            )}

            {list.length === 0 && (
                <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: '0.85rem', textAlign: 'center', padding: '20px 0' }}>
                    No stocks yet. Add one!
                </div>
            )}

            {list.map((entry) => {
                const isActive = entry.symbol === currentTicker;
                const statusColor = STATUS_COLORS[entry.status] || 'rgba(255,255,255,0.3)';
                return (
                    <div
                        key={entry.symbol}
                        onClick={() => onSelect(entry.symbol)}
                        style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            padding: '10px 12px', borderRadius: '12px', cursor: 'pointer',
                            background: isActive ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.03)',
                            border: isActive ? '1px solid rgba(99,102,241,0.4)' : '1px solid transparent',
                            transition: 'all 0.15s ease'
                        }}
                        onMouseEnter={(e) => !isActive && ((e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.06)')}
                        onMouseLeave={(e) => !isActive && ((e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.03)')}
                    >
                        <div style={{ minWidth: 0 }}>
                            <div style={{ fontWeight: 700, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                {entry.symbol}
                                {entry.status && (
                                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: statusColor, display: 'inline-block', flexShrink: 0 }} title={entry.status} />
                                )}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '130px' }}>{entry.name}</div>
                            {entry.price > 0 && (
                                <div style={{ fontSize: '0.8rem', marginTop: '2px', color: entry.change_pct >= 0 ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                                    ₹{entry.price.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                                    {' '}
                                    <span style={{ fontSize: '0.72rem' }}>{entry.change_pct >= 0 ? '▲' : '▼'}{Math.abs(entry.change_pct).toFixed(1)}%</span>
                                </div>
                            )}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                            <button
                                onClick={(ev) => { ev.stopPropagation(); remove(entry.symbol); }}
                                style={{ background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.2)', cursor: 'pointer', padding: '2px' }}
                                title="Remove"
                            >
                                <Trash2 size={13} />
                            </button>
                            <ChevronRight size={14} style={{ color: 'rgba(255,255,255,0.2)' }} />
                        </div>
                    </div>
                );
            })}
        </aside>
    );
}
