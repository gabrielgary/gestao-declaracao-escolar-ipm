import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for data fetching
 * @param {Function} fetchFn - Service function to call (e.g., listRecords)
 * @param {string} url - API endpoint
 * @param {boolean} immediate - Whether to fetch immediately on mount
 */
export default function useFetch(fetchFn, url, immediate = true) {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const execute = useCallback(async (params) => {
        setIsLoading(true);
        setError(null);
        try {
            const finalUrl = params ? `${url}?${new URLSearchParams(params)}` : url;
            const response = await fetchFn(finalUrl);
            setData(response);
            return response;
        } catch (err) {
            setError(err.message || 'Ocorreu um erro ao carregar os dados');
        } finally {
            setIsLoading(false);
        }
    }, [fetchFn, url]);

    useEffect(() => {
        if (immediate) {
            execute();
        }
    }, [immediate, execute]);

    return { data, setData, isLoading, error, refresh: execute };
}
