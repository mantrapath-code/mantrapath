import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { 
  BookOpen, 
  Sparkles, 
  Search, 
  Plus, 
  TrendingUp,
  Calendar,
  Tag,
  BarChart3,
  Wifi,
  WifiOff
} from "@phosphor-icons/react"
import { useJournal } from "@/hooks/useJournal"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"

export function JournalSection() {
  const { 
    entries, 
    loading, 
    error, 
    analytics, 
    hasMore, 
    isOnline,
    addEntry, 
    updateEntry, 
    deleteEntry, 
    searchEntries, 
    loadMore,
    refresh 
  } = useJournal()
  
  const [isWriting, setIsWriting] = useState(false)
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [tags, setTags] = useState<string[]>([])
  const [isPrivate, setIsPrivate] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [showAnalytics, setShowAnalytics] = useState(false)
  
  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required')
      return
    }
    
    const newEntry = await addEntry(title, content, {
      tags,
      is_private: isPrivate
    })
    
    if (newEntry) {
      setTitle("")
      setContent("")
      setTags([])
      setIsPrivate(false)
      setIsWriting(false)
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    searchEntries(query)
  }

  const addTag = (tag: string) => {
    if (tag.trim() && !tags.includes(tag.trim())) {
      setTags(prev => [...prev, tag.trim()])
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(prev => prev.filter(tag => tag !== tagToRemove))
  }
  
  const prompts = [
    "What are three things you're grateful for today?",
    "Describe a moment when you felt peaceful recently.",
    "What challenge are you working through right now?",
    "How did you show kindness to yourself or others today?",
    "What does your ideal day look like?",
    "What lesson did you learn this week?",
    "How have you grown as a person lately?",
    "What are you most excited about right now?"
  ]
  
  const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)]

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      {!isOnline && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-orange-50 border border-orange-200 rounded-lg p-4 flex items-center gap-3"
        >
          <WifiOff className="text-orange-600" size={20} />
          <div>
            <p className="text-sm font-medium text-orange-800">Working offline</p>
            <p className="text-xs text-orange-600">Your entries will sync when connection is restored</p>
          </div>
        </motion.div>
      )}

      {/* Analytics Summary Card */}
      {analytics && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-lg">
                <BarChart3 className="text-primary" size={20} />
                Writing Analytics
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAnalytics(!showAnalytics)}
              >
                {showAnalytics ? 'Hide' : 'Show'} Details
              </Button>
            </div>
          </CardHeader>
          {showAnalytics && (
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">{analytics.total_entries}</div>
                  <div className="text-xs text-muted-foreground">Total Entries</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-accent">{analytics.writing_streak}</div>
                  <div className="text-xs text-muted-foreground">Day Streak</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{Math.round(analytics.average_word_count)}</div>
                  <div className="text-xs text-muted-foreground">Avg Words</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {analytics.sentiment_distribution?.positive || 0}%
                  </div>
                  <div className="text-xs text-muted-foreground">Positive</div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      )}

      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={16} />
            <Input
              placeholder="Search your journal entries..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Write New Entry */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="text-primary" size={24} />
            Personal Journal
            {!isOnline && <WifiOff className="text-orange-500" size={16} />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isWriting ? (
            <div className="space-y-4">
              <div className="text-center p-6 bg-muted/50 rounded-lg">
                <Sparkles className="mx-auto text-accent mb-3" size={32} />
                <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
                  <strong>Writing prompt:</strong> <em>"{randomPrompt}"</em>
                </p>
                <Button onClick={() => setIsWriting(true)} className="gap-2">
                  <Plus size={16} />
                  Start Writing
                </Button>
              </div>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <Input
                placeholder="Entry title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={100}
              />
              <Textarea
                placeholder="What's on your mind? You can use the prompt above or write about anything..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="min-h-32"
                autoFocus
              />
              
              {/* Tags Input */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Tags (optional)</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {tags.map(tag => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => removeTag(tag)}
                    >
                      {tag} ×
                    </Badge>
                  ))}
                </div>
                <Input
                  placeholder="Add tags (press Enter to add)"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addTag(e.currentTarget.value)
                      e.currentTarget.value = ''
                    }
                  }}
                />
              </div>

              {/* Privacy Toggle */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="private"
                  checked={isPrivate}
                  onChange={(e) => setIsPrivate(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="private" className="text-sm">Keep this entry private</label>
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={handleSubmit} 
                  disabled={!title.trim() || !content.trim() || loading}
                  className="gap-2"
                >
                  {loading ? 'Saving...' : 'Save Entry'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setIsWriting(false)
                    setTitle("")
                    setContent("")
                    setTags([])
                    setIsPrivate(false)
                  }}
                >
                  Cancel
                </Button>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
      
      {/* Recent Entries */}
      {entries.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar size={20} />
              {searchQuery ? 'Search Results' : 'Recent Entries'}
            </CardTitle>
            {!searchQuery && (
              <Button variant="ghost" size="sm" onClick={refresh} disabled={loading}>
                <TrendingUp size={16} />
              </Button>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatePresence>
                {loading && entries.length === 0 ? (
                  // Loading skeletons
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                      <Skeleton className="h-20 w-full" />
                    </div>
                  ))
                ) : (
                  entries.slice(0, searchQuery ? entries.length : 5).map((entry) => (
                    <motion.div
                      key={entry.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="border-l-4 border-primary/30 pl-4 space-y-2 hover:bg-muted/30 p-3 rounded-r-lg transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <h4 className="font-medium text-foreground leading-tight">{entry.title}</h4>
                        <div className="flex items-center gap-2 ml-4">
                          {entry.is_private && (
                            <Badge variant="outline" className="text-xs">Private</Badge>
                          )}
                          <Badge variant={
                            entry.sentiment === 'positive' ? 'default' :
                            entry.sentiment === 'negative' ? 'destructive' : 'secondary'
                          } className="text-xs">
                            {entry.sentiment === 'positive' ? '😊' : 
                             entry.sentiment === 'negative' ? '😔' : '😐'} {entry.sentiment}
                          </Badge>
                        </div>
                      </div>
                      
                      <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                        {entry.content}
                      </p>
                      
                      {(entry.keywords?.length > 0 || entry.tags?.length > 0) && (
                        <div className="flex flex-wrap gap-1">
                          {(entry.tags || entry.keywords || []).slice(0, 4).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              <Tag size={10} className="mr-1" />
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{new Date(entry.timestamp).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}</span>
                        {entry.word_count && (
                          <span>{entry.word_count} words</span>
                        )}
                      </div>
                    </motion.div>
                  ))
                )}
              </AnimatePresence>
              
              {/* Load More Button */}
              {!searchQuery && hasMore && entries.length > 0 && (
                <div className="text-center pt-4">
                  <Button 
                    variant="outline" 
                    onClick={loadMore} 
                    disabled={loading}
                    className="gap-2"
                  >
                    {loading ? 'Loading...' : 'Load More Entries'}
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-destructive/50">
          <CardContent className="pt-6">
            <div className="text-center text-destructive">
              <p className="font-medium">Something went wrong</p>
              <p className="text-sm text-muted-foreground mt-1">{error}</p>
              <Button variant="outline" size="sm" onClick={refresh} className="mt-3">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!loading && entries.length === 0 && !error && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <BookOpen className="mx-auto text-muted-foreground mb-4" size={48} />
              <p className="text-lg font-medium text-foreground mb-2">
                {searchQuery ? 'No entries found' : 'Start your journaling journey'}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                {searchQuery 
                  ? `No entries match "${searchQuery}". Try a different search term.`
                  : 'Writing helps process thoughts and track your mental wellness over time.'
                }
              </p>
              {searchQuery ? (
                <Button variant="outline" onClick={() => handleSearch('')}>
                  Clear Search
                </Button>
              ) : (
                <Button onClick={() => setIsWriting(true)}>
                  Write Your First Entry
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}