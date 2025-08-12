import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Settings,
  Users,
  Brain,
  MessageSquare,
  BookOpen,
  BarChart3,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { clsx } from 'clsx'

interface LayoutProps {
  children: React.ReactNode
}

interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  description: string
}

const navigation: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Overview and metrics',
  },
  {
    name: 'Programme Setup',
    href: '/setup',
    icon: Settings,
    description: 'Configure new programmes',
  },
  {
    name: 'Client Profile',
    href: '/profile',
    icon: Users,
    description: 'Manage client information',
  },
  {
    name: 'Insights',
    href: '/insights',
    icon: Brain,
    description: 'AI-generated recommendations',
  },
  {
    name: 'Meetings',
    href: '/meetings',
    icon: MessageSquare,
    description: 'Meeting analysis and transcripts',
  },
  {
    name: 'Knowledge Base',
    href: '/knowledge',
    icon: BookOpen,
    description: 'Search domain knowledge',
  },
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const location = useLocation()

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const toggleCollapse = () => setSidebarCollapsed(!sidebarCollapsed)

  const sidebarVariants = {
    open: {
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    closed: {
      x: '-100%',
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
  }

  const contentVariants = {
    expanded: {
      marginLeft: sidebarCollapsed ? '4rem' : '16rem',
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    collapsed: {
      marginLeft: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
  }

  return (
    <div className="flex h-screen bg-secondary-50">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <motion.div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-secondary-200 shadow-lg lg:relative lg:z-auto',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
        animate={sidebarCollapsed ? 'collapsed' : 'expanded'}
        variants={{
          expanded: { width: '16rem' },
          collapsed: { width: '4rem' },
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {/* Sidebar header */}
        <div className="flex items-center justify-between p-4 border-b border-secondary-200">
          <AnimatePresence mode="wait">
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex items-center space-x-3"
              >
                <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-lg">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-secondary-900">K-Square</h1>
                  <p className="text-xs text-secondary-500">Onboarding Agent</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <button
            onClick={toggleCollapse}
            className="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg hover:bg-secondary-100 transition-colors"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4 text-secondary-600" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-secondary-600" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 group relative',
                  isActive
                    ? 'bg-primary-100 text-primary-900 shadow-sm'
                    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900'
                )}
                title={sidebarCollapsed ? item.name : undefined}
              >
                <Icon
                  className={clsx(
                    'flex-shrink-0 w-5 h-5 transition-colors',
                    isActive ? 'text-primary-600' : 'text-secondary-500 group-hover:text-secondary-700',
                    sidebarCollapsed ? 'mx-auto' : 'mr-3'
                  )}
                />
                <AnimatePresence mode="wait">
                  {!sidebarCollapsed && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      className="flex-1 min-w-0"
                    >
                      <div className="truncate">{item.name}</div>
                      {!isActive && (
                        <div className="text-xs text-secondary-500 truncate">
                          {item.description}
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
                
                {/* Tooltip for collapsed sidebar */}
                {sidebarCollapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-secondary-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                    {item.name}
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="p-4 border-t border-secondary-200">
          <Link
            to="/settings"
            className={clsx(
              'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              location.pathname === '/settings'
                ? 'bg-primary-100 text-primary-900'
                : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900'
            )}
            title={sidebarCollapsed ? 'Settings' : undefined}
          >
            <Settings
              className={clsx(
                'flex-shrink-0 w-5 h-5',
                sidebarCollapsed ? 'mx-auto' : 'mr-3'
              )}
            />
            <AnimatePresence mode="wait">
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                >
                  Settings
                </motion.span>
              )}
            </AnimatePresence>
          </Link>
        </div>
      </motion.div>

      {/* Mobile sidebar */}
      <motion.div
        className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-secondary-200 shadow-lg lg:hidden"
        variants={sidebarVariants}
        animate={sidebarOpen ? 'open' : 'closed'}
        initial="closed"
      >
        {/* Mobile header */}
        <div className="flex items-center justify-between p-4 border-b border-secondary-200">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-lg">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-secondary-900">K-Square</h1>
              <p className="text-xs text-secondary-500">Onboarding Agent</p>
            </div>
          </div>
          <button
            onClick={toggleSidebar}
            className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-secondary-100 transition-colors"
          >
            <X className="w-4 h-4 text-secondary-600" />
          </button>
        </div>

        {/* Mobile navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={toggleSidebar}
                className={clsx(
                  'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-100 text-primary-900'
                    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900'
                )}
              >
                <Icon className="flex-shrink-0 w-5 h-5 mr-3" />
                <div className="flex-1 min-w-0">
                  <div className="truncate">{item.name}</div>
                  <div className="text-xs text-secondary-500 truncate">
                    {item.description}
                  </div>
                </div>
              </Link>
            )
          })}
        </nav>

        {/* Mobile footer */}
        <div className="p-4 border-t border-secondary-200">
          <Link
            to="/settings"
            onClick={toggleSidebar}
            className={clsx(
              'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              location.pathname === '/settings'
                ? 'bg-primary-100 text-primary-900'
                : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900'
            )}
          >
            <Settings className="flex-shrink-0 w-5 h-5 mr-3" />
            Settings
          </Link>
        </div>
      </motion.div>

      {/* Main content */}
      <motion.div
        className="flex-1 flex flex-col min-w-0"
        variants={contentVariants}
        animate={window.innerWidth >= 1024 ? 'expanded' : 'collapsed'}
      >
        {/* Top bar */}
        <header className="bg-white border-b border-secondary-200 shadow-sm">
          <div className="flex items-center justify-between px-4 py-3 lg:px-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleSidebar}
                className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-secondary-100 transition-colors lg:hidden"
              >
                <Menu className="w-5 h-5 text-secondary-600" />
              </button>
              
              <div>
                <h2 className="text-lg font-semibold text-secondary-900">
                  {navigation.find(item => item.href === location.pathname)?.name || 'K-Square Onboarding'}
                </h2>
                <p className="text-sm text-secondary-500">
                  {navigation.find(item => item.href === location.pathname)?.description || 'AI-driven programme onboarding system'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="hidden sm:flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-xs font-medium">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                System Online
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 lg:p-6">
            {children}
          </div>
        </main>
      </motion.div>
    </div>
  )
}

export default Layout