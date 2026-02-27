import React, { useState } from 'react';
import { useEmailData } from '../hooks/useEmailData';
import { summarizeEmail, getEmailActions } from '../services/api';

export const Emails: React.FC = () => {
  const { emails, loading, error, refetch } = useEmailData();
  const [selectedEmail, setSelectedEmail] = useState<number | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [processing, setProcessing] = useState(false);

  const handleSummarize = async (emailId: number) => {
    setProcessing(true);
    try {
      const result = await summarizeEmail(emailId);
      setSummary(result.summary_text);
    } catch (error) {
      console.error('Failed to summarize:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleExtractActions = async (emailId: number) => {
    setProcessing(true);
    try {
      const result = await getEmailActions(emailId);
      setActions(result.action_items || []);
    } catch (error) {
      console.error('Failed to extract actions:', error);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return <div className="p-8">이메일 로드 중...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">오류: {error}</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">이메일</h1>
        <button
          onClick={refetch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          새로고침
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 이메일 목록 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="font-semibold">이메일 목록</h2>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {emails.length === 0 ? (
                <div className="p-4 text-gray-500">이메일이 없습니다</div>
              ) : (
                emails.map((email) => (
                  <div
                    key={email.id}
                    onClick={() => {
                      setSelectedEmail(email.id);
                      setSummary(null);
                      setActions([]);
                    }}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                      selectedEmail === email.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="text-sm font-semibold truncate">{email.sender}</div>
                    <div className="text-sm text-gray-600 truncate">{email.subject}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {new Date(email.received_at).toLocaleString('ko-KR')}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 상세 보기 */}
        <div className="lg:col-span-2">
          {selectedEmail ? (
            <div className="space-y-4">
              {/* 처리 버튼 */}
              <div className="bg-white p-4 rounded-lg shadow flex gap-2">
                <button
                  onClick={() => handleSummarize(selectedEmail)}
                  disabled={processing}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {processing ? '처리 중...' : '요약 생성'}
                </button>
                <button
                  onClick={() => handleExtractActions(selectedEmail)}
                  disabled={processing}
                  className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
                >
                  {processing ? '처리 중...' : '액션 추출'}
                </button>
              </div>

              {/* 요약 */}
              {summary && (
                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold mb-2">요약</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{summary}</p>
                </div>
              )}

              {/* 액션 아이템 */}
              {actions.length > 0 && (
                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold mb-3">추출된 액션</h3>
                  <div className="space-y-2">
                    {actions.map((action) => (
                      <div key={action.id} className="border-l-4 border-blue-500 pl-4 py-2">
                        <div className="font-semibold text-sm">{action.action_text}</div>
                        <div className="text-xs text-gray-600">
                          우선순위: <span className="font-semibold">{action.priority}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
              이메일을 선택해주세요
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Emails;
