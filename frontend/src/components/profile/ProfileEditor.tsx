import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { useProfile } from '@/hooks/useProfile'

interface UserProfile {
  id: string
  user_id: string
  bio?: string
  avatar_url?: string
  timezone: string
  date_of_birth?: string
  location?: string
  theme: string
  privacy_level: string
  created_at: string
  updated_at: string
}

interface ProfileEditorProps {
  profile: UserProfile
  user: any
}

export function ProfileEditor({ profile, user }: ProfileEditorProps) {
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
