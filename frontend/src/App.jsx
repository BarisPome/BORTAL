import { useEffect, useState } from 'react';

function App() {
  const [msg, setMsg] = useState("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/hello/")
      .then((res) => res.json())
      .then((data) => setMsg(data.message))
      .catch((err) => setMsg("Error connecting to backend"));
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>{msg}</h1>
    </div>
  );
}

export default App;
