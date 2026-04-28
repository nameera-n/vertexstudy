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
      setError('Please enter a ticker or article URL first.')
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
      setError(err.message || 'Could not connect to the backend. Make sure FastAPI is running on port 8000.')
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

  const overallSentiment = data?.overall_sentiment || '—'
  const weightedScore = Number(data?.weighted_score || 0).toFixed(3)

  return (
    <main style={{ minHeight: '100vh', padding: '2rem', fontFamily: 'Inter, system-ui, sans-serif', background: 'linear-gradient(135deg, #f8fafc 0%, #ecfdf5 100%)', color: '#111827' }}>
      <div style={{ maxWidth: '1120px', margin: '0 auto' }}>
        <header style={{ marginBottom: '1.5rem' }}>
          <p style={{ margin: 0, color: '#16a34a', fontWeight: 700, fontSize: '0.8rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Financial sentiment analyzer</p>
          <h1 style={{ margin: '0.4rem 0', fontSize: '2.25rem' }}>VertexStudy Dashboard</h1>
          <p style={{ margin: 0, color: '#64748b' }}>Analyze stock headlines or article URLs with FinBERT.</p>
        </header>

        <section style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 0.8fr) minmax(0, 1.5fr)', gap: '1.5rem', alignItems: 'start' }}>
          <aside style={{ background: 'white', padding: '1.25rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
            <h2 style={{ marginTop: 0, fontSize: '1.1rem' }}>Run analysis</h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Enter a ticker like NVDA or paste an article URL.</p>

            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && analyze()}
              placeholder="NVDA or https://..."
              style={{ width: '100%', boxSizing: 'border-box', padding: '0.8rem', borderRadius: '12px', marginBottom: '1rem', border: '1px solid #d1d5db', outline: 'none' }}
            />

            <button
              onClick={analyze}
              disabled={loading}
              style={{ width: '100%', padding: '0.8rem', background: loading ? '#86efac' : '#16a34a', color: 'white', border: 'none', borderRadius: '12px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 700 }}
            >
              {loading ? 'Analyzing...' : 'Analyze sentiment'}
            </button>

            {error && <div style={{ marginTop: '1rem', padding: '0.8rem', borderRadius: '12px', background: '#fef2f2', color: '#991b1b', fontSize: '0.9rem' }}>{error}</div>}
          </aside>

          <section>
            {!data && !loading && <div style={{ background: 'white', padding: '1.5rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)', color: '#64748b' }}>Results will appear here after you run an analysis.</div>}
            {loading && <div style={{ background: 'white', padding: '1.5rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)', color: '#166534', fontWeight: 700 }}>Analyzing with FinBERT...</div>}

            {data && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{ background: 'white', padding: '1rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
                    <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>Overall sentiment</p>
                    <h3 style={{ margin: '0.4rem 0 0', fontSize: '1.4rem' }}>{overallSentiment}</h3>
                  </div>
                  <div style={{ background: 'white', padding: '1rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
                    <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>Weighted score</p>
                    <h3 style={{ margin: '0.4rem 0 0', fontSize: '1.4rem' }}>{weightedScore}</h3>
                  </div>
                  <div style={{ background: 'white', padding: '1rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
                    <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>Items analyzed</p>
                    <h3 style={{ margin: '0.4rem 0 0', fontSize: '1.4rem' }}>{data.items_analyzed || items.length}</h3>
                  </div>
                </div>

                <div style={{ background: 'white', padding: '1rem', borderRadius: '18px', height: '270px', marginBottom: '1rem', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
                  <h2 style={{ margin: '0 0 0.75rem', fontSize: '1.1rem' }}>Sentiment distribution</h2>
                  <ResponsiveContainer width="100%" height="85%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="name" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#16a34a" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div style={{ display: 'grid', gap: '0.9rem' }}>
                  {items.slice(0, 10).map((item, index) => {
                    const color = item.score > 0 ? '#16a34a' : item.score < 0 ? '#dc2626' : '#64748b'
                    return (
                      <article key={`${item.text}-${index}`} style={{ background: 'white', padding: '1rem', borderRadius: '18px', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)' }}>
                        <p style={{ margin: '0 0 0.6rem', lineHeight: 1.5 }}>{item.text}</p>
                        <span style={{ color, fontWeight: 800, textTransform: 'capitalize' }}>{item.label} ({(Number(item.confidence || 0) * 100).toFixed(1)}%)</span>
                      </article>
                    )
                  })}
                </div>
              </>
            )}
          </section>
        </section>
      </div>
    </main>
  )
}
