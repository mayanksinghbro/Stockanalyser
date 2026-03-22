import React from 'react';
import { BrainCircuit, TrendingUp, TrendingDown } from 'lucide-react';

const PredictionCard = ({ ensemble, rf, lstm }) => {
    if (!ensemble && !rf && !lstm) {
        return (
            <div className="glass-card flex-center" style={{ height: '100%' }}>
                <span className="text-secondary">No AI prediction available.</span>
            </div>
        );
    }

    const best = ensemble || rf || lstm;
    const isUp = best.change_pct >= 0;

    return (
        <div className="glass-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BrainCircuit className="text-gradient" size={24} />
                AI Forecast (T+1)
            </h3>

            <div className="flex-center" style={{ flexDirection: 'column', flex: 1 }}>
                <div className="text-secondary" style={{ marginBottom: '8px', fontSize: '1.2rem' }}>
                    Expected Close
                </div>
                <div style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '16px' }}>
                    ${best.predicted_price.toFixed(2)}
                </div>

                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    borderRadius: '24px',
                    background: isUp ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: isUp ? 'var(--status-bullish)' : 'var(--status-bearish)',
                    fontWeight: 600,
                    fontSize: '1.2rem'
                }}>
                    {isUp ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                    {isUp ? 'UPSIDE' : 'DOWNSIDE'} {Math.abs(best.change_pct).toFixed(2)}%
                </div>
            </div>

            <div style={{
                marginTop: '24px',
                paddingTop: '20px',
                borderTop: '1px solid var(--card-border)',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px'
            }}>
                {rf && (
                    <div>
                        <div className="text-tertiary" style={{ fontSize: '0.9rem', marginBottom: '4px' }}>RandomForest</div>
                        <div style={{ fontWeight: 600 }}>${rf.predicted_price.toFixed(2)}</div>
                    </div>
                )}
                {lstm && (
                    <div>
                        <div className="text-tertiary" style={{ fontSize: '0.9rem', marginBottom: '4px' }}>LSTM Network</div>
                        <div style={{ fontWeight: 600 }}>${lstm.predicted_price.toFixed(2)}</div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PredictionCard;
