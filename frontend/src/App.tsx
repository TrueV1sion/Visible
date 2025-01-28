import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { useAuth } from './contexts/AuthContext';

// Layout
import MainLayout from './layouts/MainLayout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import BattlecardList from './pages/BattlecardList';
import BattlecardDetail from './pages/BattlecardDetail';
import BattlecardEditor from './pages/BattlecardEditor';
import CompetitorAnalysis from './pages/CompetitorAnalysis';
import ObjectionLibrary from './pages/ObjectionLibrary';
import UseCases from './pages/UseCases';
import Settings from './pages/Settings';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" /> : <Login />
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="battlecards">
          <Route index element={<BattlecardList />} />
          <Route path=":id" element={<BattlecardDetail />} />
          <Route path="new" element={<BattlecardEditor />} />
          <Route path=":id/edit" element={<BattlecardEditor />} />
        </Route>
        <Route path="competitor-analysis" element={<CompetitorAnalysis />} />
        <Route path="objection-library" element={<ObjectionLibrary />} />
        <Route path="use-cases" element={<UseCases />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

export default App; 