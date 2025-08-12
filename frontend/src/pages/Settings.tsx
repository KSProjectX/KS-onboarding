import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Shield,
  Database,
  Palette,
  Globe,
  Download,
  Upload,
  Trash2,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  Check,
  X,
  AlertTriangle,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ApiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

interface UserSettings {
  profile: {
    name: string
    email: string
    role: string
    avatar?: string
  }
  notifications: {
    email_enabled: boolean
    push_enabled: boolean
    workflow_updates: boolean
    insight_alerts: boolean
    meeting_reminders: boolean
    weekly_summary: boolean
  }
  privacy: {
    data_sharing: boolean
    analytics: boolean
    crash_reports: boolean
    usage_statistics: boolean
  }
  appearance: {
    theme: 'light' | 'dark' | 'auto'
    language: string
    timezone: string
    date_format: string
  }
  system: {
    auto_save: boolean
    session_timeout: number
    max_file_size: number
    backup_frequency: 'daily' | 'weekly' | 'monthly'
  }
}

interface SystemInfo {
  version: string
  last_backup: string
  storage_used: number
  storage_limit: number
  active_sessions: number
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile')
  const [showPassword, setShowPassword] = useState(false)
  const [pendingChanges, setPendingChanges] = useState(false)
  const [localSettings, setLocalSettings] = useState<UserSettings | null>(null)

  const queryClient = useQueryClient()

  const {
    data: settings,
    isLoading: settingsLoading,
    error: settingsError,
  } = useQuery({
    queryKey: ['user-settings'],
    queryFn: ApiService.getUserSettings,
    onSuccess: (data) => {
      setLocalSettings(data)
    },
  })

  const {
    data: systemInfo,
    isLoading: systemLoading,
  } = useQuery({
    queryKey: ['system-info'],
    queryFn: ApiService.getSystemInfo,
  })

