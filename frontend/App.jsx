import { useState } from 'react'
import axios from 'axios'

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

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', background: '#f8fafc', minHeight: '100vh' }}>
      <h2>VertexStudy Dashboard</h2>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter ticker or URL"
          style={{ padding: '0.5rem', borderRadius: '8px', flex: 1 }}
        />
        <button onClick={analyze}>Analyze</button>
      </div>

      {loading && <p>Loading...</p>}

      {data && (
        <div>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}