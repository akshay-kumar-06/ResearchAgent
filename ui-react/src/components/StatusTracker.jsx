import React, { useEffect, useState } from 'react';
import { Search, Brain, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import './StatusTracker.css';

/**
 * Status Tracker Component
 * Displays the current state of a running research task
 */
export default function StatusTracker({ status, query }) {
    const [progress, setProgress] = useState(15);

    // Stages corresponding to the LangGraph agents
    const stages = [
        { id: 'started', label: 'Initializing Request', icon: Search, threshold: 10 },
        { id: 'planning', label: 'Planning Research Strategy', icon: Brain, threshold: 30 },
        { id: 'searching', label: 'Gathering Information', icon: Search, threshold: 60 },
        { id: 'analyzing', label: 'Synthesizing Data', icon: FileText, threshold: 85 },
        { id: 'writing', label: 'Formatting Final Report', icon: CheckCircle, threshold: 95 },
    ];

    // Simulated progress while "running"
    useEffect(() => {
        let interval;
        if (status === 'started' || status === 'running') {
            interval = setInterval(() => {
                setProgress(prev => {
                    // Slowly increment up to 95% while running
                    if (prev < 95) {
                        return prev + Math.random() * 2;
                    }
                    return prev;
                });
            }, 1000);
        } else if (status === 'complete') {
            setProgress(100);
        }

        return () => clearInterval(interval);
    }, [status]);

    const getCurrentStageIndex = () => {
        if (status === 'complete') return stages.length - 1;
        if (status === 'error') return -1;

        // Determine visual stage based on progress percentage
        for (let i = stages.length - 1; i >= 0; i--) {
            if (progress >= stages[i].threshold) return i;
        }
        return 0;
    };

    const currentStageIndex = getCurrentStageIndex();

    if (status === 'error') {
        return (
            <div className="status-container error animate-fade-in glass-panel">
                <AlertCircle size={48} className="text-error mb-4" />
                <h3>Research Failed</h3>
                <p>There was an error processing your query: "{query}"</p>
                <p className="error-hint">Please try a different query or check your backend connection.</p>
            </div>
        );
    }

    return (
        <div className="status-container glass-panel animate-fade-in">
            <div className="status-header">
                <h2 className="status-title">Research in Progress</h2>
                <p className="status-query">"{query}"</p>
            </div>

            <div className="progress-bar-container">
                <div
                    className="progress-bar-fill"
                    style={{ width: `${progress}%` }}
                />
            </div>

            <div className="stages-list">
                {stages.map((stage, index) => {
                    const isActive = index === currentStageIndex;
                    const isComplete = index < currentStageIndex || status === 'complete';
                    const isPending = index > currentStageIndex && status !== 'complete';

                    let stateClass = '';
                    if (isActive) stateClass = 'active';
                    if (isComplete) stateClass = 'complete';
                    if (isPending) stateClass = 'pending';

                    const Icon = stage.icon;

                    return (
                        <div key={stage.id} className={`stage-item ${stateClass}`}>
                            <div className="stage-icon-wrapper">
                                {isActive && status !== 'complete' ? (
                                    <span className="spinner small"></span>
                                ) : (
                                    <Icon size={18} />
                                )}
                            </div>
                            <span className="stage-label">{stage.label}</span>
                            {isActive && status !== 'complete' && (
                                <span className="pulsing-dot"></span>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
