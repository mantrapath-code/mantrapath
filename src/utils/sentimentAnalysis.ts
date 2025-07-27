/**
 * Sentiment analysis utilities for journal and mood processing
 */

export function analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
  const positiveWords = [
    'happy', 'joy', 'great', 'wonderful', 'amazing', 'good', 'better', 
    'grateful', 'peaceful', 'love', 'excited', 'proud', 'blessed', 
    'accomplished', 'successful', 'confident', 'motivated', 'optimistic'
  ]
  
  const negativeWords = [
    'sad', 'angry', 'stressed', 'anxious', 'worried', 'difficult', 'hard', 
    'struggling', 'overwhelming', 'upset', 'frustrated', 'depressed',
    'exhausted', 'disappointed', 'discouraged', 'fearful', 'hopeless'
  ]
  
  const words = text.toLowerCase().split(/\s+/)
  const positiveCount = words.filter(word => 
    positiveWords.some(pos => word.includes(pos))
  ).length
  const negativeCount = words.filter(word => 
    negativeWords.some(neg => word.includes(neg))
  ).length
  
  if (positiveCount > negativeCount + 1) return 'positive'
  if (negativeCount > positiveCount + 1) return 'negative'
  return 'neutral'
}

export function extractKeywords(text: string): string[] {
  const keywords = [
    'work', 'stress', 'anxiety', 'sleep', 'exercise', 'family', 'friends', 
    'goals', 'gratitude', 'mindfulness', 'meditation', 'therapy', 
    'relationship', 'health', 'career', 'school', 'money', 'travel'
  ]
  
  const words = text.toLowerCase().split(/\s+/)
  return keywords.filter(keyword => 
    words.some(word => word.includes(keyword))
  )
}

export function calculateTextComplexity(text: string): {
  wordCount: number
  sentenceCount: number
  averageWordsPerSentence: number
} {
  const words = text.trim().split(/\s+/).filter(word => word.length > 0)
  const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0)
  
  return {
    wordCount: words.length,
    sentenceCount: sentences.length,
    averageWordsPerSentence: sentences.length > 0 ? words.length / sentences.length : 0
  }
}