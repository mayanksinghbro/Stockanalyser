'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, TrendingUp, X } from 'lucide-react';
import { API_BASE_URL } from '@/config';

interface SearchResult {
    symbol: string;
    name: string;
}

interface SmartSearchProps {
    onSelect: (symbol: string) => void;
    defaultValue?: string;
}

export default function SmartSearch({ onSelect, defaultValue = '' }: SmartSearchProps) {
    const [query, setQuery] = useState(defaultValue);
    const [results, setResults] = useState<SearchResult[]>([]);
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [highlighted, setHighlighted] = useState(0);
    const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fetchSuggestions = useCallback(async (q: string) => {
        if (!q || q.length < 1) { setResults([]); setOpen(false); return; }
        setLoading(true);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(q)}&limit=8`);
            if (resp.ok) {
                const data = await resp.json();
                setResults(data.results || []);
                setOpen(true);
            }
        } catch { /* ignore network errors */ }
        setLoading(false);
    }, []);

    useEffect(() => {
        if (debounce.current) clearTimeout(debounce.current);
        debounce.current = setTimeout(() => fetchSuggestions(query), 200);
        return () => { if (debounce.current) clearTimeout(debounce.current); };
    }, [query, fetchSuggestions]);

    // Close on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node) && inputRef.current && !inputRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const select = (sym: string) => {
        setQuery(sym);
        setOpen(false);
        onSelect(sym);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!open) return;
        if (e.key === 'ArrowDown') { setHighlighted((h) => Math.min(h + 1, results.length - 1)); e.preventDefault(); }
        if (e.key === 'ArrowUp') { setHighlighted((h) => Math.max(h - 1, 0)); e.preventDefault(); }
        if (e.key === 'Enter') { if (results[highlighted]) select(results[highlighted].symbol); else if (query.trim()) { setOpen(false); onSelect(query.trim().toUpperCase()); } }
        if (e.key === 'Escape') setOpen(false);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setOpen(false);
        if (query.trim()) onSelect(query.trim().toUpperCase());
    };

    return (
        <div style={{ position: 'relative', width: '340px' }}>
            <form onSubmit={handleSubmit}>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                    {loading ? (
                        <div style={{
                            position: 'absolute', left: '14px',
                            width: '16px', height: '16px',
                            borderRadius: '50%',
                            border: '2px solid rgba(255,255,255,0.1)',
                            borderTopColor: '#6366f1',
                            animation: 'spin 0.8s linear infinite',
                            flexShrink: 0
                        }} />
                    ) : (
                        <Search size={16} style={{ position: 'absolute', left: '14px', color: '#64748b', flexShrink: 0 }} />
                    )}
                    <input
                        ref={inputRef}
                        type="text"
                        placeholder="Search stocks, companies…"
                        value={query}
                        onChange={(e) => { setQuery(e.target.value); setHighlighted(0); }}
                        onFocus={() => { if (results.length > 0) setOpen(true); }}
                        onKeyDown={handleKeyDown}
                        autoComplete="off"
                        style={{
                            width: '100%',
                            background: 'rgba(255,255,255,0.06)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            padding: '10px 36px 10px 40px',
                            borderRadius: '12px',
                            color: 'white',
                            outline: 'none',
                            fontSize: '0.92rem',
                            transition: 'border-color 0.2s, background 0.2s',
                        }}
                        onFocusCapture={(e) => { e.target.style.borderColor = 'rgba(99,102,241,0.6)'; e.target.style.background = 'rgba(255,255,255,0.08)'; }}
                        onBlurCapture={(e) => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; e.target.style.background = 'rgba(255,255,255,0.06)'; }}
                    />
                    {query && (
                        <button type="button" onClick={() => { setQuery(''); setResults([]); setOpen(false); inputRef.current?.focus(); }}
                            style={{ position: 'absolute', right: '10px', background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', padding: '2px' }}>
                            <X size={14} />
                        </button>
                    )}
                </div>
            </form>

            {/* Dropdown */}
            {open && results.length > 0 && (
                <div
                    ref={dropdownRef}
                    style={{
                        position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0, zIndex: 999,
                        background: 'rgba(10, 12, 20, 0.98)',
                        border: '1px solid rgba(255,255,255,0.12)',
                        borderRadius: '14px',
                        overflow: 'hidden',
                        boxShadow: '0 16px 48px rgba(0,0,0,0.8)',
                        backdropFilter: 'blur(20px)',
                    }}
                >
                    {results.map((r, i) => (
                        <div
                            key={r.symbol}
                            onMouseDown={() => select(r.symbol)}
                            onMouseEnter={() => setHighlighted(i)}
                            style={{
                                display: 'flex', alignItems: 'center', gap: '12px',
                                padding: '10px 16px',
                                background: i === highlighted ? 'rgba(99,102,241,0.15)' : 'transparent',
                                cursor: 'pointer',
                                borderBottom: i < results.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
                                transition: 'background 0.1s',
                            }}
                        >
                            <div style={{
                                width: '32px', height: '32px', borderRadius: '8px', flexShrink: 0,
                                background: 'rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <TrendingUp size={15} color="#818cf8" />
                            </div>
                            <div style={{ minWidth: 0, flex: 1 }}>
                                <div style={{ fontWeight: 700, fontSize: '0.88rem', letterSpacing: '0.5px' }}>{r.symbol}</div>
                                <div style={{ fontSize: '0.76rem', color: 'rgba(255,255,255,0.4)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.name}</div>
                            </div>
                            <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.2)', flexShrink: 0 }}>.NS</div>
                        </div>
                    ))}
                    <div style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.02)', fontSize: '0.72rem', color: 'rgba(255,255,255,0.25)', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                        ↑↓ Navigate · Enter to analyze · Esc to close · {results.length} results for "{query}"
                    </div>
                </div>
            )}
        </div>
    );
}
