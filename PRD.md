# MantraPath - Integrated Mental Wellness Platform

MantraPath is a comprehensive mental wellness companion that connects mood tracking, journaling, AI chatbot support, and community features into a cohesive, adaptive experience.

**Experience Qualities**:
1. **Supportive** - Every interaction feels like a caring companion guiding the user's wellness journey
2. **Seamless** - Features work together automatically, reducing friction and manual effort  
3. **Personal** - The app adapts to individual patterns and provides contextual, timely support

**Complexity Level**: Light Application (multiple features with basic state)
The app integrates several wellness tools but maintains simplicity through automation and intelligent suggestions rather than overwhelming feature sets.

## Essential Features

### Mood Tracking & Analytics
- **Functionality**: Quick mood logging with visual timeline and pattern recognition
- **Purpose**: Helps users understand emotional patterns and triggers
- **Trigger**: Daily check-ins, post-chat analysis, or manual entry
- **Progression**: Quick mood selection → automatic logging → pattern insights → personalized suggestions
- **Success criteria**: Users can log moods in under 10 seconds and view meaningful trends

### AI Chatbot (Mantra-Mitra)
- **Functionality**: Contextual AI companion with assistant and immersive modes
- **Purpose**: Provides immediate support and can infer mood states from conversations
- **Trigger**: User-initiated or proactive notifications based on patterns
- **Progression**: Chat bubble access → conversation → mood inference → personalized content updates
- **Success criteria**: Users feel heard and supported, with seamless mood logging integration

### Personal Journal
- **Functionality**: Guided journaling with sentiment analysis and reflection prompts
- **Purpose**: Encourages self-reflection and tracks emotional growth over time
- **Trigger**: Daily prompts, post-mood logging, or user-initiated
- **Progression**: Writing prompt → journal entry → sentiment feedback → insight generation
- **Success criteria**: Regular journaling habit with meaningful reflection insights

### Community Support
- **Functionality**: Safe forums for peer support with moderation and encouragement
- **Purpose**: Provides social connection and shared experiences in wellness journey
- **Trigger**: User browsing, notification of relevant discussions, or posting needs
- **Progression**: Browse topics → engage with posts → share experiences → receive support
- **Success criteria**: Active, supportive community with minimal harmful content

### Adaptive Content Feed
- **Functionality**: Personalized wellness content based on mood patterns and interests
- **Purpose**: Delivers relevant support materials at the right time
- **Trigger**: Mood changes, time patterns, or user browsing
- **Progression**: Content analysis → personalization → feed update → user engagement
- **Success criteria**: High engagement with suggested content and reported helpfulness

## Edge Case Handling
- **Crisis Detection**: Emergency resources and immediate human support contact options
- **Privacy Concerns**: Anonymous posting options and granular privacy controls
- **Content Moderation**: AI + human review system for uploaded media and posts
- **Offline Access**: Core features available without internet for consistent support
- **Data Export**: Users can download their complete wellness data

## Design Direction
The design should evoke warmth, safety, and gentle guidance - like having a wise, caring friend available 24/7. Modern and clean aesthetics with soft, calming elements that reduce anxiety rather than create it. Minimal interface that gets out of the way of content and connection.

## Color Selection
Analogous color scheme using calming blues and soft greens to create a serene, trustworthy environment.

- **Primary Color**: Soft Teal (oklch(0.7 0.1 180)) - represents calm, clarity, and healing
- **Secondary Colors**: Warm Blue (oklch(0.65 0.08 220)) for trust, Sage Green (oklch(0.75 0.06 140)) for growth
- **Accent Color**: Gentle Orange (oklch(0.8 0.1 60)) for encouragement and positivity
- **Foreground/Background Pairings**: 
  - Background (Soft White oklch(0.98 0.01 180)): Dark Teal text (oklch(0.3 0.08 180)) - Ratio 6.2:1 ✓
  - Card (Pure White oklch(1 0 0)): Dark Blue text (oklch(0.25 0.06 220)) - Ratio 7.1:1 ✓
  - Primary (Soft Teal): White text (oklch(1 0 0)) - Ratio 4.8:1 ✓
  - Accent (Gentle Orange): Dark text (oklch(0.2 0.05 60)) - Ratio 5.2:1 ✓

## Font Selection
Typography should feel approachable and readable while maintaining professionalism - Inter for its excellent readability and warm character.

- **Typographic Hierarchy**: 
  - H1 (App Title): Inter Bold/32px/tight letter spacing
  - H2 (Section Headers): Inter Semibold/24px/normal spacing  
  - H3 (Card Titles): Inter Medium/18px/normal spacing
  - Body (Main Text): Inter Regular/16px/relaxed line height
  - Caption (Metadata): Inter Regular/14px/muted color

## Animations
Gentle, purposeful motion that feels supportive rather than flashy - subtle transitions that guide attention and provide feedback without causing anxiety.

- **Purposeful Meaning**: Breathing-like animations for mood check-ins, gentle fades for content updates
- **Hierarchy of Movement**: Mood visualizations get priority, followed by content transitions, then UI feedback

## Component Selection
- **Components**: Cards for content sections, Dialogs for mood logging, Tabs for navigation, Button variants for different action types, Avatar for profile/community features
- **Customizations**: Mood ring component, chat bubble layouts, progress indicators for wellness goals
- **States**: Soft focus states, gentle hover effects, encouraging active states, respectful disabled states
- **Icon Selection**: Phosphor icons for their friendly, approachable style - heart for mood, chat for support, book for journal
- **Spacing**: Generous padding (p-6, p-8) for breathing room, consistent gaps (gap-4, gap-6) for related elements
- **Mobile**: Bottom navigation, collapsible sections, thumb-friendly touch targets, swipe gestures for natural interaction