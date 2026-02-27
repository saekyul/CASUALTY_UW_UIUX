import { useState, useEffect } from 'react';
import { getEmails } from '../services/api';

interface Email {
  id: number;
  sender: string;
  subject: string;
  received_at: string;
  is_processed: boolean;
}

export const useEmailData = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEmails();
      setEmails(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch emails');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  return { emails, loading, error, refetch: fetchEmails };
};
