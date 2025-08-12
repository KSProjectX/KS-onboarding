import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  BarChart3,
  RefreshCw,
  Download,
  Filter,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import StatCard from '../components/StatCard'

interface Insight {
  id: string
  type: 'strategic' | 'tactical' | 'risk' | 'opportunity'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  impact_score: number
  effort_estimate: string
  timeline: string
  resources_required: string[]
  success_metrics: string[]
  risk_factors: string[]
  recommendations: string[]
  status: 'pending' | 'in_progress' | 'completed' | 'dismissed'
  created_at: string
  updated_at: string
}

interface InsightsSummary {
  total_insights: number
  high_priority: number
  medium_priority: number
  low_priority: number
  completed: number
  in_progress: number
  pending: number
  average_impact: number
  project_health_score: number
}

const Insights: React.FC = () => {
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedPriority, setSelectedPriority] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const queryClient = useQueryClient()

  const {
    data: insights,
    isLoading: insightsLoading,
    error: insightsError,
    refetch: refetchInsights,
  } = useQuery({
    queryKey: ['insights'],
    queryFn: () => ApiService.getInsights(),
  })

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useQuery({
    queryKey: ['insights-summary'],
    queryFn: () => ApiService.getInsightsSummary(),
  })

  const generateInsightsMutation = useMutation({
    mutationFn: ApiService.generateInsights,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insights'] })
      queryClient.invalidateQueries({ queryKey: ['insights-summary'] })
      toast.success('New insights generated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate insights')
    },
  })

  const updateInsightMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      ApiService.updateInsightStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insights'] })
      queryClient.invalidateQueries({ queryKey: ['insights-summary'] })
      toast.success('Insight status updated!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update insight')
    },
  })

  const exportInsightsMutation = useMutation({
    mutationFn: ApiService.exportInsights,
    onSuccess: (data) => {
      // Create and download file
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `insights-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('Insights exported successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to export insights')
    },
  })

  const filteredInsights = insights?.data?.filter((insight: Insight) => {
    if (selectedType !== 'all' && insight.type !== selectedType) return false
    if (selectedPriority !== 'all' && insight.priority !== selectedPriority) return false
    if (selectedStatus !== 'all' && insight.status !== selectedStatus) return false
    return true
  }) || []

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'strategic':
        return Target
      case 'tactical':
        return CheckCircle
      case 'risk':
        return AlertTriangle
      case 'opportunity':
        return TrendingUp
      default:
        return BarChart3
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'strategic':
        return 'primary'
      case 'tactical':
        return 'success'
      case 'risk':
        return 'danger'
      case 'opportunity':
        return 'warning'
      default:
        return 'info'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-danger-600 bg-danger-100'
      case 'medium':
        return 'text-warning-600 bg-warning-100'
      case 'low':
        return 'text-success-600 bg-success-100'
      default:
        return 'text-secondary-600 bg-secondary-100'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-100'
      case 'in_progress':
        return 'text-primary-600 bg-primary-100'
      case 'pending':
        return 'text-warning-600 bg-warning-100'
      case 'dismissed':
        return 'text-secondary-600 bg-secondary-100'
      default:
        return 'text-secondary-600 bg-secondary-100'
    }
  }

  if (insightsLoading || summaryLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading insights..." />
      </div>
    )
  }

  if (insightsError || summaryError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <ErrorMessage
          message="Failed to load insights"
          onRetry={refetchInsights}
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900 mb-2">
                Actionable Insights
              </h1>
              <p className="text-secondary-600">
                Strategic recommendations and tactical actions for your programme
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowFilters(!showFilters)}
                className="btn btn-secondary"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => exportInsightsMutation.mutate()}
                disabled={exportInsightsMutation.isPending}
                className="btn btn-secondary"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => generateInsightsMutation.mutate()}
                disabled={generateInsightsMutation.isPending}
                className="btn btn-primary"
              >
                {generateInsightsMutation.isPending ? (
                  <LoadingSpinner size="sm" color="white" />
                ) : (
                  <RefreshCw className="w-4 h-4 mr-2" />
                )}
                Generate New
              </motion.button>
            </div>
          </div>

          {/* Summary Stats */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Insights"
                value={summary.data.total_insights}
                icon={BarChart3}
                color="primary"
              />
              <StatCard
                title="High Priority"
                value={summary.data.high_priority}
                icon={AlertTriangle}
                color="danger"
              />
              <StatCard
                title="Project Health"
                value={`${summary.data.project_health_score}%`}
                icon={TrendingUp}
                color="success"
                trend={{
                  value: 5.2,
                  isPositive: true,
                }}
              />
              <StatCard
                title="Avg Impact"
                value={`${summary.data.average_impact.toFixed(1)}/10`}
                icon={Target}
                color="warning"
              />
            </div>
          )}

          {/* Filters */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="card mb-6"
              >
                <div className="card-content p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-1">
                        Type
                      </label>
                      <select
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value)}
                        className="input"
                      >
                        <option value="all">All Types</option>
                        <option value="strategic">Strategic</option>
                        <option value="tactical">Tactical</option>
                        <option value="risk">Risk</option>
                        <option value="opportunity">Opportunity</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-1">
                        Priority
                      </label>
                      <select
                        value={selectedPriority}
                        onChange={(e) => setSelectedPriority(e.target.value)}
                        className="input"
                      >
                        <option value="all">All Priorities</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-1">
                        Status
                      </label>
                      <select
                        value={selectedStatus}
                        onChange={(e) => setSelectedStatus(e.target.value)}
                        className="input"
                      >
                        <option value="all">All Statuses</option>
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="dismissed">Dismissed</option>
                      </select>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Insights List */}
            <div className="lg:col-span-2">
              <div className="space-y-4">
                {filteredInsights && filteredInsights.length > 0 ? (
                  filteredInsights.map((insight: Insight) => {
                    const TypeIcon = getTypeIcon(insight.type)
                    return (
                      <motion.div
                        key={insight.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ y: -2 }}
                        onClick={() => setSelectedInsight(insight)}
                        className={`card cursor-pointer transition-all hover:shadow-medium ${
                          selectedInsight?.id === insight.id
                            ? 'ring-2 ring-primary-500'
                            : ''
                        }`}
                      >
                        <div className="card-content p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex items-start space-x-3">
                              <div
                                className={`flex items-center justify-center w-10 h-10 rounded-lg bg-${getTypeColor(
                                  insight.type
                                )}-100`}
                              >
                                <TypeIcon
                                  className={`w-5 h-5 text-${getTypeColor(
                                    insight.type
                                  )}-600`}
                                />
                              </div>
                              <div className="flex-1">
                                <h3 className="font-semibold text-secondary-900 mb-1">
                                  {insight.title}
                                </h3>
                                <p className="text-sm text-secondary-600 line-clamp-2">
                                  {insight.description}
                                </p>
                              </div>
                            </div>
                            <div className="flex flex-col items-end space-y-2">
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(
                                  insight.priority
                                )}`}
                              >
                                {insight.priority.toUpperCase()}
                              </span>
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                                  insight.status
                                )}`}
                              >
                                {insight.status.replace('_', ' ').toUpperCase()}
                              </span>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between text-sm text-secondary-600">
                            <div className="flex items-center space-x-4">
                              <div className="flex items-center space-x-1">
                                <Target className="w-4 h-4" />
                                <span>Impact: {insight.impact_score}/10</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Clock className="w-4 h-4" />
                                <span>{insight.timeline}</span>
                              </div>
                            </div>
                            <span className="text-xs text-secondary-500">
                              {new Date(insight.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    )
                  })
                ) : (
                  <div className="card">
                    <div className="card-content p-8 text-center">
                      <BarChart3 className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                        No Insights Found
                      </h3>
                      <p className="text-secondary-600 mb-4">
                        {insights?.data?.length === 0
                          ? 'Generate your first insights to get started'
                          : 'No insights match your current filters'}
                      </p>
                      {insights?.data?.length === 0 && (
                        <button
                          onClick={() => generateInsightsMutation.mutate()}
                          className="btn btn-primary"
                        >
                          Generate Insights
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Insight Details */}
            <div className="lg:col-span-1">
              {selectedInsight ? (
                <motion.div
                  key={selectedInsight.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="card sticky top-8"
                >
                  <div className="card-header">
                    <h3 className="card-title">{selectedInsight.title}</h3>
                  </div>
                  <div className="card-content p-6 space-y-6">
                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Description
                      </h4>
                      <p className="text-secondary-600 text-sm">
                        {selectedInsight.description}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h5 className="font-medium text-secondary-700 mb-1">
                          Impact Score
                        </h5>
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-secondary-200 rounded-full h-2">
                            <div
                              className="bg-primary-600 h-2 rounded-full"
                              style={{ width: `${selectedInsight.impact_score * 10}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-secondary-900">
                            {selectedInsight.impact_score}/10
                          </span>
                        </div>
                      </div>
                      <div>
                        <h5 className="font-medium text-secondary-700 mb-1">
                          Effort
                        </h5>
                        <p className="text-sm text-secondary-600">
                          {selectedInsight.effort_estimate}
                        </p>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Timeline
                      </h4>
                      <p className="text-secondary-600 text-sm">
                        {selectedInsight.timeline}
                      </p>
                    </div>

                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Resources Required
                      </h4>
                      <div className="space-y-1">
                        {selectedInsight.resources_required.map((resource, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <Users className="w-3 h-3 text-secondary-500" />
                            <span className="text-sm text-secondary-600">{resource}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Success Metrics
                      </h4>
                      <div className="space-y-1">
                        {selectedInsight.success_metrics.map((metric, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <CheckCircle className="w-3 h-3 text-success-500" />
                            <span className="text-sm text-secondary-600">{metric}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {selectedInsight.risk_factors.length > 0 && (
                      <div>
                        <h4 className="font-medium text-secondary-900 mb-2">
                          Risk Factors
                        </h4>
                        <div className="space-y-1">
                          {selectedInsight.risk_factors.map((risk, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <AlertTriangle className="w-3 h-3 text-danger-500" />
                              <span className="text-sm text-secondary-600">{risk}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Recommendations
                      </h4>
                      <div className="space-y-1">
                        {selectedInsight.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <TrendingUp className="w-3 h-3 text-primary-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-secondary-600">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-secondary-900 mb-2">
                        Update Status
                      </h4>
                      <select
                        value={selectedInsight.status}
                        onChange={(e) =>
                          updateInsightMutation.mutate({
                            id: selectedInsight.id,
                            status: e.target.value,
                          })
                        }
                        disabled={updateInsightMutation.isPending}
                        className="input w-full"
                      >
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="dismissed">Dismissed</option>
                      </select>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="card sticky top-8">
                  <div className="card-content p-8 text-center">
                    <Target className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                      Select an Insight
                    </h3>
                    <p className="text-secondary-600">
                      Choose an insight from the list to view detailed information
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Insights