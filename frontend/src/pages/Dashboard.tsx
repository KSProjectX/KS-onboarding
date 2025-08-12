import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  Users,
  Brain,
  MessageSquare,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertTriangle,
  Activity,
  Zap,
} from 'lucide-react'
import { Line, Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js'
import ApiService, { DashboardData } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import StatCard from '../components/StatCard'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
)

const Dashboard: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d')
  const [selectedClient, setSelectedClient] = useState<string | undefined>(undefined)

  // Fetch dashboard data
  const {
    data: dashboardResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['dashboard', selectedClient],
    queryFn: () => ApiService.getDashboardData(selectedClient),
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const dashboardData = dashboardResponse?.data

  // Chart configurations
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  // Workflow status chart data
  const workflowStatusData = {
    labels: ['Completed', 'In Progress', 'Failed', 'Pending'],
    datasets: [
      {
        data: [
          dashboardData?.system_metrics?.completed_workflows || 0,
          dashboardData?.system_metrics?.active_workflows || 0,
          dashboardData?.system_metrics?.failed_workflows || 0,
          (dashboardData?.system_metrics?.total_workflows || 0) -
            (dashboardData?.system_metrics?.completed_workflows || 0) -
            (dashboardData?.system_metrics?.active_workflows || 0) -
            (dashboardData?.system_metrics?.failed_workflows || 0),
        ],
        backgroundColor: [
          '#10b981', // success
          '#3b82f6', // primary
          '#ef4444', // danger
          '#6b7280', // secondary
        ],
        borderWidth: 0,
      },
    ],
  }

  // Industry distribution chart data
  const industryData = {
    labels: ['Automotive', 'Healthcare', 'Retail', 'Other'],
    datasets: [
      {
        label: 'Clients by Industry',
        data: [
          dashboardData?.client_profiles?.filter(p => p.industry?.toLowerCase() === 'automotive').length || 0,
          dashboardData?.client_profiles?.filter(p => p.industry?.toLowerCase() === 'healthcare').length || 0,
          dashboardData?.client_profiles?.filter(p => p.industry?.toLowerCase() === 'retail').length || 0,
          dashboardData?.client_profiles?.filter(p => 
            !['automotive', 'healthcare', 'retail'].includes(p.industry?.toLowerCase())
          ).length || 0,
        ],
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#6b7280',
        ],
        borderRadius: 4,
      },
    ],
  }

  // Performance metrics over time (mock data for demo)
  const performanceData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Workflows Completed',
        data: [12, 19, 15, 25, 22, 18, 24],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Client Satisfaction',
        data: [85, 88, 92, 89, 94, 91, 96],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
    ],
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load dashboard"
        message="Unable to fetch dashboard data. Please try again."
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Dashboard</h1>
          <p className="mt-1 text-sm text-secondary-600">
            Overview of your K-Square programme onboarding activities
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="input text-sm"
          >
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          
          <button
            onClick={() => refetch()}
            className="btn btn-outline btn-sm"
          >
            <Activity className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Workflows"
          value={dashboardData?.system_metrics?.total_workflows || 0}
          icon={BarChart3}
          trend={{ value: 12, isPositive: true }}
          color="primary"
        />
        
        <StatCard
          title="Active Clients"
          value={dashboardData?.client_profiles?.length || 0}
          icon={Users}
          trend={{ value: 8, isPositive: true }}
          color="success"
        />
        
        <StatCard
          title="Insights Generated"
          value={dashboardData?.insights?.length || 0}
          icon={Brain}
          trend={{ value: 15, isPositive: true }}
          color="warning"
        />
        
        <StatCard
          title="Meetings Analyzed"
          value={dashboardData?.meetings?.length || 0}
          icon={MessageSquare}
          trend={{ value: 5, isPositive: false }}
          color="info"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workflow Status Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="card-title">Workflow Status</h3>
            <p className="card-description">Distribution of workflow statuses</p>
          </div>
          <div className="card-content">
            <div className="h-64">
              <Doughnut data={workflowStatusData} options={{ ...chartOptions, maintainAspectRatio: false }} />
            </div>
          </div>
        </motion.div>

        {/* Industry Distribution Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="card-title">Clients by Industry</h3>
            <p className="card-description">Distribution across different sectors</p>
          </div>
          <div className="card-content">
            <div className="h-64">
              <Bar data={industryData} options={chartOptions} />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Performance Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="card-header">
          <h3 className="card-title">Performance Trends</h3>
          <p className="card-description">Weekly performance metrics</p>
        </div>
        <div className="card-content">
          <div className="h-80">
            <Line data={performanceData} options={chartOptions} />
          </div>
        </div>
      </motion.div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <div className="card">
            <div className="card-content p-6">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                Recent Activity
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-success-600" />
                    <span className="text-sm text-secondary-700">Programme setup completed</span>
                  </div>
                  <span className="text-xs text-secondary-500">2 hours ago</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Brain className="w-5 h-5 text-primary-600" />
                    <span className="text-sm text-secondary-700">New insights generated</span>
                  </div>
                  <span className="text-xs text-secondary-500">4 hours ago</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="card">
            <div className="card-content p-6">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button className="w-full btn btn-primary text-left">
                  <Zap className="w-4 h-4 mr-2" />
                  Generate New Insights
                </button>
                <button className="w-full btn btn-secondary text-left">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Upload Meeting
                </button>
                <button className="w-full btn btn-outline text-left">
                  <Users className="w-4 h-4 mr-2" />
                  Add Client Profile
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* System Health */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <div className="card-header">
          <h3 className="card-title flex items-center">
            <Zap className="w-5 h-5 mr-2 text-success-600" />
            System Health
          </h3>
          <p className="card-description">Current system status and performance</p>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3 p-4 bg-success-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-success-600" />
              <div>
                <p className="font-medium text-success-900">API Status</p>
                <p className="text-sm text-success-700">All systems operational</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-primary-50 rounded-lg">
              <Clock className="w-8 h-8 text-primary-600" />
              <div>
                <p className="font-medium text-primary-900">Response Time</p>
                <p className="text-sm text-primary-700">~250ms average</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-warning-50 rounded-lg">
              <TrendingUp className="w-8 h-8 text-warning-600" />
              <div>
                <p className="font-medium text-warning-900">Uptime</p>
                <p className="text-sm text-warning-700">99.9% this month</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard