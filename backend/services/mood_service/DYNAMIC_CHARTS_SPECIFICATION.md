# 📊 Dynamic Mood Charts - Technical Specification

## 🎯 Overview

This document outlines the implementation of dynamic, emotion-based mood charts that integrate with the Real-Time Mood Tracking Service. These charts provide interactive, visually appealing representations of user mood data with real-time updates and emotion-based theming.

## 🎨 Chart Types & Specifications

### 1. Interactive Emotion Wheel Chart

#### Description
A circular, hierarchical visualization of the emotion wheel showing user's emotional distribution across primary, secondary, and tertiary emotions.

#### Technical Specifications
```typescript
interface EmotionWheelConfig {
  type: 'emotion_wheel';
  dimensions: {
    width: number;
    height: number;
    innerRadius: number;
    outerRadius: number;
  };
  interactions: {
    hover: boolean;
    click: boolean;
    drill_down: boolean;
  };
  animations: {
    entrance: 'fade' | 'scale' | 'rotate';
    transitions: 'smooth' | 'bounce' | 'elastic';
    duration: number; // milliseconds
  };
  theming: {
    dynamic: boolean;
    color_scheme: 'emotion_based' | 'custom';
    gradient_support: boolean;
  };
}
```

#### Data Structure
```python
class EmotionWheelData:
    """Data structure for emotion wheel visualization"""
    
    def generate_wheel_segments(self, user_emotions: Dict[str, float]) -> List[Dict]:
        """Generate hierarchical segments for the emotion wheel"""
        segments = []
        
        for primary_emotion, primary_value in user_emotions.items():
            primary_segment = {
                "id": f"primary_{primary_emotion}",
                "name": primary_emotion.title(),
                "value": primary_value,
                "level": 1,
                "color": EMOTION_THEMES[primary_emotion]["--theme-primary"],
                "startAngle": self._calculate_start_angle(primary_emotion),
                "endAngle": self._calculate_end_angle(primary_emotion, primary_value),
                "children": []
            }
            
            # Add secondary emotions
            secondary_emotions = EMOTION_WHEEL[primary_emotion].get("secondary", {})
            for secondary_name, secondary_data in secondary_emotions.items():
                secondary_value = primary_value * 0.6  # Proportional distribution
                secondary_segment = {
                    "id": f"secondary_{secondary_name}",
                    "name": secondary_name.title(),
                    "value": secondary_value,
                    "level": 2,
                    "color": self._lighten_color(primary_segment["color"], 0.3),
                    "parent": primary_segment["id"],
                    "children": []
                }
                
                # Add tertiary emotions
                tertiary_emotions = secondary_data.get("tertiary", [])
                for tertiary_name in tertiary_emotions:
                    tertiary_value = secondary_value / len(tertiary_emotions)
                    tertiary_segment = {
                        "id": f"tertiary_{tertiary_name}",
                        "name": tertiary_name.title(),
                        "value": tertiary_value,
                        "level": 3,
                        "color": self._lighten_color(secondary_segment["color"], 0.3),
                        "parent": secondary_segment["id"]
                    }
                    secondary_segment["children"].append(tertiary_segment)
                
                primary_segment["children"].append(secondary_segment)
            
            segments.append(primary_segment)
        
        return segments
```

#### Frontend Implementation (React/D3.js)
```typescript
// components/charts/EmotionWheelChart.tsx
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface EmotionWheelProps {
  data: EmotionWheelData;
  width?: number;
  height?: number;
  onEmotionSelect?: (emotion: string) => void;
  realTimeUpdates?: boolean;
}

export const EmotionWheelChart: React.FC<EmotionWheelProps> = ({
  data,
  width = 400,
  height = 400,
  onEmotionSelect,
  realTimeUpdates = true
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    const radius = Math.min(width, height) / 2;
    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    // Create hierarchical layout
    const partition = d3.partition<EmotionSegment>()
      .size([2 * Math.PI, radius]);

    const root = d3.hierarchy(data)
      .sum(d => d.value)
      .sort((a, b) => (b.value || 0) - (a.value || 0));

    partition(root);

    // Create arcs
    const arc = d3.arc<d3.HierarchyRectangularNode<EmotionSegment>>()
      .startAngle(d => d.x0)
      .endAngle(d => d.x1)
      .innerRadius(d => d.y0)
      .outerRadius(d => d.y1);

    // Draw segments
    const segments = g.selectAll("path")
      .data(root.descendants())
      .enter()
      .append("path")
      .attr("d", arc)
      .style("fill", d => d.data.color)
      .style("stroke", "#fff")
      .style("stroke-width", 2)
      .style("cursor", "pointer")
      .on("mouseover", handleMouseOver)
      .on("mouseout", handleMouseOut)
      .on("click", handleClick);

    // Add animations
    segments
      .style("opacity", 0)
      .transition()
      .duration(1000)
      .ease(d3.easeBackOut)
      .style("opacity", 1)
      .attrTween("d", function(d) {
        const interpolate = d3.interpolate(
          { x0: 0, x1: 0, y0: 0, y1: 0 },
          d
        );
        return (t: number) => arc(interpolate(t) as any) || "";
      });

    // Add labels for primary emotions
    const labels = g.selectAll("text")
      .data(root.children || [])
      .enter()
      .append("text")
      .attr("transform", d => {
        const angle = (d.x0 + d.x1) / 2;
        const radius = (d.y0 + d.y1) / 2;
        return `rotate(${(angle * 180 / Math.PI) - 90}) translate(${radius}, 0)`;
      })
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", "#333")
      .text(d => d.data.name);

    function handleMouseOver(event: any, d: d3.HierarchyRectangularNode<EmotionSegment>) {
      // Highlight segment
      d3.select(event.currentTarget)
        .transition()
        .duration(200)
        .style("opacity", 0.8)
        .style("stroke-width", 3);

      // Show tooltip
      showTooltip(event, d);
    }

    function handleMouseOut(event: any) {
      d3.select(event.currentTarget)
        .transition()
        .duration(200)
        .style("opacity", 1)
        .style("stroke-width", 2);

      hideTooltip();
    }

    function handleClick(event: any, d: d3.HierarchyRectangularNode<EmotionSegment>) {
      setSelectedEmotion(d.data.name);
      onEmotionSelect?.(d.data.name);
      
      // Animate selection
      segments
        .transition()
        .duration(300)
        .style("opacity", segment => segment === d ? 1 : 0.3);
    }

  }, [data, width, height]);

  // Real-time updates
  useEffect(() => {
    if (realTimeUpdates) {
      const updateChart = (newData: EmotionWheelData) => {
        // Smooth transition to new data
        const svg = d3.select(svgRef.current);
        // Update segments with new data...
      };

      // Subscribe to WebSocket updates
      const ws = new WebSocket(`ws://localhost:8003/ws/mood/${userId}`);
      ws.onmessage = (event) => {
        const update = JSON.parse(event.data);
        if (update.type === 'emotion_wheel_update') {
          updateChart(update.data);
        }
      };

      return () => ws.close();
    }
  }, [realTimeUpdates]);

  return (
    <div className="emotion-wheel-container">
      <svg ref={svgRef} />
      {selectedEmotion && (
        <div className="selected-emotion-info">
          <h3>{selectedEmotion}</h3>
          <p>Click to explore sub-emotions</p>
        </div>
      )}
    </div>
  );
};
```

### 2. Mood Timeline with Emotion Coloring

#### Description
A timeline chart showing mood progression over time with dynamic coloring based on detected emotions.

#### Data Structure
```python
class MoodTimelineData:
    """Generate timeline data with emotion-based coloring"""
    
    def generate_timeline_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate mood timeline with emotion colors"""
        mood_entries = self.get_mood_entries(user_id, days)
        
        timeline_data = []
        for entry in mood_entries:
            primary_emotion = entry.primary_emotion or "neutral"
            emotion_theme = EMOTION_THEMES.get(primary_emotion, EMOTION_THEMES["bad"])
            
            timeline_point = {
                "date": entry.created_at.isoformat(),
                "mood_score": entry.mood_score,
                "energy_level": entry.energy_level,
                "stress_level": entry.stress_level,
                "sleep_quality": entry.sleep_quality,
                "primary_emotion": primary_emotion,
                "emotion_color": emotion_theme["--theme-primary"],
                "emotion_intensity": entry.emotion_confidence or 0.5,
                "notes": entry.notes,
                "celebration_triggers": entry.celebration_triggers or []
            }
            
            timeline_data.append(timeline_point)
        
        return {
            "timeline": timeline_data,
            "summary": self._calculate_timeline_summary(timeline_data),
            "trends": self._calculate_trends(timeline_data),
            "config": {
                "gradient_enabled": True,
                "smooth_curves": True,
                "emotion_indicators": True,
                "interactive_points": True
            }
        }
    
    def _calculate_timeline_summary(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for the timeline"""
        if not timeline_data:
            return {}
        
        mood_scores = [point["mood_score"] for point in timeline_data]
        emotions = [point["primary_emotion"] for point in timeline_data]
        
        return {
            "average_mood": sum(mood_scores) / len(mood_scores),
            "mood_range": {"min": min(mood_scores), "max": max(mood_scores)},
            "dominant_emotion": max(set(emotions), key=emotions.count),
            "emotion_distribution": {emotion: emotions.count(emotion) for emotion in set(emotions)},
            "total_entries": len(timeline_data),
            "celebration_count": sum(len(point["celebration_triggers"]) for point in timeline_data)
        }
