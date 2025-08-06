import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Users,
  Clock,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  FileText,
  Upload,
  Play,
  Pause,
  Volume2,
  Download,
  Eye,
  Plus,
  X,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import StatCard from '../components/StatCard'

interface Meeting {
  id: string
  title: string
  date: string
  duration: number
  participants: string[]
  transcript: string
  sentiment_score: number
  engagement_score: number
  action_items: string[]
  key_topics: string[]
  summary: string
  insights: {
    positive_sentiment: number
    negative_sentiment: number
    neutral_sentiment: number
    key_decisions: string[]
    concerns_raised: string[]
    next_steps: string[]
  }
  created_at: string
  updated_at: string
}

interface MeetingsSummary {
  total_meetings: number
  total_duration: number
  average_sentiment: number
  average_engagement: number
  total_action_items: number
  completed_action_items: number
}

const Meetings: React.FC = () => {
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploadParticipants, setUploadParticipants] = useState<string[]>([])
  const [newParticipant, setNewParticipant] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const queryClient = useQueryClient()

  const {
    data: meetings,
    isLoading: meetingsLoading,
    error: meetingsError,
    refetch: refetchMeetings,
  } = useQuery({
    queryKey: ['meetings'],
    queryFn: () => ApiService.getMeetings(),
  })

  const meetingsData = meetings?.data || []

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useQuery({
    queryKey: ['meetings-summary'],
    queryFn: ApiService.getMeetingsSummary,
  })

  const uploadMutation = useMutation({
    mutationFn: (data: FormData) => ApiService.uploadMeeting(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      queryClient.invalidateQueries({ queryKey: ['meetings-summary'] })
      setShowUploadModal(false)
      setUploadFile(null)
      setUploadTitle('')
      setUploadParticipants([])
      toast.success('Meeting uploaded and analyzed successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload meeting')
    },
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadFile(file)
      if (!uploadTitle) {
        setUploadTitle(file.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const addParticipant = () => {
    if (newParticipant.trim() && !uploadParticipants.includes(newParticipant.trim())) {
      setUploadParticipants([...uploadParticipants, newParticipant.trim()])
      setNewParticipant('')
    }
  }

  const removeParticipant = (index: number) => {
    setUploadParticipants(uploadParticipants.filter((_, i) => i !== index))
  }

  const handleUpload = () => {
    if (!uploadFile || !uploadTitle.trim()) {
      toast.error('Please provide a file and title')
      return
    }

    const formData = new FormData()
    formData.append('file', uploadFile)
    formData.append('title', uploadTitle)
    formData.append('participants', JSON.stringify(uploadParticipants))

    uploadMutation.mutate(formData)
  }

  const getSentimentColor = (score: number) => {
    if (score >= 0.6) return 'text-success-600'
    if (score >= 0.4) return 'text-warning-600'
    return 'text-danger-600'
  }

  const getSentimentIcon = (score: number) => {
    if (score >= 0.6) return TrendingUp
    if (score >= 0.4) return MessageSquare
    return TrendingDown
  }

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }

  if (meetingsLoading || summaryLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading meetings..." />
      </div>
    )
  }

  if (meetingsError || summaryError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <ErrorMessage
          message="Failed to load meetings"
          onRetry={refetchMeetings}
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
                Meeting Analysis
              </h1>
              <p className="text-secondary-600">
                Upload and analyze meeting transcripts for insights and action items
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowUploadModal(true)}
              className="btn btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Upload Meeting
            </motion.button>
          </div>

          {/* Summary Stats */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Meetings"
                value={summary.data?.total_meetings || 0}
                icon={Calendar}
                color="primary"
              />
              <StatCard
                title="Total Duration"
                value={formatDuration(summary.data?.total_duration || 0)}
                icon={Clock}
                color="info"
              />
              <StatCard
                title="Avg Sentiment"
                value={`${((summary.data?.average_sentiment || 0) * 100).toFixed(0)}%`}
                icon={getSentimentIcon(summary.data?.average_sentiment || 0)}
                color={(summary.data?.average_sentiment || 0) >= 0.6 ? 'success' : (summary.data?.average_sentiment || 0) >= 0.4 ? 'warning' : 'danger'}
                trend={{
                  value: 12.5,
                  isPositive: (summary.data?.average_sentiment || 0) >= 0.5,
                }}
              />
              <StatCard
                title="Action Items"
                value={`${summary.data?.completed_action_items || 0}/${summary.data?.total_action_items || 0}`}
                icon={FileText}
                color="warning"
                subtitle="Completed"
              />
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Meetings List */}
            <div className="lg:col-span-1">
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Recent Meetings</h3>
                </div>
                <div className="card-content p-0">
                  <div className="max-h-96 overflow-y-auto">
                    {meetingsData && meetingsData.length > 0 ? (
                      <div className="space-y-1">
                        {meetingsData.map((meeting: Meeting) => {
                          const SentimentIcon = getSentimentIcon(meeting.sentiment_score)
                          return (
                            <motion.div
                              key={meeting.id}
                              whileHover={{ backgroundColor: 'rgba(0, 0, 0, 0.02)' }}
                              onClick={() => setSelectedMeeting(meeting)}
                              className={`p-4 cursor-pointer border-l-4 transition-colors ${
                                selectedMeeting?.id === meeting.id
                                  ? 'border-primary-600 bg-primary-50'
                                  : 'border-transparent hover:bg-secondary-50'
                              }`}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                  <h4 className="font-medium text-secondary-900 mb-1">
                                    {meeting.title}
                                  </h4>
                                  <p className="text-xs text-secondary-500">
                                    {new Date(meeting.date).toLocaleDateString()}
                                  </p>
                                </div>
                                <SentimentIcon
                                  className={`w-4 h-4 ${getSentimentColor(meeting.sentiment_score)}`}
                                />
                              </div>
                              
                              <div className="flex items-center justify-between text-xs text-secondary-600">
                                <div className="flex items-center space-x-3">
                                  <div className="flex items-center space-x-1">
                                    <Clock className="w-3 h-3" />
                                    <span>{formatDuration(meeting.duration)}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Users className="w-3 h-3" />
                                    <span>{meeting.participants?.length || 0}</span>
                                  </div>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <FileText className="w-3 h-3" />
                                  <span>{meeting.action_items?.length || 0}</span>
                                </div>
                              </div>
                            </motion.div>
                          )
                        })}
                      </div>
                    ) : (
                      <div className="p-8 text-center">
                        <Calendar className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                        <p className="text-secondary-600 mb-4">
                          No meetings uploaded yet
                        </p>
                        <button
                          onClick={() => setShowUploadModal(true)}
                          className="btn btn-primary"
                        >
                          Upload First Meeting
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Meeting Details */}
            <div className="lg:col-span-2">
              {selectedMeeting ? (
                <motion.div
                  key={selectedMeeting.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  {/* Meeting Header */}
                  <div className="card">
                    <div className="card-content p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                            {selectedMeeting.title}
                          </h3>
                          <div className="flex items-center space-x-4 text-sm text-secondary-600">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-4 h-4" />
                              <span>{new Date(selectedMeeting.date).toLocaleDateString()}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{formatDuration(selectedMeeting.duration)}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Users className="w-4 h-4" />
                              <span>{selectedMeeting.participants?.length || 0} participants</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`text-sm font-medium ${getSentimentColor(selectedMeeting.sentiment_score)}`}>
                            Sentiment: {(selectedMeeting.sentiment_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-secondary-900 mb-2">Participants</h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedMeeting.participants?.map((participant, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs font-medium"
                              >
                                {participant}
                              </span>
                            )) || []}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium text-secondary-900 mb-2">Key Topics</h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedMeeting.key_topics?.map((topic, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-secondary-100 text-secondary-800 rounded-full text-xs font-medium"
                              >
                                {topic}
                              </span>
                            )) || []}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Meeting Summary */}
                  <div className="card">
                    <div className="card-header">
                      <h4 className="card-title">Summary</h4>
                    </div>
                    <div className="card-content p-6">
                      <p className="text-secondary-700 leading-relaxed">
                        {selectedMeeting.summary}
                      </p>
                    </div>
                  </div>

                  {/* Action Items */}
                  <div className="card">
                    <div className="card-header">
                      <h4 className="card-title">Action Items</h4>
                    </div>
                    <div className="card-content p-6">
                      {selectedMeeting.action_items?.length > 0 ? (
                        <div className="space-y-3">
                          {selectedMeeting.action_items?.map((item, index) => (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.1 }}
                              className="flex items-start space-x-3 p-3 bg-warning-50 border border-warning-200 rounded-lg"
                            >
                              <FileText className="w-4 h-4 text-warning-600 mt-0.5 flex-shrink-0" />
                              <span className="text-secondary-700">{item}</span>
                            </motion.div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-secondary-500 text-center py-4">
                          No action items identified
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Insights */}
                  <div className="card">
                    <div className="card-header">
                      <h4 className="card-title">Insights</h4>
                    </div>
                    <div className="card-content p-6 space-y-6">
                      {/* Sentiment Breakdown */}
                      <div>
                        <h5 className="font-medium text-secondary-900 mb-3">Sentiment Analysis</h5>
                        <div className="grid grid-cols-3 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-success-600">
                              {((selectedMeeting.insights?.positive_sentiment || 0) * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-secondary-600">Positive</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-secondary-600">
                              {((selectedMeeting.insights?.neutral_sentiment || 0) * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-secondary-600">Neutral</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-danger-600">
                              {((selectedMeeting.insights?.negative_sentiment || 0) * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-secondary-600">Negative</div>
                          </div>
                        </div>
                      </div>

                      {/* Key Decisions */}
                      {selectedMeeting.insights?.key_decisions?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-secondary-900 mb-2">Key Decisions</h5>
                          <ul className="space-y-2">
                            {selectedMeeting.insights?.key_decisions?.map((decision, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <TrendingUp className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                                <span className="text-secondary-700">{decision}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Concerns */}
                      {selectedMeeting.insights?.concerns_raised?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-secondary-900 mb-2">Concerns Raised</h5>
                          <ul className="space-y-2">
                            {selectedMeeting.insights?.concerns_raised?.map((concern, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <TrendingDown className="w-4 h-4 text-danger-600 mt-0.5 flex-shrink-0" />
                                <span className="text-secondary-700">{concern}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Next Steps */}
                      {selectedMeeting.insights?.next_steps?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-secondary-900 mb-2">Next Steps</h5>
                          <ul className="space-y-2">
                            {selectedMeeting.insights?.next_steps?.map((step, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <MessageSquare className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
                                <span className="text-secondary-700">{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Transcript */}
                  <div className="card">
                    <div className="card-header">
                      <h4 className="card-title">Transcript</h4>
                    </div>
                    <div className="card-content p-6">
                      <div className="max-h-64 overflow-y-auto bg-secondary-50 p-4 rounded-lg">
                        <pre className="text-sm text-secondary-700 whitespace-pre-wrap font-mono">
                          {selectedMeeting.transcript}
                        </pre>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="card">
                  <div className="card-content p-8 text-center">
                    <Calendar className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                      Select a Meeting
                    </h3>
                    <p className="text-secondary-600">
                      Choose a meeting from the list to view detailed analysis
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h3 className="card-title">Upload Meeting</h3>
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="text-secondary-400 hover:text-secondary-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="card-content p-6 space-y-6">
                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Meeting File (Audio/Video/Text)
                  </label>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-secondary-300 rounded-lg p-6 text-center cursor-pointer hover:border-primary-500 transition-colors"
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileSelect}
                      accept=".mp3,.mp4,.wav,.txt,.docx,.pdf"
                      className="hidden"
                    />
                    {uploadFile ? (
                      <div className="flex items-center justify-center space-x-2">
                        <FileText className="w-5 h-5 text-primary-600" />
                        <span className="text-secondary-700">{uploadFile.name}</span>
                      </div>
                    ) : (
                      <div>
                        <Upload className="w-8 h-8 text-secondary-400 mx-auto mb-2" />
                        <p className="text-secondary-600">Click to upload meeting file</p>
                        <p className="text-xs text-secondary-500 mt-1">
                          Supports audio, video, and text files
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Meeting Title */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Meeting Title *
                  </label>
                  <input
                    type="text"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    placeholder="Enter meeting title"
                    className="input w-full"
                    required
                  />
                </div>

                {/* Participants */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Participants
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {uploadParticipants.map((participant, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        {participant}
                        <button
                          onClick={() => removeParticipant(index)}
                          className="ml-1 text-primary-600 hover:text-primary-800"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newParticipant}
                      onChange={(e) => setNewParticipant(e.target.value)}
                      placeholder="Add participant"
                      className="input flex-1"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          addParticipant()
                        }
                      }}
                    />
                    <button
                      onClick={addParticipant}
                      className="btn btn-secondary"
                    >
                      Add
                    </button>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={!uploadFile || !uploadTitle.trim() || uploadMutation.isPending}
                    className="btn btn-primary"
                  >
                    {uploadMutation.isPending ? (
                      <LoadingSpinner size="sm" color="white" />
                    ) : (
                      'Upload & Analyze'
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Meetings