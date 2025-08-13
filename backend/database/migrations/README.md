# MantraPath Database Migrations - README

## Migration Sequence (PostgreSQL - Authoritative)

The following migrations should be applied in order for PostgreSQL deployments:

### Active Migration Chain:
1. **001_enhanced_ai_context_tables.sql** - ⚠️ **SKIP FOR POSTGRES** (MySQL syntax)
   - Contains MySQL-specific: JSON, UUID(), ON UPDATE CURRENT_TIMESTAMP
   - **DECISION: Skip this migration for PostgreSQL deployments**

2. **002_add_mood_enhancement_columns.sql** - ✅ **AUTHORITATIVE**
   - PostgreSQL syntax (JSONB, gen_random_uuid(), TIMESTAMPTZ)
   - Phase 1 mood service enhancements
   - Includes: emotional_weather_forecasts, celebration_moments, adaptive_questions, environmental_data

3. **003_user_language_preferences.sql** - ✅ **NEW (E1 - Multilingual Foundation)**
   - User language preference table supporting 15 languages
   - Languages: en, hi, ta, te, mr, bn, gu, kn, ml, pa, or, ur, ar, es, fr
   - Regions: IN, US, CA, GB, AE, SA, ES, FR, BD, PK
   - Includes backfill for existing users

### Legacy/Superseded Files:
- `002_add_mood_enhancements.sql` - duplicate/legacy version
- `002_mood_service_phase1_enhancement.sql` - duplicate/legacy version  
- `001_enhanced_ai_context_tables_sqlite.sql` - SQLite variant

## Deployment Notes:

### For PostgreSQL (Production):
```bash
# Skip 001 (MySQL syntax) or convert to PostgreSQL
psql -d mantrapath < 002_add_mood_enhancement_columns.sql
psql -d mantrapath < 003_user_language_preferences.sql
```

### For Development (if using SQLite):
Use the _sqlite.sql variants where available.

## Current Schema State:
- ✅ User management (users, user_profiles)
- ✅ Mood tracking with Phase 1 enhancements
- ✅ Journal entries
- ✅ Chat sessions
- ✅ Language preferences (NEW - E1)
- ⏳ Unified insights backend (E2 - pending)
- ⏳ Achievements engine (E3 - pending)

## Migration Verification:
After applying migrations, verify with:
```sql
-- Check if all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verify language preferences table
SELECT COUNT(*) FROM user_language_preferences;
```
