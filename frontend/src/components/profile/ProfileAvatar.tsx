import { useState } from 'react'
import { cn } from '@/lib/utils'

interface ProfileAvatarProps {
  src?: string
  alt?: string
  size?: 'sm' | 'md' | 'lg'
  fallbackText?: string
  className?: string
  onClick?: () => void
  showOnlineStatus?: boolean
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg'
}

export function ProfileAvatar({
  src,
  alt = 'Profile',
  size = 'md',
  fallbackText,
  className,
  onClick,
  showOnlineStatus = false
}: ProfileAvatarProps) {
  const [imageError, setImageError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const handleImageLoad = () => {
    setIsLoading(false)
  }

  const handleImageError = () => {
    setImageError(true)
    setIsLoading(false)
  }

  const getInitials = (text?: string) => {
    if (!text) return '?'
    return text
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div 
      className={cn(
        'relative flex items-center justify-center rounded-full border-2 border-muted-foreground/20 bg-muted overflow-hidden transition-all duration-200',
        sizeClasses[size],
        onClick && 'cursor-pointer hover:border-primary/50 hover:scale-105',
        className
      )}
      onClick={onClick}
    >
      {/* Loading state */}
      {isLoading && src && !imageError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted animate-pulse">
          <div className="w-4 h-4 border-2 border-muted-foreground/30 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Profile image */}
      {src && !imageError && (
        <img
          src={src}
          alt={alt}
          className={cn(
            'w-full h-full object-cover transition-opacity duration-200',
            isLoading ? 'opacity-0' : 'opacity-100'
          )}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      )}

      {/* Fallback initials */}
      {(!src || imageError) && (
        <span className="font-semibold text-muted-foreground select-none">
          {getInitials(fallbackText)}
        </span>
      )}

      {/* Online status indicator */}
      {showOnlineStatus && (
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
      )}

      {/* Hover ring effect */}
      {onClick && (
        <div className="absolute inset-0 rounded-full ring-0 ring-primary/20 transition-all duration-200 hover:ring-2" />
      )}
    </div>
  )
}
