#!/bin/bash
# Activate Event Bus Integration Script
# This script uncomments event publishing code across all services

set -e

echo "🚀 Activating Event Bus Integration Across All Services"
echo "======================================================"

# Base directory for services
SERVICES_DIR="/Users/sachin/Desktop/mantrapath/backend/services"

# Function to backup a file before modification
backup_file() {
    local file=$1
    cp "$file" "$file.bak.$(date +%Y%m%d_%H%M%S)"
    echo "   ✅ Backed up: $file"
}

# Function to uncomment event imports and publishing
activate_events_in_service() {
    local service_name=$1
    local file_path=$2
    
    echo ""
    echo "🔧 Activating events in $service_name..."
    
    if [ ! -f "$file_path" ]; then
        echo "   ❌ File not found: $file_path"
        return 1
    fi
    
    # Backup the file
    backup_file "$file_path"
    
    # Uncomment event imports
    sed -i.tmp 's/^# from shared\.events import/from shared.events import/g' "$file_path"
    sed -i.tmp 's/^#from shared\.events import/from shared.events import/g' "$file_path"
    
    # Uncomment event publishing calls
    sed -i.tmp 's/^[[:space:]]*# await.*\.publish(/            await event_bus.publish(/g' "$file_path"
    sed -i.tmp 's/^[[:space:]]*#await.*\.publish(/            await event_bus.publish(/g' "$file_path"
    
    # Remove temporary files
    rm -f "$file_path.tmp"
    
    echo "   ✅ Events activated in $service_name"
}

