import React from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { clsx } from 'clsx'

interface ErrorMessageProps {
  title?: string
  message: string
  onRetry?: () => void
  retryText?: string
  className?: string
  variant?: 'default' | 'compact'
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  retryText = 'Try again',
  className,
  variant = 'default',
}) => {
  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={clsx(
          'flex items-center space-x-2 p-3 bg-danger-50 border border-danger-200 rounded-lg',
          className
        )}
      >
        <AlertTriangle className="w-4 h-4 text-danger-600 flex-shrink-0" />
        <p className="text-sm text-danger-800 flex-1">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-danger-600 hover:text-danger-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'flex flex-col items-center justify-center p-8 text-center',
        className
      )}
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
        className="flex items-center justify-center w-16 h-16 bg-danger-100 rounded-full mb-4"
      >
        <AlertTriangle className="w-8 h-8 text-danger-600" />
      </motion.div>
      
      <motion.h3
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-lg font-semibold text-secondary-900 mb-2"
      >
        {title}
      </motion.h3>
      
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-secondary-600 mb-6 max-w-md"
      >
        {message}
      </motion.p>
      
      {onRetry && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          onClick={onRetry}
          className="btn btn-primary"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          {retryText}
        </motion.button>
      )}
    </motion.div>
  )
}

export default ErrorMessage