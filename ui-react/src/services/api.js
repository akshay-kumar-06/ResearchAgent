const API_BASE_URL = 'http://localhost:8000';

export const api = {
    /**
     * Start a new research task
     * @param {string} query The research topic
     * @returns {Promise<{research_id: string, status: string, message: string}>}
     */
    async startResearch(query) {
        const response = await fetch(`${API_BASE_URL}/research`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            throw new Error('Failed to start research');
        }

        return response.json();
    },

    /**
     * Check the status of an ongoing research task
     * @param {string} researchId 
     * @returns {Promise<{research_id: string, status: string, query: string, execution_time?: number, error_message?: string}>}
     */
    async checkStatus(researchId) {
        const response = await fetch(`${API_BASE_URL}/research/${researchId}/status`);

        if (!response.ok) {
            throw new Error('Failed to get research status');
        }

        return response.json();
    },

    /**
     * Get the completed research result
     * @param {string} researchId 
     * @returns {Promise<{research_id: string, query: string, report: string, num_sources: number, execution_time: number}>}
     */
    async getResult(researchId) {
        const response = await fetch(`${API_BASE_URL}/research/${researchId}`);

        if (!response.ok) {
            throw new Error('Failed to get research result');
        }

        return response.json();
    },

    /**
     * Get the history of previous researches
     * @param {number} limit 
     * @returns {Promise<Array<{research_id: string, query: string, status: string, created_at: string}>>}
     */
    async getHistory(limit = 20) {
        const response = await fetch(`${API_BASE_URL}/research?limit=${limit}`);

        if (!response.ok) {
            throw new Error('Failed to get research history');
        }

        return response.json();
    }
};