```

#### Frontend Implementation
```typescript
// components/charts/MoodTimelineChart.tsx
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface MoodTimelineProps {
  data: MoodTimelineData;
  width?: number;
  height?: number;
  showEmotionIndicators?: boolean;
}

export const MoodTimelineChart: React.FC<MoodTimelineProps> = ({
  data,
  width = 800,
  height = 400,
  showEmotionIndicators = true
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.timeline) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(data.timeline, d => new Date(d.date)) as [Date, Date])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([1, 10])
      .range([innerHeight, 0]);

    // Create gradient definitions
    const defs = svg.append("defs");
    
    data.timeline.forEach((point, i) => {
      const gradient = defs
        .append("linearGradient")
        .attr("id", `emotion-gradient-${i}`)
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", 0).attr("y1", 0)
        .attr("x2", 0).attr("y2", innerHeight);

      gradient
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", point.emotion_color)
        .attr("stop-opacity", point.emotion_intensity);

      gradient
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", point.emotion_color)
        .attr("stop-opacity", 0.1);
    });

    // Line generator with curves
    const line = d3.line<MoodTimelinePoint>()
      .x(d => xScale(new Date(d.date)))
      .y(d => yScale(d.mood_score))
      .curve(d3.curveCardinal);

    // Draw the line
    const path = g.append("path")
      .datum(data.timeline)
      .attr("fill", "none")
      .attr("stroke", "#6366f1")
      .attr("stroke-width", 3)
      .attr("d", line);

    // Animate line drawing
    const totalLength = path.node()?.getTotalLength() || 0;
    path
      .attr("stroke-dasharray", `${totalLength} ${totalLength}`)
      .attr("stroke-dashoffset", totalLength)
      .transition()
      .duration(2000)
      .ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0);

    // Add emotion-colored dots
    const dots = g.selectAll(".mood-dot")
      .data(data.timeline)
      .enter()
      .append("circle")
      .attr("class", "mood-dot")
      .attr("cx", d => xScale(new Date(d.date)))
      .attr("cy", d => yScale(d.mood_score))
      .attr("r", 0)
      .attr("fill", d => d.emotion_color)
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .style("cursor", "pointer");

    // Animate dots appearance
    dots
      .transition()
      .delay((d, i) => i * 50)
      .duration(500)
      .attr("r", d => 4 + (d.emotion_intensity * 3));

    // Add emotion indicators if enabled
    if (showEmotionIndicators) {
      const emotionIndicators = g.selectAll(".emotion-indicator")
        .data(data.timeline.filter(d => d.celebration_triggers.length > 0))
        .enter()
        .append("g")
        .attr("class", "emotion-indicator")
        .attr("transform", d => `translate(${xScale(new Date(d.date))}, ${yScale(d.mood_score) - 20})`);

      emotionIndicators
        .append("circle")
        .attr("r", 8)
        .attr("fill", "#fbbf24")
        .attr("stroke", "#f59e0b")
        .attr("stroke-width", 2);

      emotionIndicators
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("font-size", "10px")
        .text("🎉");
    }

    // Add axes
    g.append("g")
      .attr("transform", `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%m/%d")));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (innerHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Mood Score");

    // Interactive features
    dots
      .on("mouseover", function(event, d) {
        // Show detailed tooltip
        const tooltip = d3.select("body")
          .append("div")
          .attr("class", "mood-tooltip")
          .style("opacity", 0);

        tooltip
          .transition()
          .duration(200)
          .style("opacity", 0.9);

        tooltip
          .html(`
            <div class="tooltip-content">
              <strong>${new Date(d.date).toLocaleDateString()}</strong><br/>
              Mood: ${d.mood_score}/10<br/>
              Emotion: ${d.primary_emotion}<br/>
              Energy: ${d.energy_level}/10<br/>
              ${d.notes ? `<em>"${d.notes}"</em>` : ''}
            </div>
          `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");

        // Highlight dot
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 8)
          .attr("stroke-width", 3);
      })
      .on("mouseout", function(event, d) {
        // Remove tooltip
        d3.selectAll(".mood-tooltip").remove();

        // Reset dot
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 4 + (d.emotion_intensity * 3))
          .attr("stroke-width", 2);
      });

  }, [data, width, height, showEmotionIndicators]);

  return <svg ref={svgRef} />;
};
```

### 3. Emotion Heatmap Calendar

#### Description
A calendar-style heatmap showing daily emotional states with color-coded intensity.

#### Implementation
```python
class EmotionHeatmapData:
    """Generate heatmap calendar data"""
    
    def generate_heatmap_data(self, user_id: str, year: int = None) -> Dict[str, Any]:
        """Generate emotion heatmap for calendar view"""
        if not year:
            year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        mood_entries = self.get_mood_entries_by_date_range(user_id, start_date, end_date)
        
        # Create daily emotion summary
        daily_emotions = {}
        for entry in mood_entries:
            date_key = entry.created_at.strftime('%Y-%m-%d')
            
            if date_key not in daily_emotions:
                daily_emotions[date_key] = {
                    "emotions": [],
                    "mood_scores": [],
                    "intensities": []
                }
            
            daily_emotions[date_key]["emotions"].append(entry.primary_emotion or "neutral")
            daily_emotions[date_key]["mood_scores"].append(entry.mood_score)
            daily_emotions[date_key]["intensities"].append(entry.emotion_confidence or 0.5)
        
        # Generate heatmap cells
        heatmap_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            day_data = daily_emotions.get(date_key)
            
            if day_data:
                # Calculate dominant emotion and average intensity
                dominant_emotion = max(set(day_data["emotions"]), key=day_data["emotions"].count)
                avg_intensity = sum(day_data["intensities"]) / len(day_data["intensities"])
                avg_mood = sum(day_data["mood_scores"]) / len(day_data["mood_scores"])
            else:
                dominant_emotion = None
                avg_intensity = 0
                avg_mood = 0
            
            heatmap_data.append({
                "date": date_key,
                "emotion": dominant_emotion,
                "intensity": avg_intensity,
                "mood_score": avg_mood,
                "entry_count": len(day_data["emotions"]) if day_data else 0,
                "color": EMOTION_THEMES.get(dominant_emotion, {}).get("--theme-primary", "#e5e7eb") if dominant_emotion else "#f3f4f6"
            })
            
            current_date += timedelta(days=1)
        
        return {
            "year": year,
            "heatmap_data": heatmap_data,
            "emotion_summary": self._calculate_yearly_emotion_summary(daily_emotions),
            "config": {
                "cell_size": 12,
                "cell_spacing": 2,
                "show_weekday_labels": True,
                "show_month_labels": True,
                "interactive": True
            }
        }
```

### 4. Real-Time Emotion Flow Visualization

#### Description
A dynamic, flowing visualization showing real-time emotion transitions.

#### Implementation
```typescript
// components/charts/EmotionFlowChart.tsx
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

export const EmotionFlowChart: React.FC<EmotionFlowProps> = ({
  width = 600,
  height = 400,
  userId
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [emotionHistory, setEmotionHistory] = useState<EmotionFlowPoint[]>([]);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`ws://localhost:8003/ws/mood/${userId}`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === 'mood_update') {
        const newPoint: EmotionFlowPoint = {
          timestamp: new Date(),
          emotion: update.data.currentMood,
          intensity: update.data.confidence,
          color: update.data.theme['--theme-primary']
        };
        
        setEmotionHistory(prev => [...prev.slice(-50), newPoint]); // Keep last 50 points
      }
    };

    return () => ws.close();
  }, [userId]);

  useEffect(() => {
    if (!svgRef.current || emotionHistory.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Create flowing particle system
    const particles = svg.selectAll(".emotion-particle")
      .data(emotionHistory)
      .enter()
      .append("circle")
      .attr("class", "emotion-particle")
      .attr("r", d => 3 + (d.intensity * 5))
      .attr("fill", d => d.color)
      .attr("opacity", 0.7);

    // Animate particles flowing across screen
    particles
      .attr("cx", width + 50)
      .attr("cy", height / 2)
      .transition()
      .duration(5000)
      .ease(d3.easeLinear)
      .attr("cx", -50)
      .attr("cy", (d, i) => {
        // Create wave-like movement based on emotion
        const baseY = height / 2;
        const waveAmplitude = 50;
        const waveFrequency = 0.01;
        return baseY + Math.sin(i * waveFrequency) * waveAmplitude * d.intensity;
      })
      .on("end", function() {
        d3.select(this).remove();
      });

  }, [emotionHistory, width, height]);

  return (
    <div className="emotion-flow-container">
      <svg ref={svgRef} width={width} height={height} />
      <div className="flow-legend">
        <h3>Live Emotion Flow</h3>
        <p>Watch your emotions flow in real-time</p>
      </div>
    </div>
  );
};
```

## 🎨 Dynamic Theming Integration

### CSS Custom Properties System
```css
/* Dynamic emotion-based theming */
:root {
  /* Default theme */
  --theme-primary: #6B7280;
  --theme-bg: #F9FAFB;
  --theme-text-primary: #1F2937;
  --theme-text-secondary: #6B7280;
  --theme-accent: #4F46E5;
  
  /* Transition properties */
  --theme-transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Chart-specific theming */
.emotion-wheel-container {
  background: var(--theme-bg);
  border-radius: 16px;
  padding: 24px;
  transition: var(--theme-transition);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.mood-timeline-container {
  background: linear-gradient(135deg, var(--theme-bg) 0%, rgba(255, 255, 255, 0.8) 100%);
  transition: var(--theme-transition);
}

.chart-title {
  color: var(--theme-text-primary);
  transition: var(--theme-transition);
}

.chart-subtitle {
  color: var(--theme-text-secondary);
  transition: var(--theme-transition);
}
```

### Theme Application Service
```typescript
// services/themeService.ts
class DynamicThemeService {
  private currentTheme: EmotionTheme | null = null;

  applyEmotionTheme(emotion: string, intensity: number = 1.0): void {
    const baseTheme = EMOTION_THEMES[emotion] || EMOTION_THEMES.bad;
    const adjustedTheme = this.adjustThemeIntensity(baseTheme, intensity);
    
    // Apply to CSS custom properties
    Object.entries(adjustedTheme).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value);
    });
    
    this.currentTheme = adjustedTheme;
    
    // Emit theme change event for chart updates
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme: adjustedTheme, emotion, intensity }
    }));
  }

  private adjustThemeIntensity(theme: EmotionTheme, intensity: number): EmotionTheme {
    const adjusted = { ...theme };
    
    if (intensity < 0.5) {
      // Muted emotions - reduce saturation
      Object.keys(adjusted).forEach(key => {
        if (key.startsWith('--theme-')) {
          adjusted[key] = this.reduceSaturation(adjusted[key], 0.3);
        }
      });
    } else if (intensity > 0.8) {
      // Strong emotions - increase vibrancy
      Object.keys(adjusted).forEach(key => {
        if (key.startsWith('--theme-')) {
          adjusted[key] = this.increaseSaturation(adjusted[key], 0.2);
        }
      });
    }
    
    return adjusted;
  }

  private reduceSaturation(color: string, factor: number): string {
    // Implementation for color saturation adjustment
    return color; // Simplified
  }

  private increaseSaturation(color: string, factor: number): string {
    // Implementation for color saturation adjustment
    return color; // Simplified
  }
}
```

## 📡 Real-Time Data Flow

### WebSocket Integration
```python
# Real-time chart data updates
class ChartWebSocketManager:
    """Manages WebSocket connections for real-time chart updates"""
    
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def handle_mood_update(self, user_id: str, mood_data: Dict[str, Any]):
        """Handle mood update and send chart data updates"""
        if user_id not in self.connections:
            return
        
        # Generate updated chart data
        chart_updates = {
            "emotion_wheel": await self._generate_emotion_wheel_update(user_id, mood_data),
            "timeline": await self._generate_timeline_update(user_id, mood_data),
            "heatmap": await self._generate_heatmap_update(user_id, mood_data)
        }
        
        # Send to all user connections
        for websocket in self.connections[user_id]:
            try:
                await websocket.send_text(json.dumps({
                    "type": "chart_update",
                    "data": chart_updates,
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Failed to send chart update to user {user_id}: {e}")
    
    async def _generate_emotion_wheel_update(self, user_id: str, mood_data: Dict) -> Dict:
        """Generate real-time emotion wheel update"""
        # Calculate new emotion distribution
        recent_emotions = await self.get_recent_emotions(user_id, days=7)
        return EmotionWheelData().generate_wheel_segments(recent_emotions)
    
    async def _generate_timeline_update(self, user_id: str, mood_data: Dict) -> Dict:
        """Generate real-time timeline update"""
        return {
            "new_point": {
                "date": mood_data["created_at"],
                "mood_score": mood_data["mood_score"],
                "emotion_color": EMOTION_THEMES.get(mood_data.get("primary_emotion", "bad"))["--theme-primary"],
                "emotion_intensity": mood_data.get("emotion_confidence", 0.5)
            }
        }
```

## 🚀 Performance Optimizations

### Chart Rendering Optimizations
```typescript
// Optimized chart rendering with React.memo and useMemo
export const OptimizedEmotionWheelChart = React.memo<EmotionWheelProps>(({
  data,
  width,
  height,
  onEmotionSelect
}) => {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    return processEmotionWheelData(data);
  }, [data]);

  const chartConfig = useMemo(() => ({
    width: width || 400,
    height: height || 400,
    innerRadius: 50,
    outerRadius: 180
  }), [width, height]);

  // Use RAF for smooth animations
  const animateChart = useCallback((svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) => {
    requestAnimationFrame(() => {
      // Perform chart updates
      updateChartElements(svg, processedData);
    });
  }, [processedData]);

  return <svg ref={svgRef} />;
}, (prevProps, nextProps) => {
  // Custom comparison for memo
  return (
    prevProps.data === nextProps.data &&
    prevProps.width === nextProps.width &&
    prevProps.height === nextProps.height
  );
});
```

### Data Caching Strategy
```python
class ChartDataCache:
    """Intelligent caching for chart data"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = {
            "emotion_wheel": 300,  # 5 minutes
            "timeline": 600,       # 10 minutes
            "heatmap": 3600        # 1 hour
        }
    
    async def get_cached_chart_data(self, chart_type: str, user_id: str, params: Dict) -> Optional[Dict]:
        """Get cached chart data if available and valid"""
        cache_key = self._generate_cache_key(chart_type, user_id, params)
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        return None
    
    async def cache_chart_data(self, chart_type: str, user_id: str, params: Dict, data: Dict):
        """Cache chart data with appropriate TTL"""
        cache_key = self._generate_cache_key(chart_type, user_id, params)
        ttl = self.cache_ttl.get(chart_type, 300)
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )
    
    def _generate_cache_key(self, chart_type: str, user_id: str, params: Dict) -> str:
        """Generate unique cache key"""
        param_string = "_".join(f"{k}_{v}" for k, v in sorted(params.items()))
        return f"chart_data:{chart_type}:{user_id}:{param_string}"
```

## 📊 Analytics & Insights

### Chart Interaction Analytics
```python
class ChartAnalytics:
    """Track chart interactions and generate insights"""
    
    async def track_chart_interaction(self, user_id: str, chart_type: str, interaction_type: str, data: Dict):
        """Track user interactions with charts"""
        interaction_record = {
            "user_id": user_id,
            "chart_type": chart_type,
            "interaction_type": interaction_type,  # view, click, hover, drill_down
            "interaction_data": data,
            "timestamp": datetime.now(),
            "session_id": data.get("session_id")
        }
        
        # Store in analytics database
        await self.store_interaction(interaction_record)
        
        # Generate insights if threshold reached
        if await self.should_generate_insights(user_id):
            await self.generate_chart_insights(user_id)
    
    async def generate_chart_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights based on chart interactions"""
        interactions = await self.get_user_interactions(user_id, days=30)
        
        insights = {
            "most_viewed_chart": self._find_most_viewed_chart(interactions),
            "preferred_time_range": self._analyze_time_preferences(interactions),
            "emotion_focus": self._analyze_emotion_focus(interactions),
            "engagement_patterns": self._analyze_engagement_patterns(interactions)
        }
        
        return insights
```

## 🎯 Summary

The Dynamic Mood Charts system provides:

1. **Interactive Emotion Wheel**: Hierarchical emotion visualization with real-time updates
2. **Mood Timeline**: Emotion-colored timeline with smooth animations
3. **Emotion Heatmap**: Calendar-style emotional state visualization
4. **Real-Time Flow**: Live emotion transition visualization
5. **Dynamic Theming**: Automatic theme adaptation based on emotions
6. **Performance Optimization**: Caching, memoization, and efficient rendering
7. **Analytics Integration**: User interaction tracking and insights generation

All charts integrate seamlessly with the existing MantraPath architecture and provide real-time updates via WebSocket connections, creating an immersive and responsive user experience that adapts to the user's emotional state in real-time.

