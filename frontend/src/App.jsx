import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { ConfirmEmail } from "./pages/CofirmEmail";
import { Home } from "./pages/Home";

import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/confirm-email/:token" element={<ConfirmEmail />} />
      </Routes>
    </Router>
  );
}

export default App;
