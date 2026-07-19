import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import DemoBanner from "./components/DemoBanner";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import LoginPage from "./pages/LoginPage";
import ProviderListPage from "./pages/ProviderListPage";
import ProviderDetailPage from "./pages/ProviderDetailPage";
import MatchPage from "./pages/MatchPage";
import MyAppointmentsPage from "./pages/MyAppointmentsPage";
import AppointmentConfirmationPage from "./pages/AppointmentConfirmationPage";
import AdminAppointmentsPage from "./pages/AdminAppointmentsPage";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <DemoBanner />
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProviderListPage />} />
          <Route path="/providers/:providerId" element={<ProviderDetailPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/match" element={<MatchPage />} />
            <Route path="/appointments" element={<MyAppointmentsPage />} />
            <Route
              path="/appointment-confirmation/:appointmentId"
              element={<AppointmentConfirmationPage />}
            />
          </Route>
          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminAppointmentsPage />} />
          </Route>
        </Routes>
      </main>
    </div>
  );
}
