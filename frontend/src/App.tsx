import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Dashboard from "./pages/dashboard/Dashboard";
import Resume from "./pages/resume/Resume";
import Interview from "./pages/interview/Interview";
import Landing from "./pages/landing/Landing";
import History from "./pages/history/History";
import Report from "./pages/report/Report";
import Profile from "./pages/profile/Profile";

// TODO: swap these placeholders out as each real page gets built.
// Keeping them here means the route tree compiles and is testable
// end-to-end before every page exists.
function Placeholder({ label }: { label: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg text-text-primary">
      <p className="font-mono text-sm text-text-secondary">{label} — coming soon</p>
    </div>
  );
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/history" element={<History />} />
        <Route path="/report/:id" element={<Report />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      <Route path="*" element={<Placeholder label="404" />} />
    </Routes>
  );
}

export default App;
