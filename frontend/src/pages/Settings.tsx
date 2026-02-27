import React, { useState } from 'react';

interface Settings {
  llmModel: string;
  enableOutlookSync: boolean;
  enableAutoSummarize: boolean;
  enableActionExtraction: boolean;
  enableAutoResponse: boolean;
}

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    llmModel: localStorage.getItem('llmModel') || 'claude',
    enableOutlookSync: localStorage.getItem('enableOutlookSync') !== 'false',
    enableAutoSummarize: localStorage.getItem('enableAutoSummarize') !== 'false',
    enableActionExtraction: localStorage.getItem('enableActionExtraction') !== 'false',
    enableAutoResponse: localStorage.getItem('enableAutoResponse') !== 'false',
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (key: keyof Settings, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSaveSettings = () => {
    localStorage.setItem('llmModel', settings.llmModel);
    localStorage.setItem('enableOutlookSync', String(settings.enableOutlookSync));
    localStorage.setItem('enableAutoSummarize', String(settings.enableAutoSummarize));
    localStorage.setItem('enableActionExtraction', String(settings.enableActionExtraction));
    localStorage.setItem('enableAutoResponse', String(settings.enableAutoResponse));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">설정</h1>

      {saved && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded text-green-700">
          ✓ 설정이 저장되었습니다
        </div>
      )}

      <div className="space-y-6">
        {/* LLM 모델 선택 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">LLM 설정</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">선호하는 LLM 모델</label>
              <select
                value={settings.llmModel}
                onChange={(e) => handleChange('llmModel', e.target.value)}
                className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
              >
                <option value="claude">Claude (Anthropic)</option>
                <option value="gemini">Gemini (Google)</option>
              </select>
              <p className="text-xs text-gray-600 mt-1">
                이 모델이 요약, 액션 추출, 자동 응답 생성 등에 사용됩니다.
              </p>
            </div>
          </div>
        </div>

        {/* 기능 활성화 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">기능 활성화</h2>

          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="outlookSync"
                checked={settings.enableOutlookSync}
                onChange={(e) => handleChange('enableOutlookSync', e.target.checked)}
                className="rounded"
              />
              <label htmlFor="outlookSync" className="ml-3">
                <span className="font-medium">Outlook 동기화</span>
                <p className="text-sm text-gray-600">Microsoft Outlook에서 이메일을 자동으로 동기화</p>
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoSummarize"
                checked={settings.enableAutoSummarize}
                onChange={(e) => handleChange('enableAutoSummarize', e.target.checked)}
                className="rounded"
              />
              <label htmlFor="autoSummarize" className="ml-3">
                <span className="font-medium">자동 요약</span>
                <p className="text-sm text-gray-600">이메일이 도착하면 자동으로 요약 생성</p>
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="actionExtraction"
                checked={settings.enableActionExtraction}
                onChange={(e) => handleChange('enableActionExtraction', e.target.checked)}
                className="rounded"
              />
              <label htmlFor="actionExtraction" className="ml-3">
                <span className="font-medium">액션 추출</span>
                <p className="text-sm text-gray-600">이메일에서 자동으로 할 일 항목 추출</p>
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoResponse"
                checked={settings.enableAutoResponse}
                onChange={(e) => handleChange('enableAutoResponse', e.target.checked)}
                className="rounded"
              />
              <label htmlFor="autoResponse" className="ml-3">
                <span className="font-medium">자동 응답</span>
                <p className="text-sm text-gray-600">이메일에 대한 자동 응답 제안 생성</p>
              </label>
            </div>
          </div>
        </div>

        {/* API 키 정보 */}
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <h2 className="text-lg font-semibold mb-3">API 키 정보</h2>
          <p className="text-gray-700 text-sm mb-3">
            API 키는 환경 변수를 통해 서버에서 관리됩니다.
            백엔드 설정에서 다음 환경 변수를 확인하세요:
          </p>
          <ul className="space-y-2 text-sm font-mono bg-white p-3 rounded">
            <li>• CLAUDE_API_KEY</li>
            <li>• GEMINI_API_KEY</li>
            <li>• OUTLOOK_CLIENT_ID</li>
            <li>• OUTLOOK_CLIENT_SECRET</li>
          </ul>
        </div>

        {/* 저장 버튼 */}
        <button
          onClick={handleSaveSettings}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
        >
          설정 저장
        </button>
      </div>
    </div>
  );
};

export default Settings;
