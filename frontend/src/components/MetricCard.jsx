import React from 'react';

const MetricCard = ({ title, value, icon: Icon, trend, trendValue }) => {
    return (
        <div className="glass-card flex-center" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '20px' }}>
            <div className="flex-between" style={{ width: '100%', marginBottom: '16px' }}>
                <span className="text-secondary" style={{ fontSize: '1rem', fontWeight: 500 }}>{title}</span>
                {Icon && <Icon className="text-tertiary" size={20} />}
            </div>

            <div style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '8px' }}>
                {value}
            </div>

            {trend && trendValue && (
                <div style={{
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    color: trend === 'up' ? 'var(--status-bullish)' : (trend === 'down' ? 'var(--status-bearish)' : 'var(--text-secondary)')
                }}>
                    {trend === 'up' ? '▲' : (trend === 'down' ? '▼' : '▬')} {trendValue}
                </div>
            )}
        </div>
    );
};

export default MetricCard;
