import { useState, useEffect } from 'react'
import axios from 'axios'

interface JobResponse {
  job_id: string
  message: string
  domains_count: number
  recipients_count: number
}

interface JobStatus {
  job_id: string
  status: string
  progress: number
  domains_count: number
  results_count: number
  started_at: string
  completed_at: string | null
  error: string | null
}

interface EmailConfigResponse {
  recipients: string[]
  count: number
}

function App() {
  const [currentView, setCurrentView] = useState<'scanner' | 'settings'>('scanner')
  const [domains, setDomains] = useState('')
  const [customEmails, setCustomEmails] = useState('')
  const [useConfiguredEmails, setUseConfiguredEmails] = useState(true)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [configuredEmails, setConfiguredEmails] = useState<string[]>([])
  const [newEmail, setNewEmail] = useState('')
  const [settingsLoading, setSettingsLoading] = useState(false)
  const [settingsMessage, setSettingsMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

  useEffect(() => {
    loadEmailConfig()
  }, [])

  const loadEmailConfig = async () => {
    try {
      const response = await axios.get<EmailConfigResponse>(`${API_BASE}/api/email-config`)
      setConfiguredEmails(response.data.recipients)
    } catch (err) {
      console.error('Error loading email config:', err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)
    setJobStatus(null)

    try {
      const response = await axios.post<JobResponse>(`${API_BASE}/api/analyze`, {
        domains,
        emails: customEmails,
        use_configured_emails: useConfiguredEmails,
      })

      setJobId(response.data.job_id)
      setSuccess(response.data.message)
      
      startPolling(response.data.job_id)
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred. Please try again.')
      setLoading(false)
    }
  }

  const startPolling = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get<JobStatus>(`${API_BASE}/api/status/${id}`)
        setJobStatus(response.data)

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval)
          setLoading(false)
        }
      } catch (err) {
        console.error('Error polling status:', err)
      }
    }, 2000)
  }

  const handleAddEmail = async () => {
    if (!newEmail.trim()) return
    
    setSettingsLoading(true)
    setSettingsMessage(null)
    
    try {
      await axios.post(`${API_BASE}/api/email-config/add`, { email: newEmail })
      setNewEmail('')
      await loadEmailConfig()
      setSettingsMessage({ type: 'success', text: 'Email added successfully' })
    } catch (err: any) {
      setSettingsMessage({ type: 'error', text: err.response?.data?.error || 'Failed to add email' })
    } finally {
      setSettingsLoading(false)
    }
  }

  const handleRemoveEmail = async (email: string) => {
    setSettingsLoading(true)
    setSettingsMessage(null)
    
    try {
      await axios.post(`${API_BASE}/api/email-config/remove`, { email })
      await loadEmailConfig()
      setSettingsMessage({ type: 'success', text: 'Email removed successfully' })
    } catch (err: any) {
      setSettingsMessage({ type: 'error', text: err.response?.data?.error || 'Failed to remove email' })
    } finally {
      setSettingsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="flex border-b">
            <button
              onClick={() => setCurrentView('scanner')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-colors ${
                currentView === 'scanner'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              🔍 Scanner
            </button>
            <button
              onClick={() => setCurrentView('settings')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-colors ${
                currentView === 'settings'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              ⚙️ Email Settings
            </button>
          </div>

          {currentView === 'scanner' ? (
            <div className="p-8">
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">
                  🔒 Wayback Security Scanner
                </h1>
                <p className="text-gray-600">
                  Automated security analysis of archived web pages
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="domains" className="block text-sm font-medium text-gray-700 mb-2">
                    Domain(s) to Analyze
                  </label>
                  <textarea
                    id="domains"
                    value={domains}
                    onChange={(e) => setDomains(e.target.value)}
                    placeholder="expertzone.microsoft.com&#10;example.com&#10;or comma-separated: domain1.com, domain2.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    rows={4}
                    required
                    disabled={loading}
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Enter one domain per line or comma-separated
                  </p>
                </div>

                <div className="border rounded-lg p-4 bg-gray-50">
                  <label className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      checked={useConfiguredEmails}
                      onChange={(e) => setUseConfiguredEmails(e.target.checked)}
                      className="w-4 h-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                      disabled={loading}
                    />
                    <span className="ml-2 text-sm font-medium text-gray-700">
                      Send to configured emails ({configuredEmails.length})
                    </span>
                  </label>
                  
                  {configuredEmails.length > 0 && useConfiguredEmails && (
                    <div className="mb-3 p-3 bg-white rounded border">
                      <p className="text-xs text-gray-600 mb-2">Configured recipients:</p>
                      <div className="flex flex-wrap gap-2">
                        {configuredEmails.map((email, idx) => (
                          <span key={idx} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                            {email}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <label htmlFor="customEmails" className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Email(s) (Optional)
                    </label>
                    <textarea
                      id="customEmails"
                      value={customEmails}
                      onChange={(e) => setCustomEmails(e.target.value)}
                      placeholder="custom@example.com&#10;another@example.com&#10;or comma-separated"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                      rows={3}
                      disabled={loading}
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      Add extra recipients for this scan only
                    </p>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-3 px-6 rounded-lg text-white font-semibold text-lg transition-all duration-200 ${
                    loading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 transform hover:scale-105'
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    '🚀 Start Analysis'
                  )}
                </button>
              </form>

              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">⚠️</span>
                    <div>
                      <h3 className="text-red-800 font-semibold">Error</h3>
                      <p className="text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {success && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">✅</span>
                    <div>
                      <h3 className="text-green-800 font-semibold">Analysis Started</h3>
                      <p className="text-green-700">{success}</p>
                      {jobId && (
                        <p className="text-sm text-green-600 mt-1">Job ID: {jobId}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {jobStatus && (
                <div className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="text-blue-900 font-semibold mb-4 flex items-center">
                    <span className="text-2xl mr-2">📊</span>
                    Analysis Progress
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-blue-800">Status:</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        jobStatus.status === 'completed' ? 'bg-green-200 text-green-800' :
                        jobStatus.status === 'failed' ? 'bg-red-200 text-red-800' :
                        'bg-yellow-200 text-yellow-800'
                      }`}>
                        {jobStatus.status.toUpperCase()}
                      </span>
                    </div>

                    {jobStatus.status === 'processing' && (
                      <div>
                        <div className="flex justify-between text-sm text-blue-700 mb-1">
                          <span>Progress</span>
                          <span>{jobStatus.progress}%</span>
                        </div>
                        <div className="w-full bg-blue-200 rounded-full h-3">
                          <div
                            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                            style={{ width: `${jobStatus.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div>
                        <p className="text-sm text-blue-600">Domains</p>
                        <p className="text-2xl font-bold text-blue-900">{jobStatus.domains_count}</p>
                      </div>
                      <div>
                        <p className="text-sm text-blue-600">Findings</p>
                        <p className="text-2xl font-bold text-blue-900">{jobStatus.results_count}</p>
                      </div>
                    </div>

                    {jobStatus.completed_at && (
                      <div className="pt-3 border-t border-blue-200">
                        <p className="text-sm text-blue-700">
                          ✉️ Results have been sent to configured email(s)
                        </p>
                      </div>
                    )}

                    {jobStatus.error && (
                      <div className="pt-3 border-t border-red-300 bg-red-50 -mx-6 -mb-6 px-6 py-3 rounded-b-lg">
                        <p className="text-sm text-red-700">
                          <strong>Error:</strong> {jobStatus.error}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-8 p-6 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-3">🔍 What We Analyze:</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Retrieves all archived URLs from Wayback Machine</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Identifies suspicious files (.js, .json, .config, .env, etc.)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Detects API keys, tokens, secrets, passwords, and credentials</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Scans for AWS keys, JWT tokens, database URLs, and more</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Sends detailed HTML report to configured email(s)</span>
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="p-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-2">
                  📧 Email Configuration
                </h2>
                <p className="text-gray-600">
                  Manage default recipients for scan results
                </p>
              </div>

              {settingsMessage && (
                <div className={`mb-6 p-4 rounded-lg border ${
                  settingsMessage.type === 'success' 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : 'bg-red-50 border-red-200 text-red-800'
                }`}>
                  {settingsMessage.text}
                </div>
              )}

              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Add New Recipient
                </label>
                <div className="flex gap-3">
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="email@example.com"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={settingsLoading}
                  />
                  <button
                    onClick={handleAddEmail}
                    disabled={settingsLoading || !newEmail.trim()}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Configured Recipients ({configuredEmails.length})
                </h3>
                
                {configuredEmails.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg">
                    <p className="text-gray-500">No recipients configured yet</p>
                    <p className="text-sm text-gray-400 mt-2">Add an email above to get started</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {configuredEmails.map((email, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">📧</span>
                          <span className="font-medium text-gray-800">{email}</span>
                        </div>
                        <button
                          onClick={() => handleRemoveEmail(email)}
                          disabled={settingsLoading}
                          className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">ℹ️ How It Works</h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Configure default recipients here to automatically receive all scan results</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>You can add additional one-time recipients in the Scanner tab</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>All configured emails will receive detailed HTML reports</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Email configuration is stored persistently on the server</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>

        <div className="text-center mt-6 text-white text-sm">
          <p>Built with security in mind | Powered by Wayback Machine CDX API</p>
        </div>
      </div>
    </div>
  )
}

export default App
