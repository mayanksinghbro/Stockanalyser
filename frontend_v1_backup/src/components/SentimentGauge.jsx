import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const SentimentGauge = ({ score }) => {
    // Score is between -1 and 1
    // We'll normalize it to 0-100 for display
    const normalizedScore = ((score + 1) / 2) * 100;

    const data = [
        { name: 'Score', value: normalizedScore },
        { name: 'Remaining', value: 100 - normalizedScore }
    ];

    let color = 'var(--status-neutral)';
    let label = 'Neutral';
    if (score > 0.2) {
        color = 'var(--status-bullish)';
        label = 'Bullish 📈';
    } else if (score < -0.2) {
        color = 'var(--status-bearish)';
        label = 'Bearish 📉';
    }

    return (
        <div className="glass-card flex-center" style={{ flexDirection: 'column', height: '100%', position: 'relative' }}>
            <h3 style={{ position: 'absolute', top: '24px', left: '24px' }}>Market Mood</h3>

            <div style={{ width: '100%', height: '180px', marginTop: '32px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="100%"
                            startAngle={180}
                            endAngle={0}
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={0}
                            dataKey="value"
                            stroke="none"
                            cornerRadius={5}
                        >
                            <Cell fill={color} />
                            <Cell fill="var(--card-border)" />
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
            </div>

            <div style={{ textAlign: 'center', marginTop: '-40px' }}>
                <div style={{ fontSize: '2rem', fontWeight: 800, color }}>
                    {score > 0 ? '+' : ''}{(score).toFixed(3)}
                </div>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                    {label}
                </div>
            </div>
        </div>
    );
};

export default SentimentGauge;
