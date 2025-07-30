import { useState, useEffect, useCallback } from 'react'
import { apiService } from '@/services/api'
import { toast } from 'sonner'

interface Forum {
  id: string
  name: string
  description: string
  category: string
  member_count: number
  is_joined: boolean
}

interface Thread {
  id: string
  forum_id: string
  title: string
  content: string
  author: string
  reply_count: number
  view_count: number
  created_at: string
  is_pinned: boolean
}

interface Reply {
  id: string
  thread_id: string
  content: string
  author: string
  created_at: string
  likes_count: number
}

export function useCommunity() {
  const [forums, setForums] = useState<Forum[]>([])
  const [threads, setThreads] = useState<Thread[]>([])
  const [replies, setReplies] = useState<Reply[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load forums
  const loadForums = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const forumsData = await apiService.getForums()
      setForums(forumsData)
      
    } catch (err) {
      console.error('Failed to load forums:', err)
      setError('Failed to load forums')
      toast.error('Failed to load community forums')
    } finally {
      setLoading(false)
    }
  }, [])

  // Load threads for a forum
  const loadThreads = useCallback(async (forumId: string) => {
    try {
      setLoading(true)
      setError(null)
      
      const threadsData = await apiService.getForumThreads(forumId)
      setThreads(threadsData)
      
    } catch (err) {
      console.error('Failed to load threads:', err)
      setError('Failed to load threads')
      toast.error('Failed to load forum threads')
    } finally {
      setLoading(false)
    }
  }, [])

  // Join forum
  const joinForum = useCallback(async (forumId: string) => {
    try {
      await apiService.joinForum(forumId)
      
      // Update local state
      setForums(prev => prev.map(forum => 
        forum.id === forumId 
          ? { ...forum, is_joined: true, member_count: forum.member_count + 1 }
          : forum
      ))
      
      toast.success('Successfully joined forum!')
      
    } catch (err) {
      console.error('Failed to join forum:', err)
      toast.error('Failed to join forum')
    }
  }, [])

  // Leave forum
  const leaveForum = useCallback(async (forumId: string) => {
    try {
      await apiService.leaveForum(forumId)
      
      // Update local state
      setForums(prev => prev.map(forum => 
        forum.id === forumId 
          ? { ...forum, is_joined: false, member_count: Math.max(0, forum.member_count - 1) }
          : forum
      ))
      
      toast.success('Successfully left forum')
      
    } catch (err) {
      console.error('Failed to leave forum:', err)
      toast.error('Failed to leave forum')
    }
  }, [])

  // Create thread
  const createThread = useCallback(async (forumId: string, title: string, content: string) => {
    try {
      setLoading(true)
      
      const newThread = await apiService.createThread({
        forum_id: forumId,
        title,
        content
      })
      
      setThreads(prev => [newThread, ...prev])
      toast.success('Thread created successfully!')
      
      return newThread
      
    } catch (err) {
      console.error('Failed to create thread:', err)
      toast.error('Failed to create thread')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Reply to thread
  const replyToThread = useCallback(async (threadId: string, content: string, parentId?: string) => {
    try {
      const newReply = await apiService.replyToThread(threadId, content, parentId)
      
      setReplies(prev => [...prev, newReply])
      
      // Update thread reply count
      setThreads(prev => prev.map(thread => 
        thread.id === threadId 
          ? { ...thread, reply_count: thread.reply_count + 1 }
          : thread
      ))
      
      toast.success('Reply posted successfully!')
      
      return newReply
      
    } catch (err) {
      console.error('Failed to post reply:', err)
      toast.error('Failed to post reply')
      throw err
    }
  }, [])

  // Like content
  const likeContent = useCallback(async (contentType: string, contentId: string) => {
    try {
      await apiService.likeContent(contentType, contentId)
      toast.success('Content liked!')
      
    } catch (err) {
      console.error('Failed to like content:', err)
      if ((err as any).status !== 400) { // Don't show error for "already liked"
        toast.error('Failed to like content')
      }
    }
  }, [])

  // Unlike content
  const unlikeContent = useCallback(async (contentType: string, contentId: string) => {
    try {
      await apiService.unlikeContent(contentType, contentId)
      toast.success('Like removed')
      
    } catch (err) {
      console.error('Failed to unlike content:', err)
      toast.error('Failed to remove like')
    }
  }, [])

  // Load forums on mount
  useEffect(() => {
    loadForums()
  }, [loadForums])

  return {
    forums,
    threads,
    replies,
    loading,
    error,
    actions: {
      loadForums,
      loadThreads,
      joinForum,
      leaveForum,
      createThread,
      replyToThread,
      likeContent,
      unlikeContent,
      refresh: loadForums
    }
  }
}