  const updateSettingsMutation = useMutation({
    mutationFn: (settings: Partial<UserSettings>) =>
      ApiService.updateUserSettings(settings),
    onSuccess: () => {
      toast.success('Settings updated successfully')
      setPendingChanges(false)
      queryClient.invalidateQueries({ queryKey: ['user-settings'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update settings')
    },
  })

  const exportDataMutation = useMutation({
    mutationFn: ApiService.exportUserData,
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ks-onboarding-data-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('Data exported successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to export data')
    },
  })

  const resetSettingsMutation = useMutation({
    mutationFn: ApiService.resetUserSettings,
    onSuccess: () => {
      toast.success('Settings reset to defaults')
      setPendingChanges(false)
      queryClient.invalidateQueries({ queryKey: ['user-settings'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to reset settings')
    },
  })

  const handleSettingChange = (section: keyof UserSettings, key: string, value: any) => {
    if (!localSettings) return

    const updatedSettings = {
      ...localSettings,
      [section]: {
        ...localSettings[section],
        [key]: value,
      },
    }
    setLocalSettings(updatedSettings)
    setPendingChanges(true)
  }

  const handleSaveSettings = () => {
    if (localSettings) {
      updateSettingsMutation.mutate(localSettings)
    }
  }

  const handleResetSettings = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
      resetSettingsMutation.mutate()
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'system', label: 'System', icon: Database },
  ]

  if (settingsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading settings..." />
      </div>
    )
  }

  if (settingsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <ErrorMessage
          title="Failed to Load Settings"
          message="Unable to load your settings. Please try again."
          onRetry={() => queryClient.invalidateQueries({ queryKey: ['user-settings'] })}
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
          className="max-w-6xl mx-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900 mb-2">
                Settings
              </h1>
              <p className="text-secondary-600">
                Manage your account preferences and system configuration
              </p>
            </div>
            
            {pendingChanges && (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-warning-600">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm">Unsaved changes</span>
                </div>
                <button
                  onClick={handleSaveSettings}
                  disabled={updateSettingsMutation.isLoading}
                  className="btn btn-primary"
                >
                  {updateSettingsMutation.isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="card">
                <div className="card-content p-0">
                  <nav className="space-y-1">
                    {tabs.map((tab) => {
                      const Icon = tab.icon
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`w-full flex items-center space-x-3 px-4 py-3 text-left transition-colors ${
                            activeTab === tab.id
                              ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                              : 'text-secondary-600 hover:bg-secondary-50'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          <span className="font-medium">{tab.label}</span>
                        </button>
                      )
                    })}
                  </nav>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="lg:col-span-3">
              <div className="card">
                <div className="card-content p-6">
                  {/* Profile Settings */}
                  {activeTab === 'profile' && localSettings && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Profile Information
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Full Name
                            </label>
                            <input
                              type="text"
                              value={localSettings.profile.name}
                              onChange={(e) => handleSettingChange('profile', 'name', e.target.value)}
                              className="input w-full"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Email Address
                            </label>
                            <input
                              type="email"
                              value={localSettings.profile.email}
                              onChange={(e) => handleSettingChange('profile', 'email', e.target.value)}
                              className="input w-full"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Role
                            </label>
                            <select
                              value={localSettings.profile.role}
                              onChange={(e) => handleSettingChange('profile', 'role', e.target.value)}
                              className="input w-full"
                            >
                              <option value="admin">Administrator</option>
                              <option value="manager">Manager</option>
                              <option value="analyst">Analyst</option>
                              <option value="viewer">Viewer</option>
                            </select>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Security
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Current Password
                            </label>
                            <div className="relative">
                              <input
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Enter current password"
                                className="input w-full pr-10"
                              />
                              <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                              >
                                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </button>
                            </div>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              New Password
                            </label>
                            <input
                              type="password"
                              placeholder="Enter new password"
                              className="input w-full"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Confirm New Password
                            </label>
                            <input
                              type="password"
                              placeholder="Confirm new password"
                              className="input w-full"
                            />
                          </div>
                          <button className="btn btn-secondary">
                            Update Password
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Notification Settings */}
                  {activeTab === 'notifications' && localSettings && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Notification Preferences
                        </h3>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Email Notifications</h4>
                              <p className="text-sm text-secondary-600">Receive notifications via email</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.email_enabled}
                                onChange={(e) => handleSettingChange('notifications', 'email_enabled', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Push Notifications</h4>
                              <p className="text-sm text-secondary-600">Receive browser push notifications</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.push_enabled}
                                onChange={(e) => handleSettingChange('notifications', 'push_enabled', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Workflow Updates</h4>
                              <p className="text-sm text-secondary-600">Get notified about workflow progress</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.workflow_updates}
                                onChange={(e) => handleSettingChange('notifications', 'workflow_updates', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Insight Alerts</h4>
                              <p className="text-sm text-secondary-600">Receive alerts for new insights</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.insight_alerts}
                                onChange={(e) => handleSettingChange('notifications', 'insight_alerts', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Meeting Reminders</h4>
                              <p className="text-sm text-secondary-600">Get reminded about upcoming meetings</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.meeting_reminders}
                                onChange={(e) => handleSettingChange('notifications', 'meeting_reminders', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Weekly Summary</h4>
                              <p className="text-sm text-secondary-600">Receive weekly progress summaries</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.notifications.weekly_summary}
                                onChange={(e) => handleSettingChange('notifications', 'weekly_summary', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Privacy Settings */}
                  {activeTab === 'privacy' && localSettings && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Privacy & Data
                        </h3>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Data Sharing</h4>
                              <p className="text-sm text-secondary-600">Allow sharing anonymized data for improvements</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.privacy.data_sharing}
                                onChange={(e) => handleSettingChange('privacy', 'data_sharing', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Analytics</h4>
                              <p className="text-sm text-secondary-600">Enable usage analytics and tracking</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.privacy.analytics}
                                onChange={(e) => handleSettingChange('privacy', 'analytics', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Crash Reports</h4>
                              <p className="text-sm text-secondary-600">Automatically send crash reports</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.privacy.crash_reports}
                                onChange={(e) => handleSettingChange('privacy', 'crash_reports', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Usage Statistics</h4>
                              <p className="text-sm text-secondary-600">Collect usage statistics for optimization</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.privacy.usage_statistics}
                                onChange={(e) => handleSettingChange('privacy', 'usage_statistics', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Data Management
                        </h3>
                        <div className="space-y-3">
                          <button
                            onClick={() => exportDataMutation.mutate()}
                            disabled={exportDataMutation.isLoading}
                            className="btn btn-secondary w-full justify-start"
                          >
                            {exportDataMutation.isLoading ? (
                              <LoadingSpinner size="sm" />
                            ) : (
                              <Download className="w-4 h-4 mr-2" />
                            )}
                            Export My Data
                          </button>
                          <button className="btn btn-secondary w-full justify-start">
                            <Upload className="w-4 h-4 mr-2" />
                            Import Data
                          </button>
                          <button className="btn btn-danger w-full justify-start">
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete All Data
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Appearance Settings */}
                  {activeTab === 'appearance' && localSettings && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Appearance & Localization
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Theme
                            </label>
                            <select
                              value={localSettings.appearance.theme}
                              onChange={(e) => handleSettingChange('appearance', 'theme', e.target.value)}
                              className="input w-full"
                            >
                              <option value="light">Light</option>
                              <option value="dark">Dark</option>
                              <option value="auto">Auto (System)</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Language
                            </label>
                            <select
                              value={localSettings.appearance.language}
                              onChange={(e) => handleSettingChange('appearance', 'language', e.target.value)}
                              className="input w-full"
                            >
                              <option value="en">English</option>
                              <option value="es">Español</option>
                              <option value="fr">Français</option>
                              <option value="de">Deutsch</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Timezone
                            </label>
                            <select
                              value={localSettings.appearance.timezone}
                              onChange={(e) => handleSettingChange('appearance', 'timezone', e.target.value)}
                              className="input w-full"
                            >
                              <option value="UTC">UTC</option>
                              <option value="America/New_York">Eastern Time</option>
                              <option value="America/Chicago">Central Time</option>
                              <option value="America/Denver">Mountain Time</option>
                              <option value="America/Los_Angeles">Pacific Time</option>
                              <option value="Europe/London">London</option>
                              <option value="Europe/Paris">Paris</option>
                              <option value="Asia/Tokyo">Tokyo</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Date Format
                            </label>
                            <select
                              value={localSettings.appearance.date_format}
                              onChange={(e) => handleSettingChange('appearance', 'date_format', e.target.value)}
                              className="input w-full"
                            >
                              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                              <option value="DD MMM YYYY">DD MMM YYYY</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* System Settings */}
                  {activeTab === 'system' && localSettings && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          System Configuration
                        </h3>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-secondary-900">Auto Save</h4>
                              <p className="text-sm text-secondary-600">Automatically save changes</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={localSettings.system.auto_save}
                                onChange={(e) => handleSettingChange('system', 'auto_save', e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Session Timeout (minutes)
                            </label>
                            <input
                              type="number"
                              min="5"
                              max="480"
                              value={localSettings.system.session_timeout}
                              onChange={(e) => handleSettingChange('system', 'session_timeout', parseInt(e.target.value))}
                              className="input w-full"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Max File Size (MB)
                            </label>
                            <input
                              type="number"
                              min="1"
                              max="100"
                              value={localSettings.system.max_file_size}
                              onChange={(e) => handleSettingChange('system', 'max_file_size', parseInt(e.target.value))}
                              className="input w-full"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                              Backup Frequency
                            </label>
                            <select
                              value={localSettings.system.backup_frequency}
                              onChange={(e) => handleSettingChange('system', 'backup_frequency', e.target.value)}
                              className="input w-full"
                            >
                              <option value="daily">Daily</option>
                              <option value="weekly">Weekly</option>
                              <option value="monthly">Monthly</option>
                            </select>
                          </div>
                        </div>
                      </div>

                      {systemInfo && (
                        <div>
                          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                            System Information
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-secondary-50 p-4 rounded-lg">
                              <div className="text-sm text-secondary-600">Version</div>
                              <div className="font-semibold text-secondary-900">{systemInfo.version}</div>
                            </div>
                            <div className="bg-secondary-50 p-4 rounded-lg">
                              <div className="text-sm text-secondary-600">Last Backup</div>
                              <div className="font-semibold text-secondary-900">
                                {new Date(systemInfo.last_backup).toLocaleDateString()}
                              </div>
                            </div>
                            <div className="bg-secondary-50 p-4 rounded-lg">
                              <div className="text-sm text-secondary-600">Storage Used</div>
                              <div className="font-semibold text-secondary-900">
                                {((systemInfo.storage_used / systemInfo.storage_limit) * 100).toFixed(1)}%
                              </div>
                              <div className="w-full bg-secondary-200 rounded-full h-2 mt-1">
                                <div
                                  className="bg-primary-600 h-2 rounded-full"
                                  style={{
                                    width: `${(systemInfo.storage_used / systemInfo.storage_limit) * 100}%`,
                                  }}
                                ></div>
                              </div>
                            </div>
                            <div className="bg-secondary-50 p-4 rounded-lg">
                              <div className="text-sm text-secondary-600">Active Sessions</div>
                              <div className="font-semibold text-secondary-900">{systemInfo.active_sessions}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      <div>
                        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                          Danger Zone
                        </h3>
                        <div className="border border-danger-200 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-danger-900">Reset All Settings</h4>
                              <p className="text-sm text-danger-600">
                                This will reset all settings to their default values
                              </p>
                            </div>
                            <button
                              onClick={handleResetSettings}
                              disabled={resetSettingsMutation.isLoading}
                              className="btn btn-danger"
                            >
                              {resetSettingsMutation.isLoading ? (
                                <LoadingSpinner size="sm" />
                              ) : (
                                <>
                                  <RefreshCw className="w-4 h-4 mr-2" />
                                  Reset
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Settings