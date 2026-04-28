import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_BASE_URL = 'http://localhost:8000'

export default function App() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyze = async () => {
    const value = query.trim()

    if (!value) {
      setError('Please enter a ticker or URL first.')
      return
    }

    setLoading(true)
    setError('')
    setData(null)

    try {
      const params = new URLSearchParams()

      if (value.startsWith('http://') || value.startsWith('https://')) {
        params.set('url', value)
      } else {
        params.set('ticker', value.toUpperCase())
      }

      const response = await fetch(`${API_BASE_URL}/analyze?${params.toString()}`)
      const result = await response.json()

      if (!response.ok || result.error) {
        throw new Error(result.error || 'Analysis failed.')
      }

      setData(result)
    } catch (err) {
      setError(err.message || 'Could not connect to backend.')
    } finally {
      setLoading(false)
    }
  }

  const items = data?.items || []

  const chartData = [
    { name: 'Positive', value: data?.counts?.positive || 0 },
    { name: 'Neutral', value: data?.counts?.neutral || 0 },
    { name: 'Negative', value: data?.counts?.negative || 0 },
  ]

  return (
    <main style={{ minHeight: '100vh', padding: '2rem', fontFamily: 'Inter, sans-serif', background: 'linear-gradient(135deg,#f8fafc,#ecfdf5)' }}>
      <h1>VertexStudy Dashboard</h1>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter ticker or URL"
      />
      <button onClick={analyze}>{loading ? 'Loading...' : 'Analyze'}</button>

      {error && <p>{error}</p>}

      {data && (
        <>
          <h3>{data.overall_sentiment}</h3>
          <p>Score: {data.weighted_score}</p>

          <div style={{ height: 250 }}>
            <ResponsiveContainer>
              <BarChart data={chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#16a34a" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {items.map((item, i) => (
            <div key={i}>
              <p>{item.text}</p>
              <span>{item.label}</span>
            </div>
          ))}
        </>
      )}
    </main>
  )
}
