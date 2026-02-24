import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { DocumentPage } from './pages/DocumentPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="documents/:docId" element={<DocumentPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
