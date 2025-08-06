import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Building2,
  Users,
  MapPin,
  Calendar,
  TrendingUp,
  Edit3,
  Save,
  X,
  Plus,
  Trash2,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import StatCard from '../components/StatCard'

interface Stakeholder {
  name: string
  role: string
}

interface ClientProfile {
  id: string
  company_name: string
  industry: string
  company_size: string
  founding_year: number
  regions: string[]
  stakeholders: Stakeholder[]
  completeness_score: number
  insights: {
    market_position: string
    growth_potential: string
    risk_factors: string[]
    recommendations: string[]
  }
  created_at: string
  updated_at: string
}

const ClientProfile: React.FC = () => {
  const [selectedProfile, setSelectedProfile] = useState<ClientProfile | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState<Partial<ClientProfile>>({})
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newProfile, setNewProfile] = useState<Partial<ClientProfile>>({
    company_name: '',
    industry: '',
    company_size: '',
    founding_year: new Date().getFullYear(),
    regions: [],
    stakeholders: [],
  })

  const queryClient = useQueryClient()

  const {
    data: profilesResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['client-profiles'],
    queryFn: ApiService.getClientProfiles,
  })

  const profiles = profilesResponse?.data || []

  const createMutation = useMutation({
    mutationFn: ApiService.createClientProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-profiles'] })
      setShowCreateForm(false)
      setNewProfile({
        company_name: '',
        industry: '',
        company_size: '',
        founding_year: new Date().getFullYear(),
        regions: [],
        stakeholders: [],
      })
      toast.success('Client profile created successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create profile')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ClientProfile> }) =>
      ApiService.updateClientProfile(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-profiles'] })
      setIsEditing(false)
      setEditForm({})
      toast.success('Profile updated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update profile')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: ApiService.deleteClientProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-profiles'] })
      setSelectedProfile(null)
      toast.success('Profile deleted successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete profile')
    },
  })

  const handleEdit = (profile: ClientProfile) => {
    setEditForm(profile)
    setIsEditing(true)
  }

  const handleSave = () => {
    if (selectedProfile && editForm) {
      updateMutation.mutate({ id: selectedProfile.id, data: editForm })
    }
  }

  const handleCreate = () => {
    createMutation.mutate(newProfile)
  }

  const addArrayItem = (field: 'regions' | 'stakeholders', value: string, isEdit = false) => {
    if (!value.trim()) return
    
    let newItem: any = value.trim()
    if (field === 'stakeholders' && value.includes('|')) {
      const [name, role] = value.split('|')
      newItem = { name: name.trim(), role: role.trim() }
    }
    
    if (isEdit) {
      setEditForm(prev => ({
        ...prev,
        [field]: [...(prev[field] || []), newItem]
      }))
    } else {
      setNewProfile(prev => ({
        ...prev,
        [field]: [...(prev[field] || []), newItem]
      }))
    }
  }

  const removeArrayItem = (field: 'regions' | 'stakeholders', index: number, isEdit = false) => {
    if (isEdit) {
      setEditForm(prev => ({
        ...prev,
        [field]: prev[field]?.filter((_, i) => i !== index) || []
      }))
    } else {
      setNewProfile(prev => ({
        ...prev,
        [field]: prev[field]?.filter((_, i) => i !== index) || []
      }))
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading client profiles..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <ErrorMessage
          message="Failed to load client profiles"
          onRetry={refetch}
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
                Client Profiles
              </h1>
              <p className="text-secondary-600">
                Manage and analyze your client profiles
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowCreateForm(true)}
              className="btn btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Profile
            </motion.button>
          </div>

          {/* Stats */}
          {profiles && profiles.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Profiles"
                value={profiles.length}
                icon={Building2}
                color="primary"
              />
              <StatCard
                title="Avg Completeness"
                value={`${profiles.length > 0 ? Math.round(
                  profiles.reduce((acc: number, p: ClientProfile) => acc + p.completeness_score, 0) / profiles.length
                ) : 0}%`}
                icon={TrendingUp}
                color="success"
              />
              <StatCard
                title="Industries"
                value={new Set(profiles.map((p: ClientProfile) => p.industry)).size}
                icon={MapPin}
                color="info"
              />
              <StatCard
                title="Total Stakeholders"
                value={profiles.reduce((acc: number, p: ClientProfile) => acc + p.stakeholders.length, 0)}
                icon={Users}
                color="warning"
              />
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Profiles List */}
            <div className="lg:col-span-1">
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Profiles</h3>
                </div>
                <div className="card-content p-0">
                  <div className="max-h-96 overflow-y-auto">
                    {profiles && profiles.length > 0 ? (
                      <div className="space-y-1">
                        {profiles.map((profile: ClientProfile) => (
                          <motion.div
                            key={profile.id}
                            whileHover={{ backgroundColor: 'rgba(0, 0, 0, 0.02)' }}
                            onClick={() => setSelectedProfile(profile)}
                            className={`p-4 cursor-pointer border-l-4 transition-colors ${
                              selectedProfile?.id === profile.id
                                ? 'border-primary-600 bg-primary-50'
                                : 'border-transparent hover:bg-secondary-50'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <h4 className="font-medium text-secondary-900">
                                  {profile.company_name}
                                </h4>
                                <p className="text-sm text-secondary-600">
                                  {profile.industry}
                                </p>
                              </div>
                              <div className="text-right">
                                <div className={`text-xs font-medium ${
                                  profile.completeness_score >= 80
                                    ? 'text-success-600'
                                    : profile.completeness_score >= 60
                                    ? 'text-warning-600'
                                    : 'text-danger-600'
                                }`}>
                                  {profile.completeness_score}%
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-8 text-center">
                        <Building2 className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                        <p className="text-secondary-600 mb-4">
                          No client profiles yet
                        </p>
                        <button
                          onClick={() => setShowCreateForm(true)}
                          className="btn btn-primary"
                        >
                          Create First Profile
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Profile Details */}
            <div className="lg:col-span-2">
              {selectedProfile ? (
                <motion.div
                  key={selectedProfile.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="card"
                >
                  <div className="card-header">
                    <div className="flex items-center justify-between">
                      <h3 className="card-title">{selectedProfile.company_name}</h3>
                      <div className="flex items-center space-x-2">
                        {!isEditing ? (
                          <>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleEdit(selectedProfile)}
                              className="btn btn-secondary btn-sm"
                            >
                              <Edit3 className="w-4 h-4 mr-1" />
                              Edit
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => deleteMutation.mutate(selectedProfile.id)}
                              className="btn btn-danger btn-sm"
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Delete
                            </motion.button>
                          </>
                        ) : (
                          <>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={handleSave}
                              disabled={updateMutation.isPending}
                              className="btn btn-success btn-sm"
                            >
                              <Save className="w-4 h-4 mr-1" />
                              Save
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => {
                                setIsEditing(false)
                                setEditForm({})
                              }}
                              className="btn btn-secondary btn-sm"
                            >
                              <X className="w-4 h-4 mr-1" />
                              Cancel
                            </motion.button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="card-content p-6 space-y-6">
                    {/* Basic Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Company Name
                        </label>
                        {isEditing ? (
                          <input
                            type="text"
                            value={editForm.company_name || ''}
                            onChange={(e) => setEditForm(prev => ({ ...prev, company_name: e.target.value }))}
                            className="input"
                          />
                        ) : (
                          <p className="text-secondary-900">{selectedProfile.company_name}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Industry
                        </label>
                        {isEditing ? (
                          <input
                            type="text"
                            value={editForm.industry || ''}
                            onChange={(e) => setEditForm(prev => ({ ...prev, industry: e.target.value }))}
                            className="input"
                          />
                        ) : (
                          <p className="text-secondary-900">{selectedProfile.industry}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Company Size
                        </label>
                        {isEditing ? (
                          <select
                            value={editForm.company_size || ''}
                            onChange={(e) => setEditForm(prev => ({ ...prev, company_size: e.target.value }))}
                            className="input"
                          >
                            <option value="">Select size</option>
                            <option value="startup">Startup (1-10)</option>
                            <option value="small">Small (11-50)</option>
                            <option value="medium">Medium (51-200)</option>
                            <option value="large">Large (201-1000)</option>
                            <option value="enterprise">Enterprise (1000+)</option>
                          </select>
                        ) : (
                          <p className="text-secondary-900 capitalize">{selectedProfile.company_size}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Founded Year
                        </label>
                        {isEditing ? (
                          <input
                            type="number"
                            value={editForm.founding_year || ''}
                            onChange={(e) => setEditForm(prev => ({ ...prev, founding_year: parseInt(e.target.value) }))}
                            className="input"
                          />
                        ) : (
                          <p className="text-secondary-900">{selectedProfile.founding_year}</p>
                        )}
                      </div>
                    </div>

                    {/* Regions */}
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Regions
                      </label>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {(isEditing ? editForm.regions : selectedProfile.regions)?.map((region, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                          >
                            {region}
                            {isEditing && (
                              <button
                                onClick={() => removeArrayItem('regions', index, true)}
                                className="ml-1 text-primary-600 hover:text-primary-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            )}
                          </span>
                        ))}
                      </div>
                      {isEditing && (
                        <div className="flex space-x-2">
                          <input
                            type="text"
                            placeholder="Add region"
                            className="input flex-1"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                addArrayItem('regions', e.currentTarget.value, true)
                                e.currentTarget.value = ''
                              }
                            }}
                          />
                        </div>
                      )}
                    </div>

                    {/* Stakeholders */}
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Stakeholders
                      </label>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {(isEditing ? editForm.stakeholders : selectedProfile.stakeholders)?.map((stakeholder, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800"
                          >
                            <span className="font-medium">{typeof stakeholder === 'string' ? stakeholder : stakeholder.name}</span>
                            {typeof stakeholder === 'object' && stakeholder.role && (
                              <span className="ml-1 text-secondary-600">({stakeholder.role})</span>
                            )}
                            {isEditing && (
                              <button
                                onClick={() => removeArrayItem('stakeholders', index, true)}
                                className="ml-1 text-secondary-600 hover:text-secondary-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            )}
                          </span>
                        ))}
                      </div>
                      {isEditing && (
                        <div className="flex space-x-2">
                          <input
                            type="text"
                            placeholder="Stakeholder name"
                            className="input flex-1"
                            id="stakeholder-name"
                          />
                          <input
                            type="text"
                            placeholder="Role"
                            className="input flex-1"
                            id="stakeholder-role"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const nameInput = document.getElementById('stakeholder-name') as HTMLInputElement
                                const roleInput = e.currentTarget
                                if (nameInput.value.trim() && roleInput.value.trim()) {
                                  addArrayItem('stakeholders', `${nameInput.value.trim()}|${roleInput.value.trim()}`, true)
                                  nameInput.value = ''
                                  roleInput.value = ''
                                }
                              }
                            }}
                          />
                        </div>
                      )}
                    </div>

                    {/* Insights */}
                    {!isEditing && selectedProfile.insights && (
                      <div>
                        <h4 className="text-lg font-semibold text-secondary-900 mb-4">
                          Insights
                        </h4>
                        <div className="space-y-4">
                          <div>
                            <h5 className="font-medium text-secondary-700 mb-1">
                              Market Position
                            </h5>
                            <p className="text-secondary-600">
                              {selectedProfile.insights.market_position}
                            </p>
                          </div>
                          <div>
                            <h5 className="font-medium text-secondary-700 mb-1">
                              Growth Potential
                            </h5>
                            <p className="text-secondary-600">
                              {selectedProfile.insights.growth_potential}
                            </p>
                          </div>
                          <div>
                            <h5 className="font-medium text-secondary-700 mb-1">
                              Risk Factors
                            </h5>
                            <ul className="list-disc list-inside text-secondary-600 space-y-1">
                              {selectedProfile.insights.risk_factors.map((risk, index) => (
                                <li key={index}>{risk}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium text-secondary-700 mb-1">
                              Recommendations
                            </h5>
                            <ul className="list-disc list-inside text-secondary-600 space-y-1">
                              {selectedProfile.insights.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ) : (
                <div className="card">
                  <div className="card-content p-8 text-center">
                    <Building2 className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                      Select a Profile
                    </h3>
                    <p className="text-secondary-600">
                      Choose a client profile from the list to view details
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Create Profile Modal */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowCreateForm(false)}
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
                  <h3 className="card-title">Create New Profile</h3>
                  <button
                    onClick={() => setShowCreateForm(false)}
                    className="text-secondary-400 hover:text-secondary-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="card-content p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      value={newProfile.company_name || ''}
                      onChange={(e) => setNewProfile(prev => ({ ...prev, company_name: e.target.value }))}
                      className="input"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Industry *
                    </label>
                    <input
                      type="text"
                      value={newProfile.industry || ''}
                      onChange={(e) => setNewProfile(prev => ({ ...prev, industry: e.target.value }))}
                      className="input"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Company Size
                    </label>
                    <select
                      value={newProfile.company_size || ''}
                      onChange={(e) => setNewProfile(prev => ({ ...prev, company_size: e.target.value }))}
                      className="input"
                    >
                      <option value="">Select size</option>
                      <option value="startup">Startup (1-10)</option>
                      <option value="small">Small (11-50)</option>
                      <option value="medium">Medium (51-200)</option>
                      <option value="large">Large (201-1000)</option>
                      <option value="enterprise">Enterprise (1000+)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Founded Year
                    </label>
                    <input
                      type="number"
                      value={newProfile.founding_year || ''}
                      onChange={(e) => setNewProfile(prev => ({ ...prev, founding_year: parseInt(e.target.value) }))}
                      className="input"
                    />
                  </div>
                </div>

                {/* Regions */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Regions
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {newProfile.regions?.map((region, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        {region}
                        <button
                          onClick={() => removeArrayItem('regions', index, false)}
                          className="ml-1 text-primary-600 hover:text-primary-800"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Add region and press Enter"
                    className="input"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addArrayItem('regions', e.currentTarget.value, false)
                        e.currentTarget.value = ''
                      }
                    }}
                  />
                </div>

                {/* Stakeholders */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Stakeholders
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {newProfile.stakeholders?.map((stakeholder, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800"
                      >
                        <span className="font-medium">{typeof stakeholder === 'string' ? stakeholder : stakeholder.name}</span>
                        {typeof stakeholder === 'object' && stakeholder.role && (
                          <span className="ml-1 text-secondary-600">({stakeholder.role})</span>
                        )}
                        <button
                          onClick={() => removeArrayItem('stakeholders', index, false)}
                          className="ml-1 text-secondary-600 hover:text-secondary-800"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Stakeholder name"
                      className="input flex-1"
                      id="create-stakeholder-name"
                    />
                    <input
                      type="text"
                      placeholder="Role"
                      className="input flex-1"
                      id="create-stakeholder-role"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          const nameInput = document.getElementById('create-stakeholder-name') as HTMLInputElement
                          const roleInput = e.currentTarget
                          if (nameInput.value.trim() && roleInput.value.trim()) {
                            addArrayItem('stakeholders', `${nameInput.value.trim()}|${roleInput.value.trim()}`, false)
                            nameInput.value = ''
                            roleInput.value = ''
                          }
                        }
                      }}
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => setShowCreateForm(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreate}
                    disabled={!newProfile.company_name || !newProfile.industry || createMutation.isPending}
                    className="btn btn-primary"
                  >
                    {createMutation.isPending ? (
                      <LoadingSpinner size="sm" color="white" />
                    ) : (
                      'Create Profile'
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

export default ClientProfile