/**
 * Shared community data store for consistent community experience across components
 */

import { useKV } from './useKV'
import { communityApi } from '@/services/api'
import { useState, useCallback } from 'react'
import { toast } from 'sonner'

export interface CommunityThread {
  id: string
  title: string
  content: string
  author: {
    id: string
    name: string
    avatar_url?: string
    badges: string[]
  }
  forum_id: string
  forum_name: string
  created_at: string
  updated_at: string
  reply_count: number
  like_count: number
  view_count: number
  is_liked: boolean
  is_bookmarked: boolean
  tags: string[]
  category: string
}

export interface CommunityForum {
  id: string
  name: string
  description: string
  category: string
  member_count: number
  thread_count: number
  is_member: boolean
  created_at: string
  tags: string[]
}

export interface CommunityStats {
  forumsJoined: number
  threadsLiked: number
  repliesPosted: number
  reputation: number
}

export function useCommunityData() {
  const [joinedForums, setJoinedForums] = useKV("joined-forums", [] as string[])
  // Remove localStorage tracking for likes - will use backend data instead
  const [bookmarkedThreads, setBookmarkedThreads] = useKV("bookmarked-threads", [] as string[])
  const [userReputation, setUserReputation] = useKV("user-reputation", 0)
  const [communityStats, setCommunityStats] = useKV("community-stats", {
    forumsJoined: 0,
    threadsLiked: 0,
    repliesPosted: 0,
    reputation: 0
  } as CommunityStats)

  const [forums, setForums] = useState<CommunityForum[]>([])
  const [threads, setThreads] = useState<CommunityThread[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [enhancedStats, setEnhancedStats] = useState<{
    reputation: number
    forums_joined: number
    threads_liked: number
    threads_created: number
    replies_posted: number
    likes_received: number
    help_score: number
  } | null>(null)

  // Load forums
  const loadForums = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const forumsData = await communityApi.getForums()
      setForums(forumsData || [])
      
      // Sync localStorage with backend data
      if (forumsData) {
        const joinedForumIds = forumsData
          .filter((forum: any) => forum.is_joined)
          .map((forum: any) => forum.id)
        setJoinedForums(joinedForumIds)
      }
    } catch (err) {
      console.error('Failed to load forums:', err)
      setError('Failed to load forums')
      toast.error('Failed to load community forums')
    } finally {
      setLoading(false)
    }
  }, [setJoinedForums])

  // Load threads for a forum
  const loadThreads = useCallback(async (forumId: string) => {
    try {
      setLoading(true)
      setError(null)
      const threadsData = await communityApi.getForumThreads(forumId)
      setThreads(threadsData || [])
      
      // Update threads liked count from backend data
      if (threadsData) {
        const likedCount = threadsData.filter((thread: any) => thread.is_liked).length
        const updatedStats = {
          ...communityStats,
          threadsLiked: likedCount
        }
        setCommunityStats(updatedStats)
      }
    } catch (err: any) {
      console.error('Failed to load threads:', err)
      setError('Failed to load threads')
      
      // Handle specific error cases
      if (err.status === 401) {
        toast.error('Please log in to view forum discussions')
      } else if (err.status === 403) {
        // Check if it's a forum membership issue
        if (err.message && err.message.includes('Must be a forum member')) {
          toast.error('You need to join this forum to view discussions')
        } else {
          toast.error('Access denied. Please check your permissions.')
        }
      } else {
        toast.error('Failed to load forum threads')
      }
    } finally {
      setLoading(false)
    }
  }, [communityStats, setCommunityStats])

  // Join forum
  const joinForum = useCallback(async (forumId: string) => {
    try {
      await communityApi.joinForum(forumId)
      const updatedJoined = [...joinedForums, forumId]
      setJoinedForums(updatedJoined)
      
      // Update stats
      const updatedStats = {
        ...communityStats,
        forumsJoined: updatedJoined.length
      }
      setCommunityStats(updatedStats)
      
      toast.success('Successfully joined forum!')
    } catch (err: any) {
      console.error('Failed to join forum:', err)
      
      // Handle specific error cases
      if (err.status === 401 || err.status === 403) {
        toast.error('Please log in to join forums')
      } else {
        toast.error('Failed to join forum')
      }
    }
  }, [joinedForums, communityStats, setJoinedForums, setCommunityStats])

  // Leave forum
  const leaveForum = useCallback(async (forumId: string) => {
    try {
      await communityApi.leaveForum(forumId)
      const updatedJoined = joinedForums.filter(id => id !== forumId)
      setJoinedForums(updatedJoined)
      
      // Update stats
      const updatedStats = {
        ...communityStats,
        forumsJoined: updatedJoined.length
      }
      setCommunityStats(updatedStats)
      
      toast.success('Successfully left forum')
    } catch (err: any) {
      console.error('Failed to leave forum:', err)
      
      // Handle specific error cases
      if (err.status === 401 || err.status === 403) {
        toast.error('Please log in to leave forums')
      } else {
        toast.error('Failed to leave forum')
      }
    }
  }, [joinedForums, communityStats, setJoinedForums, setCommunityStats])

  // Like/Unlike content (using toggle endpoint)
  const toggleLike = useCallback(async (contentType: string, contentId: string) => {
    try {
      const response = await communityApi.likeContent(contentType, contentId)
      
      // Update the thread in our local state with the new like status
      setThreads(prevThreads => 
        prevThreads.map(thread => 
          thread.id === contentId 
            ? { 
                ...thread, 
                is_liked: response.liked,
                like_count: response.like_count
              }
            : thread
        )
      )
      
      // Update stats
      if (response.liked) {
        const updatedStats = {
          ...communityStats,
          threadsLiked: communityStats.threadsLiked + 1
        }
        setCommunityStats(updatedStats)
        setUserReputation(userReputation + 1)
        toast.success('Content liked!')
      } else {
        const updatedStats = {
          ...communityStats,
          threadsLiked: Math.max(0, communityStats.threadsLiked - 1)
        }
        setCommunityStats(updatedStats)
        toast.success('Like removed')
      }
    } catch (err) {
      console.error('Failed to toggle like:', err)
      toast.error('Failed to update like')
    }
  }, [communityStats, userReputation, setCommunityStats, setUserReputation])

  // Reply to thread
  const replyToThread = useCallback(async (threadId: string, content: string, parentId?: string) => {
    try {
      await communityApi.replyToThread(threadId, content, parentId)
      
      // Update stats and reputation
      const updatedStats = {
        ...communityStats,
        repliesPosted: communityStats.repliesPosted + 1
      }
      setCommunityStats(updatedStats)
      setUserReputation(userReputation + 2) // More points for replies
      
      toast.success('Reply posted successfully!')
    } catch (err) {
      console.error('Failed to post reply:', err)
      toast.error('Failed to post reply')
    }
  }, [communityStats, userReputation, setCommunityStats, setUserReputation])

  // Load enhanced user statistics
  const loadUserStats = useCallback(async () => {
    try {
      const stats = await communityApi.getUserStats()
      setEnhancedStats(stats)
      
      // Update local reputation
      setUserReputation(stats.reputation)
      
      // Update community stats with backend data
      setCommunityStats({
        forumsJoined: stats.forums_joined,
        threadsLiked: stats.threads_liked,
        repliesPosted: stats.replies_posted,
        reputation: stats.reputation
      })
    } catch (err: any) {
      console.error('Failed to load user stats:', err)
      
      // Handle authentication errors gracefully
      if (err.status === 401 || err.status === 403) {
        console.log('User not authenticated for stats - using fallback')
        return // Don't set fallback stats if not authenticated
      }
      
      // For other errors, use fallback calculation if backend fails
      if (enhancedStats === null) {
        setEnhancedStats({
          reputation: userReputation,
          forums_joined: joinedForums.length,
          threads_liked: communityStats.threadsLiked,
          threads_created: 0,
          replies_posted: communityStats.repliesPosted,
          likes_received: 0,
          help_score: Math.min(10, userReputation / 10)
        })
      }
    }
  }, [setUserReputation, setCommunityStats])

  return {
    // Data
    forums,
    threads,
    joinedForums,
    bookmarkedThreads,
    userReputation,
    communityStats,
    enhancedStats,
    loading,
    error,
    
    // Actions
    loadForums,
    loadThreads,
    loadUserStats,
    joinForum,
    leaveForum,
    likeContent: toggleLike,
    unlikeContent: toggleLike,
    replyToThread,
    
    // Utilities
    isForumJoined: (forumId: string) => {
      // First check localStorage for immediate response
      const isInLocalStorage = joinedForums.includes(forumId)
      
      // Then check backend data if available (more authoritative)
      const forumFromBackend = forums.find(f => f.id === forumId)
      if (forumFromBackend && 'is_joined' in forumFromBackend) {
        return (forumFromBackend as any).is_joined
      }
      
      // Fallback to localStorage
      return isInLocalStorage
    },
    isThreadLiked: (threadId: string) => {
      // Check the thread data from backend for like status
      const thread = threads.find(t => t.id === threadId)
      return thread?.is_liked || false
    },
    isThreadBookmarked: (threadId: string) => bookmarkedThreads.includes(threadId),
  }
}
