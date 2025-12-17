import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import LibraryPage from './pages/LibraryPage';
import ExercisesPage from './pages/ExercisesPage';
import ProgressPage from './pages/ProgressPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:chatId" element={<ChatPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/exercises" element={<ExercisesPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default App;
