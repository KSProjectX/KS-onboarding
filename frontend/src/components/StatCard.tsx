import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, LucideIcon } from 'lucide-react'
import { clsx } from 'clsx'

interface StatCardProps {
  title: string
  value: number | string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  className?: string
  subtitle?: string
  loading?: boolean
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  color = 'primary',
  className,
  subtitle,
  loading = false,
}) => {
  const colorClasses = {
    primary: {
      bg: 'bg-primary-50',
      icon: 'text-primary-600',
      border: 'border-primary-200',
    },
    success: {
      bg: 'bg-success-50',
      icon: 'text-success-600',
      border: 'border-success-200',
    },
    warning: {
      bg: 'bg-warning-50',
      icon: 'text-warning-600',
      border: 'border-warning-200',
    },
    danger: {
      bg: 'bg-danger-50',
      icon: 'text-danger-600',
      border: 'border-danger-200',
    },
    info: {
      bg: 'bg-secondary-50',
      icon: 'text-secondary-600',
      border: 'border-secondary-200',
    },
  }

  const colors = colorClasses[color]

  if (loading) {
    return (
      <div className={clsx('card', className)}>
        <div className="card-content p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="h-4 bg-secondary-200 rounded animate-pulse mb-2"></div>
              <div className="h-8 bg-secondary-200 rounded animate-pulse mb-1"></div>
              <div className="h-3 bg-secondary-200 rounded animate-pulse w-20"></div>
            </div>
            <div className="w-12 h-12 bg-secondary-200 rounded-lg animate-pulse"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className={clsx('card hover:shadow-medium transition-shadow', className)}
    >
      <div className="card-content p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-secondary-600 mb-1">
              {title}
            </p>
            
            <motion.p
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-2xl font-bold text-secondary-900 mb-1"
            >
              {typeof value === 'number' ? value.toLocaleString() : value}
            </motion.p>
            
            <div className="flex items-center space-x-2">
              {trend && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className={clsx(
                    'flex items-center text-xs font-medium',
                    trend.isPositive ? 'text-success-600' : 'text-danger-600'
                  )}
                >
                  {trend.isPositive ? (
                    <TrendingUp className="w-3 h-3 mr-1" />
                  ) : (
                    <TrendingDown className="w-3 h-3 mr-1" />
                  )}
                  {Math.abs(trend.value)}%
                </motion.div>
              )}
              
              {subtitle && (
                <p className="text-xs text-secondary-500">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            className={clsx(
              'flex items-center justify-center w-12 h-12 rounded-lg border',
              colors.bg,
              colors.border
            )}
          >
            <Icon className={clsx('w-6 h-6', colors.icon)} />
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}

export default StatCard