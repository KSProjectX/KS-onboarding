import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: Date
  metadata?: {
    completeness?: number
    validation?: any
  }
}

interface SetupData {
  client_name?: string
  industry?: string
  problem_statement?: string
  tech_stack?: string | string[]
  timeline?: string
  budget?: string
  stakeholders?: string[]
  regions?: string[]
}

const ProgrammeSetup: React.FC = () => {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [setupData, setSetupData] = useState<SetupData>({})
  const [isComplete, setIsComplete] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Start conversation when component mounts
  const startConversationMutation = useMutation({
    mutationFn: () => ApiService.startConversation(`programme_setup_${Date.now()}`),
    onSuccess: (response) => {
      setConversationId(response.conversation_id)
      const botMessage: Message = {
        id: '1',
        type: 'bot',
        content: response.message,
        timestamp: new Date(),
      }
      setMessages([botMessage])
    },
    onError: (error: any) => {
      console.error('Start conversation error:', error)
      toast.error('Failed to start conversation')
    },
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) => {
      if (!conversationId) throw new Error('No conversation ID')
      return ApiService.sendMessage(conversationId, message)
    },
    onSuccess: (response) => {
      const botMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: response.message,
        timestamp: new Date(),
        metadata: {
          completeness: response.completion_percentage,
        },
      }
      setMessages((prev) => [...prev, botMessage])
      
      // Update setup data from client_info
      if (response.client_info) {
        setSetupData({
          client_name: response.client_info.company_name,
          industry: response.client_info.industry,
          problem_statement: response.client_info.problem_statement,
          tech_stack: response.client_info.tech_stack,
          timeline: response.client_info.timeline,
          budget: response.client_info.budget,
        })
      }
      
      setIsComplete(response.is_complete)
      
      if (response.is_complete) {
        toast.success('Programme setup completed!')
        setTimeout(() => {
          navigate('/profile')
        }, 2000)
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send message')
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: 'I apologize, but I encountered an error processing your message. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    },
  })

  // Start conversation on component mount
  useEffect(() => {
    startConversationMutation.mutate()
  }, [])

  const handleSendMessage = () => {
    if (!inputValue.trim() || sendMessageMutation.isPending || !conversationId) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    
    sendMessageMutation.mutate(inputValue)

    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getCompletenessColor = (completeness: number) => {
    if (completeness >= 90) return 'text-success-600'
    if (completeness >= 70) return 'text-warning-600'
    return 'text-danger-600'
  }

  const getCompletenessIcon = (completeness: number) => {
    if (completeness >= 90) return CheckCircle
    if (completeness >= 70) return AlertCircle
    return AlertCircle
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">
              Programme Setup
            </h1>
            <p className="text-secondary-600">
              Let's configure your K-Square programme through our conversational AI
            </p>
          </div>

          {/* Progress Bar */}
          {messages.length > 1 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card mb-6"
            >
              <div className="card-content p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-secondary-700">
                    Setup Progress
                  </span>
                  {messages[messages.length - 1]?.metadata?.completeness && (
                    <div className="flex items-center space-x-2">
                      {React.createElement(
                        getCompletenessIcon(messages[messages.length - 1].metadata!.completeness!),
                        {
                          className: `w-4 h-4 ${getCompletenessColor(
                            messages[messages.length - 1].metadata!.completeness!
                          )}`,
                        }
                      )}
                      <span
                        className={`text-sm font-medium ${
                          getCompletenessColor(messages[messages.length - 1].metadata!.completeness!)
                        }`}
                      >
                        {messages[messages.length - 1].metadata!.completeness}%
                      </span>
                    </div>
                  )}
                </div>
                <div className="w-full bg-secondary-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width: `${messages[messages.length - 1]?.metadata?.completeness || 0}%`,
                    }}
                    transition={{ duration: 0.5 }}
                    className="bg-primary-600 h-2 rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Chat Container */}
          <div className="card">
            <div className="card-content p-0">
              {/* Messages */}
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`flex items-start space-x-3 ${
                        message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <div
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          message.type === 'user'
                            ? 'bg-primary-600'
                            : 'bg-secondary-600'
                        }`}
                      >
                        {message.type === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div
                        className={`flex-1 max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl ${
                          message.type === 'user' ? 'text-right' : ''
                        }`}
                      >
                        <div
                          className={`inline-block p-3 rounded-lg ${
                            message.type === 'user'
                              ? 'bg-primary-600 text-white'
                              : 'bg-secondary-100 text-secondary-900'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">
                            {message.content}
                          </p>
                        </div>
                        <p className="text-xs text-secondary-500 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {sendMessageMutation.isPending && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-start space-x-3"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary-600 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="inline-block p-3 rounded-lg bg-secondary-100">
                        <div className="flex items-center space-x-2">
                          <Loader className="w-4 h-4 animate-spin text-secondary-600" />
                          <span className="text-sm text-secondary-600">
                            Thinking...
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-secondary-200 p-4">
                <div className="flex items-center space-x-3">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={isComplete ? 'Setup completed! You can ask follow-up questions...' : 'Type your message...'}
                    disabled={sendMessageMutation.isPending}
                    className="flex-1 input"
                  />
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || sendMessageMutation.isPending}
                    className="btn btn-primary p-2"
                  >
                    <Send className="w-4 h-4" />
                  </motion.button>
                </div>
              </div>
            </div>
          </div>

          {/* Setup Summary */}
          {isComplete && Object.keys(setupData).length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card mt-6"
            >
              <div className="card-content p-6">
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                  Setup Summary
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(setupData).map(([key, value]) => (
                    <div key={key} className="flex flex-col">
                      <span className="text-sm font-medium text-secondary-600 capitalize">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-secondary-900">
                        {Array.isArray(value) ? value.join(', ') : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default ProgrammeSetup