import React from 'react';
import { createRoot } from 'react-dom/client';

function App(): React.ReactElement {
  return <h1>Malato</h1>;
}

const el = document.getElementById('root');
if (el) {
  createRoot(el).render(<App />);
}
