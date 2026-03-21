import React from 'react';
import { Newspaper } from 'lucide-react';

const NewsList = ({ articles }) => {
    return (
        <div className="glass-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Newspaper className="text-gradient" size={24} />
                Latest Market News
            </h3>

            {(!articles || articles.length === 0) ? (
                <div className="flex-center" style={{ flex: 1, color: 'var(--text-tertiary)' }}>
                    No recent news found.
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto', paddingRight: '12px' }}>
                    {articles.map((article, idx) => (
                        <div key={idx} style={{
                            padding: '16px',
                            background: 'rgba(255, 255, 255, 0.03)',
                            borderRadius: '12px',
                            border: '1px solid rgba(255, 255, 255, 0.05)',
                            transition: 'background 0.2s ease',
                            cursor: 'pointer'
                        }}
                            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)'}
                            onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'}
                        >
                            <div style={{ fontSize: '1.05rem', fontWeight: 500, marginBottom: '8px', lineHeight: 1.4 }}>
                                {article.title}
                            </div>
                            <div className="flex-between" style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                                <span>{article.source}</span>
                                <span>{new Date(article.published).toLocaleDateString()}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default NewsList;
