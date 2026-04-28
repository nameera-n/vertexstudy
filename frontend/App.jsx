import { useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function App() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const analyze = async () => {
    setLoading(true)
    try {
      const url = query.startsWith('http')
        ? `http://localhost:8000/analyze?url=${query}`
        : `http://localhost:8000/analyze?ticker=${query}`

      const res = await axios.get(url)
      setData(res.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const getSummary = () => {
    if (!data || !data.results) return null

    let pos = 0, neu = 0, neg = 0
    data.results.forEach(r => {
      if (r.score > 0) pos++
      else if (r.score < 0) neg++
      else neu++
    })

    return [
      { name: 'Positive', value: pos },
      { name: 'Neutral', value: neu },
      { name: 'Negative', value: neg }
    ]
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', background: '#f9fafb', minHeight: '100vh' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>VertexStudy Dashboard</h2>

      <div style={{ display: 'flex', gap: '2rem' }}>

        {/* LEFT PANEL */}
        <div style={{ flex: 1, background: 'white', padding: '1rem', borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
          <h4>Input</h4>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter ticker or URL"
            style={{ padding: '0.6rem', borderRadius: '8px', width: '100%', marginBottom: '1rem' }}
          />
          <button onClick={analyze} style={{ padding: '0.6rem 1rem', background: '#16a34a', color: 'white', border: 'none', borderRadius: '8px' }}>
            Analyze
          </button>
        </div>

        {/* RIGHT PANEL */}
        <div style={{ flex: 2 }}>

          {loading && <p>Analyzing...</p>}

          {data && (
            <>
              <div style={{ background: 'white', padding: '1rem', borderRadius: '16px', marginBottom: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
                <h4>Summary</h4>
                <p><b>Score:</b> {data.weighted_score?.toFixed(3)}</p>
              </div>

              {/* CHART */}
              <div style={{ background: 'white', padding: '1rem', borderRadius: '16px', marginBottom: '1rem', height: '250px', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={getSummary()}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#16a34a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* RESULTS */}
              {data.results?.slice(0,10).map((r, i) => (
                <div key={i} style={{ background: 'white', padding: '1rem', borderRadius: '16px', marginBottom: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
                  <p>{r.text}</p>
                  <span style={{ color: r.score > 0 ? '#16a34a' : r.score < 0 ? '#dc2626' : '#6b7280' }}>
                    {r.label} ({(r.confidence*100).toFixed(1)}%)
                  </span>
                </div>
              ))}
            </>
          )}

        </div>
      </div>
    </div>
  )
}