# Function to add lifespan context manager
add_lifespan_manager() {
    local service_name=$1
    local file_path=$2
    
    echo "   🔄 Adding lifespan manager to $service_name..."
    
    # Check if lifespan is already present
    if grep -q "async def lifespan" "$file_path"; then
        echo "   ⚠️  Lifespan manager already exists in $service_name"
        return 0
    fi
    
    # Create lifespan code
    lifespan_code='
from contextlib import asynccontextmanager
from shared.events import get_enhanced_event_bus, cleanup_enhanced_event_bus

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with event bus initialization"""
    # Startup
    logger.info("Initializing enhanced event bus...")
    event_bus = get_enhanced_event_bus()
    await event_bus.initialize()
    logger.info("Enhanced event bus initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Cleaning up enhanced event bus...")
    await cleanup_enhanced_event_bus()
    logger.info("Enhanced event bus cleanup completed")

'
    
    # Find the line where FastAPI app is created and add lifespan
    if grep -q "app = FastAPI(" "$file_path"; then
        # Add lifespan parameter to existing FastAPI creation
        sed -i.tmp 's/app = FastAPI(/app = FastAPI(lifespan=lifespan, /g' "$file_path"
    else
        echo "   ❌ Could not find FastAPI app creation in $service_name"
        return 1
    fi
    
    # Add the lifespan code after imports
    # Find the last import line and add lifespan code after it
    local import_line=$(grep -n "^from\|^import" "$file_path" | tail -1 | cut -d: -f1)
    
    if [ -n "$import_line" ]; then
        # Insert lifespan code after last import
        sed -i.tmp "${import_line}a\\
$lifespan_code" "$file_path"
    fi
    
    rm -f "$file_path.tmp"
    echo "   ✅ Lifespan manager added to $service_name"
}

# Activate events in Mood Service
echo ""
echo "1️⃣  MOOD SERVICE"
activate_events_in_service "Mood Service" "$SERVICES_DIR/mood_service/main.py"
add_lifespan_manager "Mood Service" "$SERVICES_DIR/mood_service/main.py"

# Activate events in Community Service
echo ""
echo "2️⃣  COMMUNITY SERVICE"
activate_events_in_service "Community Service" "$SERVICES_DIR/community_service/main.py"
add_lifespan_manager "Community Service" "$SERVICES_DIR/community_service/main.py"

# Activate events in ML Service
echo ""
echo "3️⃣  ML SERVICE"
activate_events_in_service "ML Service" "$SERVICES_DIR/ml_service/main.py"
add_lifespan_manager "ML Service" "$SERVICES_DIR/ml_service/main.py"

# Check Translation Service (may already be active)
echo ""
echo "4️⃣  TRANSLATION SERVICE"
if grep -q "publish_translation_event" "$SERVICES_DIR/translation_service/main.py"; then
    echo "   ✅ Translation Service already has event publishing"
else
    activate_events_in_service "Translation Service" "$SERVICES_DIR/translation_service/main.py"
fi
add_lifespan_manager "Translation Service" "$SERVICES_DIR/translation_service/main.py"

# Add basic event subscriptions to Content Service
echo ""
echo "5️⃣  CONTENT SERVICE"
content_service_file="$SERVICES_DIR/content_service/main.py"

if [ -f "$content_service_file" ]; then
    backup_file "$content_service_file"
    
    # Add event imports
    if ! grep -q "from shared.events import" "$content_service_file"; then
        sed -i.tmp '/^from pydantic import/a\\
from shared.events import get_enhanced_event_bus, V3EventChannels' "$content_service_file"
    fi
    
    add_lifespan_manager "Content Service" "$content_service_file"
    
    # Add event subscription setup function
    subscription_code='

# Event subscription setup
async def setup_content_event_subscriptions():
    """Setup event subscriptions for content recommendations"""
    event_bus = get_enhanced_event_bus()
    
    @event_bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED)
    async def handle_mood_change(event):
        """Update content recommendations based on mood changes"""
        try:
            user_id = event.user_id
            mood_score = event.data.get("mood_score", 5)
            
            # Log mood-based content update
            logger.info(f"Updating content recommendations for user {user_id} based on mood {mood_score}")
            
            # Here you would implement mood-based content recommendation logic
            # For now, just log the event
            
        except Exception as e:
            logger.error(f"Error handling mood change event: {e}")
    
    logger.info("Content service event subscriptions setup completed")

'
    
    # Add subscription code
    echo "$subscription_code" >> "$content_service_file"
    
    rm -f "$content_service_file.tmp"
    echo "   ✅ Content Service event integration added"
fi

# Add basic event subscriptions to Profile Service  
echo ""
echo "6️⃣  PROFILE SERVICE"
profile_service_file="$SERVICES_DIR/profile_service/main.py"

if [ -f "$profile_service_file" ]; then
    backup_file "$profile_service_file"
    
    # Add event imports
    if ! grep -q "from shared.events import" "$profile_service_file"; then
        sed -i.tmp '/^from pydantic import/a\\
from shared.events import get_enhanced_event_bus, V3EventChannels' "$profile_service_file"
    fi
    
    add_lifespan_manager "Profile Service" "$profile_service_file"
    
    rm -f "$profile_service_file.tmp"
    echo "   ✅ Profile Service event integration added"
fi

# Create verification script
echo ""
echo "📝 Creating verification script..."
cat > "$SERVICES_DIR/../scripts/verify_event_activation.sh" << 'EOF'
#!/bin/bash
# Verify Event Bus Activation

echo "🔍 Verifying Event Bus Activation"
echo "================================="

SERVICES_DIR="/Users/sachin/Desktop/mantrapath/backend/services"

check_service_events() {
    local service_name=$1
    local file_path=$2
    
    echo ""
    echo "Checking $service_name..."
    
    if [ ! -f "$file_path" ]; then
        echo "   ❌ File not found: $file_path"
        return 1
    fi
    
    # Check for uncommented imports
    if grep -q "^from shared\.events import" "$file_path"; then
        echo "   ✅ Event imports are active"
    else
        echo "   ❌ Event imports still commented"
    fi
    
    # Check for lifespan manager
    if grep -q "async def lifespan" "$file_path"; then
        echo "   ✅ Lifespan manager present"
    else
        echo "   ❌ Lifespan manager missing"
    fi
    
    # Check for event publishing calls
    if grep -q "await.*\.publish(" "$file_path"; then
        echo "   ✅ Event publishing calls found"
    else
        echo "   ⚠️  No event publishing calls found"
    fi
}

check_service_events "Mood Service" "$SERVICES_DIR/mood_service/main.py"
check_service_events "Community Service" "$SERVICES_DIR/community_service/main.py"
check_service_events "ML Service" "$SERVICES_DIR/ml_service/main.py"
check_service_events "Translation Service" "$SERVICES_DIR/translation_service/main.py"
check_service_events "Content Service" "$SERVICES_DIR/content_service/main.py"
check_service_events "Profile Service" "$SERVICES_DIR/profile_service/main.py"

echo ""
echo "🎯 Next Steps:"
echo "1. Start services and check logs for event bus initialization"
echo "2. Test event publishing by creating mood entries"
echo "3. Monitor NATS streams: nats stream ls"
echo "4. Check service health: curl http://localhost:8000/health"

EOF

chmod +x "$SERVICES_DIR/../scripts/verify_event_activation.sh"

echo ""
echo "✅ Event Bus Activation Complete!"
echo "================================="
echo ""
echo "📁 Backup files created with timestamp suffix"
echo "🔧 Event imports uncommented in all services"
echo "⚡ Lifespan managers added for event bus initialization"
echo "📝 Verification script created: scripts/verify_event_activation.sh"
echo ""
echo "🎯 Next Steps:"
echo "1. Run verification: ./scripts/verify_event_activation.sh"
echo "2. Start services: ./start.sh backend"
echo "3. Test event flow: curl -X POST http://localhost:8003/mood-entries"
echo "4. Monitor events: nats stream ls"
echo ""
echo "⚠️  If issues occur, restore from backup files with .bak suffix"
