# MantraPath Pre-Launch Website 🚀

A beautiful, responsive showcase website for MantraPath - your comprehensive mental wellness platform.

## 🌟 Features

- **Fully Responsive Design** - Optimized for all devices (mobile, tablet, desktop)
- **Modern CSS Grid & Flexbox** - Professional layout system
- **Mobile-First Approach** - Designed with mobile users in mind
- **Touch-Friendly Interface** - Optimized for touch interactions
- **Smooth Animations** - Elegant scroll-triggered animations
- **Accessibility Focused** - WCAG compliant with proper focus management
- **Performance Optimized** - Fast loading with lazy loading support
- **Dark Mode Support** - Automatic dark mode detection
- **High Contrast Support** - Accessible for users with visual needs

## 📱 Mobile Optimizations

### Responsive Breakpoints
- **Mobile**: < 480px
- **Mobile Large**: 480px - 767px  
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

### Mobile Features
- Hamburger menu with smooth animations
- Touch-friendly button sizes (minimum 44px)
- Swipe gestures support
- Mobile-optimized typography scaling
- Thumb-friendly navigation
- Fast tap response times

## 🎨 Design System

### Colors
- **Primary**: #667eea (Gradient start)
- **Secondary**: #764ba2 (Gradient end)
- **Text Primary**: #333333
- **Text Secondary**: #666666
- **Background**: #ffffff
- **Accent**: #f8fafc

### Typography
- **Font Family**: Inter (Google Fonts)
- **Responsive sizing**: clamp() for fluid typography
- **Font Weights**: 300, 400, 500, 600, 700

### Components
- **Buttons**: Primary & Secondary variants
- **Cards**: Feature cards, community cards, timeline items
- **Navigation**: Fixed header with scroll effects
- **Animations**: Scroll-triggered reveals, floating elements

## 🚀 Deployment Options

### Option 1: Static Hosting (Recommended)

**Netlify (Free)**
```bash
# Drag and drop the pre-launch folder to netlify.com
# Or connect to GitHub repository
# Custom domain: Configure DNS to point to Netlify
```

**Vercel (Free)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd pre-launch
vercel --prod
```

**GitHub Pages (Free)**
```bash
# Push to GitHub repository
# Enable GitHub Pages in repository settings
# Select source as main branch / root folder
```

### Option 2: Traditional Web Hosting

**cPanel/WHM Hosting**
```bash
# Upload files via FTP or File Manager
# Extract to public_html folder
# Configure domain DNS
```

**AWS S3 + CloudFront**
```bash
# Create S3 bucket
# Enable static website hosting
# Upload files
# Configure CloudFront distribution
# Set up custom domain with Route 53
```

### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Deploy:
```bash
docker build -t mantrapath-prelaunch .
docker run -p 80:80 mantrapath-prelaunch
```

## 🌐 DNS Configuration

### For Custom Domain (e.g., preview.mantrapath.com)

**DNS Records:**
```
Type: CNAME
Name: preview
Value: your-hosting-provider-url
TTL: 300
```

**Or A Record:**
```
Type: A  
Name: preview
Value: hosting-provider-ip
TTL: 300
```

## 📊 Performance Optimizations

### Already Implemented
- ✅ Minified CSS with optimal selectors
- ✅ Compressed images references
- ✅ Lazy loading support
- ✅ Efficient animations (transform/opacity)
- ✅ Debounced scroll/resize handlers
- ✅ Intersection Observer for animations

### Additional Optimizations (Optional)
```html
<!-- Add to <head> for even better performance -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="//cdnjs.cloudflare.com">

<!-- Add Service Worker for caching -->
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
</script>
```

## 🔧 Customization

### Update Content
Edit `index.html` to modify:
- Hero section text and stats
- Feature descriptions
- Mission statement
- Company information
- Contact details

### Styling Changes
Edit `styles.css` to modify:
- Color scheme (CSS custom properties)
- Typography (font sizes, families)
- Layout (grid/flexbox properties)
- Animations (keyframes, transitions)

### Functionality
Edit `script.js` to modify:
- Mobile menu behavior
- Scroll animations
- Form handling
- Analytics integration

## 📱 Testing Checklist

### Mobile Testing
- [ ] Test on iPhone (Safari)
- [ ] Test on Android (Chrome)
- [ ] Test on iPad (Safari)
- [ ] Verify touch interactions
- [ ] Check mobile menu functionality
- [ ] Test orientation changes

### Performance Testing
- [ ] Google PageSpeed Insights (>90 score)
- [ ] GTmetrix analysis
- [ ] Mobile usability test
- [ ] Cross-browser compatibility

### Accessibility Testing
- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Color contrast ratios
- [ ] Focus indicators
- [ ] ARIA labels

## 🚀 Launch Checklist

### Pre-Launch
- [ ] Content review and approval
- [ ] Mobile responsiveness verification
- [ ] Performance optimization
- [ ] SEO meta tags review
- [ ] Analytics setup (Google Analytics)
- [ ] Error tracking setup (Sentry)

### Launch Day
- [ ] DNS propagation verification
- [ ] SSL certificate activation
- [ ] Final performance test
- [ ] Mobile functionality verification
- [ ] Social media preview test

### Post-Launch
- [ ] Monitor analytics
- [ ] Track user feedback
- [ ] Performance monitoring
- [ ] Regular content updates

## 📈 Analytics Integration

### Google Analytics 4
```html
<!-- Add before closing </head> tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Event Tracking
```javascript
// Track button clicks
gtag('event', 'click', {
  event_category: 'engagement',
  event_label: 'cta_button'
});
```

## 🛡️ Security Headers

### Recommended Headers
```
Content-Security-Policy: default-src 'self' 'unsafe-inline' *.googleapis.com *.gstatic.com *.cdnjs.cloudflare.com
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

## 📞 Support

For technical support or customization requests:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🏆 Browser Support

- **Chrome**: 70+
- **Firefox**: 65+
- **Safari**: 12+
- **Edge**: 79+
- **Mobile Safari**: 12+
- **Chrome Mobile**: 70+

---

**Ready to showcase MantraPath to the world!** 🌟

This pre-launch website represents the beginning of an amazing journey in mental wellness technology. Built with care, optimized for all users, and ready to inspire your community.
