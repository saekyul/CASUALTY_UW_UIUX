import React, { useState } from 'react';
import { queryData } from '../services/api';

interface QueryResult {
  status: string;
  sql_query: string;
  results: any[];
  error?: string;
}

export const Data: React.FC = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExecuteQuery = async () => {
    if (!query.trim()) {
      setError('쿼리를 입력해주세요');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await queryData(query);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handleClearQuery = () => {
    setQuery('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">데이터 분석</h1>

      {/* 쿼리 입력 */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">자연어 쿼리</h2>
        <p className="text-gray-600 text-sm mb-4">
          자연어로 데이터베이스에서 원하는 정보를 쿼리할 수 있습니다. LLM이 자동으로 SQL 쿼리로 변환합니다.
        </p>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="예: '지난 30일간 작성된 모든 작업을 보여줘' 또는 '사용자 목록을 이메일 별로 정렬해서 보여줘'"
          className="w-full h-24 p-4 border rounded focus:outline-none focus:border-blue-500"
        />

        <div className="flex gap-2 mt-4">
          <button
            onClick={handleExecuteQuery}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '실행 중...' : '쿼리 실행'}
          </button>
          <button
            onClick={handleClearQuery}
            className="bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700"
          >
            초기화
          </button>
        </div>

        {error && <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded text-red-700">{error}</div>}
      </div>

      {/* 결과 표시 */}
      {result && (
        <div className="space-y-6">
          {/* SQL 쿼리 */}
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <h3 className="font-semibold mb-2">생성된 SQL 쿼리</h3>
            <pre className="bg-gray-900 text-green-400 p-4 rounded overflow-x-auto text-sm font-mono">
              {result.sql_query}
            </pre>
          </div>

          {/* 결과 */}
          {result.status === 'success' && result.results.length > 0 ? (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold mb-4">쿼리 결과 ({result.results.length}행)</h3>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="bg-gray-100 border-b">
                      {Object.keys(result.results[0]).map((key) => (
                        <th key={key} className="px-4 py-2 text-left font-semibold">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.results.map((row, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50">
                        {Object.values(row).map((value: any, idx) => (
                          <td key={idx} className="px-4 py-2">
                            {value !== null ? String(value) : '(null)'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
              <p className="text-yellow-800">
                {result.error || '조건에 맞는 데이터가 없습니다'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* 예시 */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mt-6">
        <h3 className="font-semibold mb-3">쿼리 예시</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• 모든 사용자 목록을 보여줘</li>
          <li>• 처리 상태가 pending인 작업들을 보여줘</li>
          <li>• 가장 최근 10개의 이메일을 보여줘</li>
          <li>• 우선순위가 높은 작업들을 마감일 순서로 보여줘</li>
        </ul>
      </div>
    </div>
  );
};

export default Data;
