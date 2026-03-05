import React from 'react';
import { Search, Sparkles, BookOpen } from 'lucide-react';
import './HeroSearch.css';

/**
 * Hero Search Component
 * A visually stunning search bar for initiating a new research query
 */
export default function HeroSearch({ query, setQuery, onSearch, isLoading }) {
    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim() && !isLoading) {
            onSearch(query);
        }
    };

    return (
        <div className="hero-container animate-fade-in">
            <div className="hero-content">
                <div className="hero-badge">
                    <Sparkles size={16} className="text-accent" />
                    <span>AI-Powered Autonomous Research</span>
                </div>

                <h1 className="hero-title">
                    What would you like to <span className="text-gradient">research</span> today?
                </h1>

                <p className="hero-subtitle">
                    Enter any topic and our multi-agent system will gather, analyze, and synthesize
                    information from across the web into a comprehensive report.
                </p>

                <form onSubmit={handleSubmit} className="search-form glass-panel">
                    <div className="search-input-wrapper">
                        <Search className="search-icon" size={24} />
                        <input
                            type="text"
                            className="search-input"
                            placeholder="e.g., The impact of quantum computing on cryptography..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            disabled={isLoading}
                            autoFocus
                        />
                    </div>

                    <button
                        type="submit"
                        className={`search-button ${isLoading ? 'loading' : ''}`}
                        disabled={!query.trim() || isLoading}
                    >
                        {isLoading ? (
                            <span className="spinner"></span>
                        ) : (
                            <>
                                <span>Research</span>
                                <BookOpen size={18} />
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
