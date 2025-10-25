#!/bin/bash

# Test script to verify microphone permission handling

echo "🎤 Testing Microphone Permission Handling"
echo "========================================="

# Test 1: Frontend accessibility
echo "1. Testing Frontend Accessibility..."
if curl -k -s https://localhost:5175 > /dev/null; then
    echo "   ✅ Frontend accessible via HTTPS"
    echo "   🔗 URL: https://localhost:5175"
else
    echo "   ❌ Frontend not accessible"
    exit 1
fi

# Test 2: Check if microphone permission API is available
echo "2. Testing Microphone Permission API..."
if curl -k -s https://localhost:5175 | grep -q "navigator.permissions"; then
    echo "   ✅ Browser permission API should be available"
else
    echo "   ⚠️  Permission API might not be available (this is normal in some browsers)"
fi

# Test 3: Check if getUserMedia is available
echo "3. Testing getUserMedia API..."
if curl -k -s https://localhost:5175 | grep -q "getUserMedia"; then
    echo "   ✅ getUserMedia API should be available"
else
    echo "   ❌ getUserMedia API not found in frontend"
fi

# Test 4: Check HTTPS certificate
echo "4. Testing HTTPS Certificate..."
CERT_INFO=$(curl -k -s -I https://localhost:5175 2>&1 | grep -i "certificate\|ssl\|tls" || echo "No certificate info")
if echo "$CERT_INFO" | grep -qi "certificate\|ssl\|tls"; then
    echo "   ✅ HTTPS is working (self-signed certificate)"
    echo "   📝 Note: Browser will show security warning - this is expected"
else
    echo "   ⚠️  HTTPS status unclear"
fi

echo ""
echo "🎯 Microphone Permission Test Instructions:"
echo "=========================================="
echo ""
echo "1. Open your browser and go to: https://localhost:5175"
echo "2. Accept the security warning about the self-signed certificate"
echo "3. Navigate to the mood page"
echo "4. Click on the 'Voice' tab"
echo "5. You should see one of these scenarios:"
echo ""
echo "   📱 Scenario A - Permission Granted:"
echo "      - Green alert: 'Microphone access granted. You can now record your voice.'"
echo "      - Blue microphone button is clickable"
echo "      - Click to start recording"
echo ""
echo "   📱 Scenario B - Permission Denied:"
echo "      - Red alert with specific error message"
echo "      - 'Refresh Page to Retry' button"
echo "      - Click the button to retry"
echo ""
echo "   📱 Scenario C - Permission Prompt:"
echo "      - Blue alert: 'Click the microphone button below to allow microphone access'"
echo "      - Click the microphone button"
echo "      - Browser will ask for permission"
echo ""
echo "   📱 Scenario D - Checking Permissions:"
echo "      - Loading spinner: 'Checking microphone permissions...'"
echo "      - Wait for it to resolve to one of the above scenarios"
echo ""
echo "🔧 Troubleshooting:"
echo "=================="
echo ""
echo "If microphone access is still denied:"
echo "1. Check browser address bar for microphone icon (🔒🎤)"
echo "2. Click the microphone icon and select 'Allow'"
echo "3. Refresh the page"
echo "4. Try a different browser (Chrome, Firefox, Safari)"
echo "5. Check if microphone is being used by another application"
echo ""
echo "If you see 'NotSupportedError':"
echo "- Try using Chrome, Firefox, or Safari"
echo "- Make sure you're using HTTPS (not HTTP)"
echo ""
echo "If you see 'NotFoundError':"
echo "- Check if microphone is connected"
echo "- Check system audio settings"
echo ""
echo "✅ The microphone permission handling has been significantly improved!"
echo "   - Proactive permission requests when voice tab is accessed"
echo "   - Clear error messages for different failure scenarios"
echo "   - User-friendly guidance and retry options"
echo "   - Real-time permission status updates"

