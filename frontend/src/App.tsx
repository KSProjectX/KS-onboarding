import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProgrammeSetup from './pages/ProgrammeSetup'
import ClientProfile from './pages/ClientProfile'
import Insights from './pages/Insights'
import Meetings from './pages/Meetings'
import KnowledgeBase from './pages/KnowledgeBase'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <Layout>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="h-full"
        >
          <Routes>
            {/* Default route redirects to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Main application routes */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/setup" element={<ProgrammeSetup />} />
            <Route path="/profile" element={<ClientProfile />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/meetings" element={<Meetings />} />
            <Route path="/knowledge" element={<KnowledgeBase />} />
            <Route path="/settings" element={<Settings />} />
            
            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </motion.div>
      </Layout>
    </div>
  )
}

export default App