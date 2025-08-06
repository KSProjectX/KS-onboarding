import React from 'react'
import { motion } from 'framer-motion'
import { Home, ArrowLeft, Search } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto text-center"
        >
          {/* 404 Animation */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mb-8"
          >
            <div className="text-8xl md:text-9xl font-bold text-primary-600 mb-4">
              404
            </div>
            <div className="w-32 h-1 bg-gradient-to-r from-primary-500 to-secondary-500 mx-auto rounded-full"></div>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mb-8"
          >
            <h1 className="text-3xl md:text-4xl font-bold text-secondary-900 mb-4">
              Page Not Found
            </h1>
            <p className="text-lg text-secondary-600 mb-6">
              Sorry, the page you are looking for doesn't exist or has been moved.
            </p>
            <p className="text-secondary-500">
              You might have mistyped the address or the page may have been relocated.
            </p>
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link
              to="/"
              className="btn btn-primary flex items-center space-x-2"
            >
              <Home className="w-4 h-4" />
              <span>Go Home</span>
            </Link>
            
            <button
              onClick={() => navigate(-1)}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Go Back</span>
            </button>
          </motion.div>

          {/* Helpful Links */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-12 pt-8 border-t border-secondary-200"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              Popular Pages
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Link
                to="/"
                className="p-4 bg-white rounded-lg shadow-sm hover:shadow-medium transition-shadow text-center group"
              >
                <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:bg-primary-200 transition-colors">
                  <Home className="w-4 h-4 text-primary-600" />
                </div>
                <div className="text-sm font-medium text-secondary-900">Dashboard</div>
              </Link>
              
              <Link
                to="/programme-setup"
                className="p-4 bg-white rounded-lg shadow-sm hover:shadow-medium transition-shadow text-center group"
              >
                <div className="w-8 h-8 bg-secondary-100 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:bg-secondary-200 transition-colors">
                  <Search className="w-4 h-4 text-secondary-600" />
                </div>
                <div className="text-sm font-medium text-secondary-900">Setup</div>
              </Link>
              
              <Link
                to="/insights"
                className="p-4 bg-white rounded-lg shadow-sm hover:shadow-medium transition-shadow text-center group"
              >
                <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:bg-success-200 transition-colors">
                  <Search className="w-4 h-4 text-success-600" />
                </div>
                <div className="text-sm font-medium text-secondary-900">Insights</div>
              </Link>
              
              <Link
                to="/knowledge-base"
                className="p-4 bg-white rounded-lg shadow-sm hover:shadow-medium transition-shadow text-center group"
              >
                <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:bg-warning-200 transition-colors">
                  <Search className="w-4 h-4 text-warning-600" />
                </div>
                <div className="text-sm font-medium text-secondary-900">Knowledge</div>
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default NotFound