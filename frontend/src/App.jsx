import React, { useEffect, useState } from 'react';
import './App.css';

const API_BASE = '/api/literature';

function App() {
  const [poems, setPoems] = useState([]);
  const [stories, setStories] = useState([]);
  const [gajals, setGajals] = useState([]);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    fetch(`${API_BASE}/poem/`).then(res => res.json()).then(setPoems);
    fetch(`${API_BASE}/story/`).then(res => res.json()).then(setStories);
    fetch(`${API_BASE}/gajal/`).then(res => res.json()).then(setGajals);
  }, []);

  const handleLogin = async () => {
    const res = await fetch('/api/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'admin', password: 'admin' })
    });
    const data = await res.json();
    localStorage.setItem('token', data.access);
    setToken(data.access);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <div className="App">
      <header className="header">
        <div className="title">Title Banner</div>
        <div className="news">News Slider</div>
        <nav className="menu">Menu Bar</nav>
      </header>

      <main className="body">
        <h2>Literature</h2>

        <section>
          <h3>Poems</h3>
          {poems.map(p => (
            <div className="card" key={p.id}>
              <strong>{p.title}</strong><br/>
              <small>{p.created_by?.user?.username}</small>
            </div>
          ))}
          {token && <button className="btn">Add Poem</button>}
        </section>

        <section>
          <h3>Stories</h3>
          {stories.map(s => (
            <div className="card" key={s.id}>
              <strong>{s.title}</strong><br/>
              <small>{s.created_by?.user?.username}</small>
            </div>
          ))}
          {token && <button className="btn">Add Story</button>}
        </section>

        <section>
          <h3>Gajals</h3>
          {gajals.map(g => (
            <div className="card" key={g.id}>
              <strong>{g.title}</strong><br/>
              <small>{g.created_by?.user?.username}</small>
            </div>
          ))}
          {token && <button className="btn">Add Gajal</button>}
        </section>

        <div className="auth">
          {!token ? (
            <button className="btn" onClick={handleLogin}>Login</button>
          ) : (
            <button className="btn" onClick={handleLogout}>Logout</button>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
