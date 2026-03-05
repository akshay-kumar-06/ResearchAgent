import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import HeroSearch from './components/HeroSearch';
import StatusTracker from './components/StatusTracker';
import ReportViewer from './components/ReportViewer';
import { api } from './services/api';

function App() {
  const [currentView, setCurrentView] = useState('new'); // 'new', 'status', 'report'
  const [query, setQuery] = useState('');
  const [activeResearchId, setActiveResearchId] = useState(null);
  const [researchStatus, setResearchStatus] = useState(null);
  const [researchResult, setResearchResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Poll for status when research is active
  useEffect(() => {
    let pollInterval;

    const checkStatus = async () => {
      if (!activeResearchId || researchStatus === 'complete' || researchStatus === 'error') {
        return;
      }

      try {
        const statusData = await api.checkStatus(activeResearchId);
        setResearchStatus(statusData.status);

        if (statusData.status === 'complete') {
          fetchResult(activeResearchId);
          fetchHistory(); // Refresh history
        } else if (statusData.status === 'error') {
          setError(statusData.error_message || 'Research failed');
        }
      } catch (err) {
        console.error('Failed to check status:', err);
      }
    };

    if (activeResearchId && researchStatus !== 'complete' && researchStatus !== 'error') {
      pollInterval = setInterval(checkStatus, 2000);
    }

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [activeResearchId, researchStatus]);

  const fetchHistory = async () => {
    try {
      const historyData = await api.getHistory();
      setHistory(historyData);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const fetchResult = async (id) => {
    try {
      const resultData = await api.getResult(id);
      setResearchResult(resultData);
      setCurrentView('report');
    } catch (err) {
      console.error('Failed to fetch result:', err);
      setError('Failed to load research report');
      setResearchStatus('error');
    }
  };

  const handleStartSearch = async (searchQuery) => {
    setIsLoading(true);
    setError(null);
    setQuery(searchQuery);

    try {
      const response = await api.startResearch(searchQuery);
      setActiveResearchId(response.research_id);
      setResearchStatus('started');
      setCurrentView('status');
      fetchHistory(); // Optimistic update for the sidebar
    } catch (err) {
      setError('Failed to start research. Make sure the backend is running.');
      setResearchStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistory = async (id) => {
    const item = history.find(h => h.research_id === id);
    if (!item) return;

    setQuery(item.query);
    setActiveResearchId(id);

    if (item.status === 'complete') {
      setResearchStatus('complete');
      fetchResult(id);
    } else {
      setResearchStatus(item.status);
      setCurrentView('status');
    }
  };

  const resetToNew = () => {
    setCurrentView('new');
    setQuery('');
    setActiveResearchId(null);
    setResearchStatus(null);
    setResearchResult(null);
    setError(null);
  };

  return (
    <Layout
      history={history}
      onSelectHistory={handleSelectHistory}
      currentView={currentView}
      setCurrentView={(view) => {
        if (view === 'new') resetToNew();
      }}
    >
      <div className="content-wrapper">
        {currentView === 'new' && (
          <HeroSearch
            query={query}
            setQuery={setQuery}
            onSearch={handleStartSearch}
            isLoading={isLoading}
          />
        )}

        {currentView === 'status' && (
          <StatusTracker
            status={error ? 'error' : researchStatus}
            query={query}
          />
        )}

        {currentView === 'report' && researchResult && (
          <ReportViewer
            result={researchResult}
            onNewSearch={resetToNew}
          />
        )}
      </div>
    </Layout>
  );
}

export default App;
