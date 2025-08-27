/**
 * Voice Permission Utility
 * Handles microphone permissions and browser compatibility for voice features
 */

export interface VoiceCapabilities {
  microphone: boolean
  speechRecognition: boolean
  speechSynthesis: boolean
}

export interface PermissionStatus {
  microphone: 'granted' | 'denied' | 'prompt' | 'unknown'
  notifications: 'granted' | 'denied' | 'default' | 'unknown'
}

class VoicePermissionManager {
  private static instance: VoicePermissionManager
  private permissionStatus: PermissionStatus = {
    microphone: 'unknown',
    notifications: 'unknown'
  }

  static getInstance(): VoicePermissionManager {
    if (!VoicePermissionManager.instance) {
      VoicePermissionManager.instance = new VoicePermissionManager()
    }
    return VoicePermissionManager.instance
  }

  async checkCapabilities(): Promise<VoiceCapabilities> {
    return {
      microphone: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      speechRecognition: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
      speechSynthesis: !!window.speechSynthesis
    }
  }

  async requestMicrophonePermission(): Promise<boolean> {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('🎤 Microphone not supported in this browser')
        return false
      }

      console.log('🎤 Requesting microphone permission...')
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      
      // Stop the stream immediately - we just needed permission
      stream.getTracks().forEach(track => track.stop())
      
      this.permissionStatus.microphone = 'granted'
      console.log('✅ Microphone permission granted')
      return true
    } catch (error: any) {
      console.error('❌ Microphone permission denied:', error)
      
      if (error.name === 'NotAllowedError') {
        this.permissionStatus.microphone = 'denied'
      } else if (error.name === 'NotFoundError') {
        console.warn('🎤 No microphone device found')
      } else {
        console.warn('🎤 Microphone request failed:', error.message)
      }
      
      return false
    }
  }

  async checkMicrophonePermission(): Promise<PermissionState | 'unknown'> {
    try {
      if ('permissions' in navigator) {
        const result = await navigator.permissions.query({ name: 'microphone' as PermissionName })
        this.permissionStatus.microphone = result.state as 'granted' | 'denied' | 'prompt'
        return result.state
      }
    } catch (error) {
      console.warn('Could not check microphone permission:', error)
    }
    return 'unknown'
  }

  async requestNotificationPermission(): Promise<boolean> {
    try {
      if (!('Notification' in window)) {
        console.warn('🔔 Notifications not supported')
        return false
      }

      if (Notification.permission === 'granted') {
        this.permissionStatus.notifications = 'granted'
        return true
      }

      if (Notification.permission === 'denied') {
        this.permissionStatus.notifications = 'denied'
        return false
      }

      console.log('🔔 Requesting notification permission...')
      const permission = await Notification.requestPermission()
      this.permissionStatus.notifications = permission as 'granted' | 'denied' | 'default'
      
      return permission === 'granted'
    } catch (error) {
      console.error('❌ Notification permission request failed:', error)
      return false
    }
  }

  getPermissionStatus(): PermissionStatus {
    return { ...this.permissionStatus }
  }

  async initializeAllPermissions(): Promise<{ 
    microphone: boolean
    notifications: boolean
    capabilities: VoiceCapabilities
  }> {
    console.log('🚀 Initializing voice and notification permissions...')
    
    const capabilities = await this.checkCapabilities()
    const microphoneGranted = capabilities.microphone ? await this.requestMicrophonePermission() : false
    const notificationsGranted = await this.requestNotificationPermission()

    return {
      microphone: microphoneGranted,
      notifications: notificationsGranted,
      capabilities
    }
  }

  showPermissionHelp(): void {
    const helpMessage = `
🎤 Voice Features Help:

To enable voice input:
1. Click the microphone icon
2. Allow microphone access when prompted
3. Speak clearly into your microphone

If voice isn't working:
• Check browser permissions (🔒 icon in address bar)
• Ensure microphone is connected and working
• Try refreshing the page

Supported browsers: Chrome, Firefox, Safari, Edge
    `.trim()

    console.log(helpMessage)
    
    // Show a user-friendly notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Voice Help', {
        body: 'Check the console for voice setup instructions',
        icon: '/icons/microphone.png'
      })
    }
  }
}

export const voicePermissionManager = VoicePermissionManager.getInstance()

// Auto-initialize permissions in development
if (import.meta.env.DEV) {
  setTimeout(() => {
    voicePermissionManager.initializeAllPermissions().then((result) => {
      console.log('🎤 Voice permissions initialized:', result)
    })
  }, 1000)
}

// Global helper for components
declare global {
  interface Window {
    requestVoicePermissions: () => Promise<boolean>
    showVoiceHelp: () => void
  }
}

if (typeof window !== 'undefined') {
  window.requestVoicePermissions = () => voicePermissionManager.requestMicrophonePermission()
  window.showVoiceHelp = () => voicePermissionManager.showPermissionHelp()
}
