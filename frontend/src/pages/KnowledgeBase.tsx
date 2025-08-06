import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Book,
  Tag,
  Clock,
  TrendingUp,
  FileText,
  ExternalLink,
  Filter,
  Download,
  Bookmark,
  Share,
  Eye,
  ThumbsUp,
  MessageSquare,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

interface KnowledgeItem {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
  source: string
  relevance_score: number
  last_updated: string
  views: number
  likes: number
  bookmarked: boolean
  metadata: {
    industry?: string
    complexity?: 'beginner' | 'intermediate' | 'advanced'
    estimated_read_time?: number
    related_topics?: string[]
  }
}

interface SearchResult {
  items: KnowledgeItem[]
  total: number
  query: string
  suggestions: string[]
}

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedComplexity, setSelectedComplexity] = useState('all')
  const [selectedItem, setSelectedItem] = useState<KnowledgeItem | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const queryClient = useQueryClient()

  const {
    data: categories,
    isLoading: categoriesLoading,
  } = useQuery({
    queryKey: ['knowledge-categories'],
    queryFn: ApiService.getKnowledgeCategories,
  })

  const {
    data: popularItems,
    isLoading: popularLoading,
  } = useQuery({
    queryKey: ['popular-knowledge'],
    queryFn: ApiService.getPopularKnowledge,
  })

  const searchMutation = useMutation({
    mutationFn: (params: { query: string; category?: string; complexity?: string }) =>
      ApiService.searchKnowledge(params),
    onSuccess: (data) => {
      setSearchResults(data)
      setIsSearching(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Search failed')
      setIsSearching(false)
    },
  })

  const bookmarkMutation = useMutation({
    mutationFn: ({ id, bookmarked }: { id: string; bookmarked: boolean }) =>
      ApiService.toggleBookmark(id, bookmarked),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['popular-knowledge'] })
      if (searchResults) {
        setSearchResults({
          ...searchResults,
          items: searchResults.items.map(item =>
            item.id === selectedItem?.id
              ? { ...item, bookmarked: !item.bookmarked }
              : item
          ),
        })
      }
      if (selectedItem) {
        setSelectedItem({ ...selectedItem, bookmarked: !selectedItem.bookmarked })
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update bookmark')
    },
  })

  const likeMutation = useMutation({
    mutationFn: (id: string) => ApiService.likeKnowledgeItem(id),
    onSuccess: () => {
      if (selectedItem) {
        setSelectedItem({ ...selectedItem, likes: selectedItem.likes + 1 })
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to like item')
    },
  })

  const handleSearch = (query: string) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (!query.trim()) {
      setSearchResults(null)
      return
    }

    setIsSearching(true)
    searchTimeoutRef.current = setTimeout(() => {
      searchMutation.mutate({
        query,
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
        complexity: selectedComplexity !== 'all' ? selectedComplexity : undefined,
      })
    }, 500)
  }

  useEffect(() => {
    handleSearch(searchQuery)
  }, [searchQuery, selectedCategory, selectedComplexity])

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'beginner':
        return 'text-success-600 bg-success-100'
      case 'intermediate':
        return 'text-warning-600 bg-warning-100'
      case 'advanced':
        return 'text-danger-600 bg-danger-100'
      default:
        return 'text-secondary-600 bg-secondary-100'
    }
  }

  const formatReadTime = (minutes: number) => {
    return `${minutes} min read`
  }

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    )
  }

  const displayItems = searchResults?.items || popularItems || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">
              Knowledge Base
            </h1>
            <p className="text-secondary-600 mb-6">
              Search through our comprehensive database of industry insights and best practices
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for insights, best practices, case studies..."
                  className="w-full pl-10 pr-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                {isSearching && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <LoadingSpinner size="sm" />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowFilters(!showFilters)}
                className="btn btn-secondary"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </motion.button>
              
              {searchResults && (
                <div className="text-sm text-secondary-600">
                  {searchResults.total} results for "{searchResults.query}"
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <button className="btn btn-secondary btn-sm">
                <Download className="w-4 h-4 mr-1" />
                Export
              </button>
              <button className="btn btn-secondary btn-sm">
                <Share className="w-4 h-4 mr-1" />
                Share
              </button>
            </div>
          </div>

          {/* Filter Panel */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="card mb-6"
              >
                <div className="card-content p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-1">
                        Category
                      </label>
                      <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        className="input w-full"
                      >
                        <option value="all">All Categories</option>
                        {categories?.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-1">
                        Complexity
                      </label>
                      <select
                        value={selectedComplexity}
                        onChange={(e) => setSelectedComplexity(e.target.value)}
                        className="input w-full"
                      >
                        <option value="all">All Levels</option>
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                      </select>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Search Suggestions */}
          {searchResults?.suggestions && searchResults.suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <p className="text-sm text-secondary-600 mb-2">Did you mean:</p>
              <div className="flex flex-wrap gap-2">
                {searchResults.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setSearchQuery(suggestion)}
                    className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm hover:bg-primary-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Results List */}
            <div className="lg:col-span-2">
              <div className="space-y-4">
                {displayItems.length > 0 ? (
                  displayItems.map((item) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      whileHover={{ y: -2 }}
                      onClick={() => setSelectedItem(item)}
                      className={`card cursor-pointer transition-all hover:shadow-medium ${
                        selectedItem?.id === item.id
                          ? 'ring-2 ring-primary-500'
                          : ''
                      }`}
                    >
                      <div className="card-content p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="font-semibold text-secondary-900 mb-2">
                              {searchQuery ? highlightText(item.title, searchQuery) : item.title}
                            </h3>
                            <p className="text-sm text-secondary-600 line-clamp-2 mb-3">
                              {searchQuery ? highlightText(item.content.substring(0, 150) + '...', searchQuery) : item.content.substring(0, 150) + '...'}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2 ml-4">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                bookmarkMutation.mutate({ id: item.id, bookmarked: !item.bookmarked })
                              }}
                              className={`p-1 rounded ${item.bookmarked ? 'text-warning-600' : 'text-secondary-400 hover:text-warning-600'}`}
                            >
                              <Bookmark className={`w-4 h-4 ${item.bookmarked ? 'fill-current' : ''}`} />
                            </button>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-xs text-secondary-500">
                            <div className="flex items-center space-x-1">
                              <Tag className="w-3 h-3" />
                              <span>{item.category}</span>
                            </div>
                            {item.metadata.complexity && (
                              <span className={`px-2 py-1 rounded-full font-medium ${getComplexityColor(item.metadata.complexity)}`}>
                                {item.metadata.complexity}
                              </span>
                            )}
                            {item.metadata.estimated_read_time && (
                              <div className="flex items-center space-x-1">
                                <Clock className="w-3 h-3" />
                                <span>{formatReadTime(item.metadata.estimated_read_time)}</span>
                              </div>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-3 text-xs text-secondary-500">
                            <div className="flex items-center space-x-1">
                              <Eye className="w-3 h-3" />
                              <span>{item.views}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <ThumbsUp className="w-3 h-3" />
                              <span>{item.likes}</span>
                            </div>
                            {searchResults && (
                              <div className="flex items-center space-x-1">
                                <TrendingUp className="w-3 h-3" />
                                <span>{(item.relevance_score * 100).toFixed(0)}%</span>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {item.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-3">
                            {item.tags.slice(0, 3).map((tag, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded text-xs"
                              >
                                {tag}
                              </span>
                            ))}
                            {item.tags.length > 3 && (
                              <span className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded text-xs">
                                +{item.tags.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="card">
                    <div className="card-content p-8 text-center">
                      {isSearching ? (
                        <LoadingSpinner size="lg" text="Searching knowledge base..." />
                      ) : searchQuery ? (
                        <>
                          <Search className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                          <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                            No Results Found
                          </h3>
                          <p className="text-secondary-600 mb-4">
                            No knowledge items match your search criteria
                          </p>
                          <button
                            onClick={() => {
                              setSearchQuery('')
                              setSelectedCategory('all')
                              setSelectedComplexity('all')
                            }}
                            className="btn btn-primary"
                          >
                            Clear Search
                          </button>
                        </>
                      ) : (
                        <>
                          <Book className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                          <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                            Welcome to Knowledge Base
                          </h3>
                          <p className="text-secondary-600">
                            Start searching to discover insights and best practices
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Item Details */}
            <div className="lg:col-span-1">
              {selectedItem ? (
                <motion.div
                  key={selectedItem.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="card sticky top-8"
                >
                  <div className="card-header">
                    <div className="flex items-start justify-between">
                      <h3 className="card-title pr-4">{selectedItem.title}</h3>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => bookmarkMutation.mutate({ id: selectedItem.id, bookmarked: !selectedItem.bookmarked })}
                          className={`p-1 rounded ${selectedItem.bookmarked ? 'text-warning-600' : 'text-secondary-400 hover:text-warning-600'}`}
                        >
                          <Bookmark className={`w-4 h-4 ${selectedItem.bookmarked ? 'fill-current' : ''}`} />
                        </button>
                        <button
                          onClick={() => likeMutation.mutate(selectedItem.id)}
                          className="p-1 rounded text-secondary-400 hover:text-primary-600"
                        >
                          <ThumbsUp className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="card-content p-6 space-y-4">
                    {/* Metadata */}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-2">
                        <span className="text-secondary-600">{selectedItem.category}</span>
                        {selectedItem.metadata.complexity && (
                          <span className={`px-2 py-1 rounded-full font-medium ${getComplexityColor(selectedItem.metadata.complexity)}`}>
                            {selectedItem.metadata.complexity}
                          </span>
                        )}
                      </div>
                      {selectedItem.metadata.estimated_read_time && (
                        <div className="flex items-center space-x-1 text-secondary-500">
                          <Clock className="w-3 h-3" />
                          <span>{formatReadTime(selectedItem.metadata.estimated_read_time)}</span>
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="prose prose-sm max-w-none">
                      <div className="text-secondary-700 leading-relaxed whitespace-pre-wrap">
                        {selectedItem.content}
                      </div>
                    </div>

                    {/* Tags */}
                    {selectedItem.tags.length > 0 && (
                      <div>
                        <h4 className="font-medium text-secondary-900 mb-2">Tags</h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedItem.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs cursor-pointer hover:bg-primary-200"
                              onClick={() => setSearchQuery(tag)}
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Related Topics */}
                    {selectedItem.metadata.related_topics && selectedItem.metadata.related_topics.length > 0 && (
                      <div>
                        <h4 className="font-medium text-secondary-900 mb-2">Related Topics</h4>
                        <div className="space-y-1">
                          {selectedItem.metadata.related_topics.map((topic, index) => (
                            <button
                              key={index}
                              onClick={() => setSearchQuery(topic)}
                              className="block text-sm text-primary-600 hover:text-primary-800 hover:underline"
                            >
                              {topic}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="border-t border-secondary-200 pt-4">
                      <div className="grid grid-cols-2 gap-4 text-center">
                        <div>
                          <div className="text-lg font-semibold text-secondary-900">
                            {selectedItem.views}
                          </div>
                          <div className="text-xs text-secondary-600">Views</div>
                        </div>
                        <div>
                          <div className="text-lg font-semibold text-secondary-900">
                            {selectedItem.likes}
                          </div>
                          <div className="text-xs text-secondary-600">Likes</div>
                        </div>
                      </div>
                    </div>

                    {/* Source */}
                    <div className="border-t border-secondary-200 pt-4">
                      <div className="flex items-center justify-between text-xs text-secondary-500">
                        <span>Source: {selectedItem.source}</span>
                        <span>{new Date(selectedItem.last_updated).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="card sticky top-8">
                  <div className="card-content p-8 text-center">
                    <Book className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                      Select an Item
                    </h3>
                    <p className="text-secondary-600">
                      Choose a knowledge item to view detailed information
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

export default KnowledgeBase