import React, { useState } from 'react';
import { Menu, X, Clock, FileText, CheckCircle2, ChevronRight, BrainCircuit } from 'lucide-react';
import './Layout.css';

/**
 * Main Layout Component
 * Includes the Sidebar for history and the main content area
 */
export default function Layout({ children, history, onSelectHistory, currentView, setCurrentView }) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'complete': return <CheckCircle2 size={16} className="text-success" />;
            case 'running': return <span className="spinner small"></span>;
            case 'started': return <Clock size={16} className="text-warning" />;
            case 'error': return <X size={16} className="text-error" />;
            default: return <FileText size={16} className="text-muted" />;
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    return (
        <div className="app-layout">
            {/* Mobile Sidebar Overlay */}
            {!isSidebarOpen && (
                <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(true)} />
            )}

            {/* Sidebar */}
            <aside className={`sidebar glass-panel ${isSidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <div className="logo-container" onClick={() => setCurrentView('new')} style={{ cursor: 'pointer' }}>
                        <div className="logo-icon">
                            <BrainCircuit size={24} className="text-accent" />
                        </div>
                        <span className="logo-text">NeuralSearch</span>
                    </div>
                    <button
                        className="icon-btn hide-desktop"
                        onClick={toggleSidebar}
                        aria-label="Close sidebar"
                    >
                        <X size={20} />
                    </button>
                </div>

                <button
                    className="new-chat-btn"
                    onClick={() => setCurrentView('new')}
                >
                    <span className="plus-icon">+</span>
                    New Research
                </button>

                <div className="history-section">
                    <h3 className="section-title">Recent Research</h3>

                    {history.length === 0 ? (
                        <div className="empty-history">
                            <p>No previous research found.</p>
                        </div>
                    ) : (
                        <ul className="history-list">
                            {history.map((item) => (
                                <li key={item.research_id} className="history-item">
                                    <button
                                        className="history-btn"
                                        onClick={() => onSelectHistory(item.research_id)}
                                        title={item.query}
                                    >
                                        {getStatusIcon(item.status)}
                                        <div className="history-item-content">
                                            <span className="history-query">{item.query}</span>
                                            <span className="history-date">{formatDate(item.created_at)}</span>
                                        </div>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <div className="sidebar-footer">
                    <div className="user-profile">
                        <div className="avatar">RS</div>
                        <div className="user-info">
                            <span className="user-name">Researcher</span>
                            <span className="user-role">Pro Account</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className={`main-content ${!isSidebarOpen ? 'expanded' : ''}`}>
                <header className="topbar">
                    <button
                        className="icon-btn toggle-sidebar-btn"
                        onClick={toggleSidebar}
                        aria-label="Toggle sidebar"
                    >
                        <Menu size={24} />
                    </button>

                    <div className="topbar-actions">
                        {/* Add topbar actions here if needed */}
                    </div>
                </header>

                <div className="content-area">
                    {children}
                </div>
            </main>
        </div>
    );
}
