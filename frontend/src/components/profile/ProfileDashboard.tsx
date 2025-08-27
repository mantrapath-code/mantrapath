import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { ProfileAvatar } from './ProfileAvatar'
import { User, Gear, Eye, PencilSimple } from '@phosphor-icons/react'
import { useProfile } from '@/hooks/useProfile'
import { useAuth } from '@/hooks/useAuth'
import { getUserDisplayName, getUserInitials } from '@/utils/userDisplay'

interface ProfileDashboardProps {
  onClose?: () => void
}

export function ProfileDashboard({ onClose }: ProfileDashboardProps) {
  const { user } = useAuth()
  const { profile, stats, loading, error } = useProfile()
  const [activeTab, setActiveTab] = useState('overview')

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Loading profile...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center">
        <p className="text-destructive mb-4">Error loading profile: {error}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    )
  }

  if (!user || !profile) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center">
        <p className="text-muted-foreground">No profile data available</p>
      </div>
    )
  }

  const getDisplayName = () => {
    return getUserDisplayName(user)
  }

  const getInitials = () => {
    return getUserInitials(user)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      {/* Profile Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <ProfileAvatar
                src={profile.avatar_url}
                fallbackText={getInitials()}
                alt={getDisplayName()}
                size="lg"
                className="w-20 h-20"
              />
              <div>
                <CardTitle className="text-2xl">{getDisplayName()}</CardTitle>
                <p className="text-muted-foreground">ID: {getUserDisplayName(user)}</p>
                {profile.bio && (
                  <p className="text-sm text-foreground mt-2 max-w-md">{profile.bio}</p>
                )}
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                  {profile.location && <span>📍 {profile.location}</span>}
                  {user.created_at && <span>📅 Joined {new Date(user.created_at).toLocaleDateString()}</span>}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setActiveTab('edit')}
              >
                <PencilSimple size={16} />
                <span className="ml-2">Edit Profile</span>
              </Button>
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  ✕
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Profile Navigation */}
      <Card>
        <CardContent className="p-0">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full justify-start border-b rounded-none bg-transparent h-auto p-0">
              <TabsTrigger 
                value="overview" 
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
              >
                <Eye size={16} />
                <span className="ml-2">Overview</span>
              </TabsTrigger>
              <TabsTrigger 
                value="edit" 
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
              >
                <User size={16} />
                <span className="ml-2">Edit Profile</span>
              </TabsTrigger>
              <TabsTrigger 
                value="settings" 
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
              >
                <Gear size={16} />
                <span className="ml-2">Settings</span>
              </TabsTrigger>
            </TabsList>

            <div className="p-6">
              <TabsContent value="overview" className="mt-0">
                <ProfileOverview profile={profile} stats={stats} user={user} />
              </TabsContent>
              
              <TabsContent value="edit" className="mt-0">
                <ProfileEditor profile={profile} user={user} />
              </TabsContent>
              
              <TabsContent value="settings" className="mt-0">
                <ProfileSettings profile={profile} user={user} />
              </TabsContent>
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </motion.div>
  )
}

// Placeholder components - these will be implemented in detail later
interface ProfileOverviewProps {
  profile: any
  stats: any
  user: any
}

function ProfileOverview({ profile, stats, user }: ProfileOverviewProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-3">Profile Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">Email</label>
            <p className="text-foreground">{user.email || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">User ID</label>
            <p className="text-foreground">{getUserDisplayName(user)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Location</label>
            <p className="text-foreground">{profile.location || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Member Since</label>
            <p className="text-foreground">
              {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
            </p>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-3">Wellness Journey</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary">{stats?.daysActive || 0}</div>
              <div className="text-sm text-muted-foreground">Days Active</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary">{stats?.moodEntries || 0}</div>
              <div className="text-sm text-muted-foreground">Mood Entries</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary">{stats?.avgMoodScore || 0}</div>
              <div className="text-sm text-muted-foreground">Avg Mood Score</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function ProfileEditor({ profile, user }: { profile: any; user: any }) {
  const { updateProfile } = useProfile()
  const [formData, setFormData] = useState({
    bio: profile.bio || '',
    location: profile.location || '',
    timezone: profile.timezone || 'UTC',
    date_of_birth: profile.date_of_birth || ''
  })
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSave = async () => {
    try {
      setIsSaving(true)
      setMessage('')
      
      // Only send supported fields to backend
      const supportedData = {
        bio: formData.bio,
        timezone: formData.timezone
        // Note: location and date_of_birth are not yet supported by backend
      }
      
      await updateProfile(supportedData)
      setMessage('Profile updated successfully! (Note: Location and Date of Birth will be supported in a future update)')
      
      setTimeout(() => setMessage(''), 5000)
    } catch (error) {
      setMessage('Failed to update profile. Please try again.')
      console.error('Profile update error:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = () => {
    setFormData({
      bio: profile.bio || '',
      location: profile.location || '',
      timezone: profile.timezone || 'UTC',
      date_of_birth: profile.date_of_birth || ''
    })
    setMessage('')
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Edit Profile</h3>
        <p className="text-muted-foreground text-sm">
          Update your profile information and preferences.
        </p>
      </div>

      {message && (
        <div className={`p-3 rounded-md text-sm ${
          message.includes('success') 
            ? 'bg-green-50 text-green-700 border border-green-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <Textarea
              id="bio"
              placeholder="Tell others about yourself..."
              value={formData.bio}
              onChange={(e) => handleInputChange('bio', e.target.value)}
              rows={3}
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground">
              {formData.bio.length}/500 characters
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="Your city, country"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <select
                id="timezone"
                value={formData.timezone}
                onChange={(e) => handleInputChange('timezone', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
                <option value="Europe/Paris">Paris</option>
                <option value="Asia/Tokyo">Tokyo</option>
                <option value="Asia/Shanghai">Shanghai</option>
                <option value="Asia/Kolkata">India</option>
                <option value="Australia/Sydney">Sydney</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="date_of_birth">Date of Birth</Label>
            <Input
              id="date_of_birth"
              type="date"
              value={formData.date_of_birth}
              onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              This information is private and won't be shared publicly
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-3">
        <Button 
          onClick={handleSave} 
          disabled={isSaving}
          className="min-w-[120px]"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button 
          variant="outline" 
          onClick={handleReset}
          disabled={isSaving}
        >
          Reset
        </Button>
      </div>
    </div>
  )
}

function ProfileSettings({ profile, user }: { profile: any; user: any }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Profile Settings</h3>
      <p className="text-muted-foreground">
        Privacy and notification settings will be implemented here.
      </p>
      <div className="p-8 border-2 border-dashed border-muted rounded-lg text-center text-muted-foreground">
        Profile Settings Component - Coming Soon
      </div>
    </div>
  )
}
