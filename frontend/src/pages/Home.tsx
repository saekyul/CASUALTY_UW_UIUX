import React, { useEffect, useState } from 'react';
import { fetchStatus } from '../services/api';

interface StatusData {
  status: string;
  database_connected: boolean;
  claude_api_available: boolean;
  gemini_api_available: boolean;
  outlook_configured: boolean;
}

export const Home: React.FC = () => {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getStatus = async () => {
      try {
        const data = await fetchStatus();
        setStatus(data);
      } catch (error) {
        console.error('Failed to fetch status:', error);
      } finally {
        setLoading(false);
      }
    };

    getStatus();
  }, []);

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">LLM Data Integration PoC</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">시스템 상태</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>전체 상태:</span>
              <span className={`font-semibold ${
                status?.status === 'healthy' ? 'text-green-600' : 'text-yellow-600'
              }`}>
                {status?.status === 'healthy' ? '정상' : '제한'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>데이터베이스:</span>
              <span className={status?.database_connected ? 'text-green-600' : 'text-red-600'}>
                {status?.database_connected ? '연결됨' : '미연결'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Claude API:</span>
              <span className={status?.claude_api_available ? 'text-green-600' : 'text-red-600'}>
                {status?.claude_api_available ? '사용 가능' : '미설정'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Gemini API:</span>
              <span className={status?.gemini_api_available ? 'text-green-600' : 'text-red-600'}>
                {status?.gemini_api_available ? '사용 가능' : '미설정'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Outlook:</span>
              <span className={status?.outlook_configured ? 'text-green-600' : 'text-red-600'}>
                {status?.outlook_configured ? '설정됨' : '미설정'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">주요 기능</h2>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start">
              <span className="mr-2">📧</span>
              <span>이메일 요약 및 분석</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">🎯</span>
              <span>액션 아이템 자동 추출</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">🤖</span>
              <span>자동 응답 생성</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">🔄</span>
              <span>자연어 SQL 변환</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">📊</span>
              <span>데이터 분석 및 시각화</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
        <h2 className="text-lg font-semibold mb-3">시작하기</h2>
        <p className="text-gray-700 mb-4">
          좌측 네비게이션 메뉴를 사용하여 다음 기능들을 이용할 수 있습니다:
        </p>
        <ul className="space-y-2 text-gray-700">
          <li><strong>이메일:</strong> Outlook 이메일 목록 보기 및 요약 생성</li>
          <li><strong>데이터:</strong> 자연어로 데이터베이스 쿼리하기</li>
          <li><strong>설정:</strong> API 키 및 설정 관리</li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
