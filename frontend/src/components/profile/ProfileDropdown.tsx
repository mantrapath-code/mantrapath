import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Gear, SignOut, Eye } from '@phosphor-icons/react'
import { ProfileAvatar } from './ProfileAvatar'
import { cn } from '@/lib/utils'
import { useProfile } from '@/hooks/useProfile'

interface User {
  id: string
  username: string
  email?: string
  first_name?: string
  last_name?: string
  created_at?: string
}

interface ProfileDropdownProps {
  user: User
  onProfileView: () => void
  onProfileEdit: () => void
  onSettings: () => void
  onLogout: () => void
  className?: string
}

export function ProfileDropdown({
  user,
  onProfileView,
  onProfileEdit,
  onSettings,
  onLogout,
  className
}: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { profile } = useProfile()

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Close dropdown on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen])

  const handleLogout = () => {
    setIsOpen(false)
    onLogout()
  }

  const handleProfileView = () => {
    setIsOpen(false)
    onProfileView()
  }

  const handleProfileEdit = () => {
    setIsOpen(false)
    onProfileEdit()
  }

  const handleSettings = () => {
    setIsOpen(false)
    onSettings()
  }

  const getDisplayName = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`
    }
    return user.username
  }

  const getInitials = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`
    }
    return user.username
  }

  return (
    <div className={cn('relative', className)} ref={dropdownRef}>
      {/* Profile Avatar Trigger */}
      <ProfileAvatar
        src={profile?.avatar_url}
        fallbackText={getInitials()}
        alt={`${getDisplayName()}'s profile`}
        size="md"
        onClick={() => setIsOpen(!isOpen)}
        className="ring-2 ring-transparent hover:ring-primary/20 transition-all duration-200"
      />

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-64 bg-card border border-border rounded-lg shadow-lg overflow-hidden z-50"
          >
            {/* Profile Header */}
            <div className="px-4 py-3 border-b border-border bg-muted/50">
              <div className="flex items-center gap-3">
                <ProfileAvatar
                  src={profile?.avatar_url}
                  fallbackText={getInitials()}
                  alt={getDisplayName()}
                  size="md"
                />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-foreground truncate">
                    {getDisplayName()}
                  </p>
                  <p className="text-sm text-muted-foreground truncate">
                    @{user.username}
                  </p>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <div className="py-2">
              <DropdownMenuItem
                icon={<Eye size={16} />}
                label="View Profile"
                onClick={handleProfileView}
              />
              <DropdownMenuItem
                icon={<User size={16} />}
                label="Edit Profile"
                onClick={handleProfileEdit}
              />
              <DropdownMenuItem
                icon={<Gear size={16} />}
                label="Settings"
                onClick={handleSettings}
              />
            </div>

            {/* Divider */}
            <div className="border-t border-border" />

            {/* Logout */}
            <div className="py-2">
              <DropdownMenuItem
                icon={<SignOut size={16} />}
                label="Logout"
                onClick={handleLogout}
                className="text-destructive hover:bg-destructive/10"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface DropdownMenuItemProps {
  icon: React.ReactNode
  label: string
  onClick: () => void
  className?: string
}

function DropdownMenuItem({ icon, label, onClick, className }: DropdownMenuItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center gap-3 px-4 py-2 text-sm text-foreground hover:bg-muted/50 transition-colors duration-150',
        className
      )}
    >
      <span className="text-muted-foreground">{icon}</span>
      <span>{label}</span>
    </button>
  )
}
