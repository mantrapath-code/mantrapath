# MantraPath Data Directory

This directory contains all persistent data for the MantraPath application. Data is stored in host directories to ensure it survives container pruning, system restarts, and Docker cleanup operations.

## 📁 Directory Structure

```
/home/sachin/mantrapath/data/
├── postgres/          # PostgreSQL database files
├── redis/             # Redis cache data
├── nats/              # NATS JetStream data
├── ai-models/         # AI models cache
├── voice-models/      # Voice Service Vosk models
├── voice-audio/       # Voice Service audio files
├── models-data/       # Models Service data
├── models-cache/      # Models Service cache
└── README.md          # This file
```

## 🔒 Data Persistence

### What's Protected
- **Database**: All user data, mood entries, analytics, and application state
- **Cache**: Redis cache for performance optimization
- **Events**: NATS JetStream event history and subscriptions
- **AI Models**: Downloaded and cached AI models for emotion analysis
- **Voice Models**: Speech-to-Text and Text-to-Speech models
- **Audio Files**: Temporary voice processing files

### What's NOT Protected
- Container logs (stored in container filesystem)
- Temporary container files
- Build cache and intermediate layers

## 🛠️ Data Management

### Backup Data
```bash
# Create a complete backup
tar -czf mantrapath-backup-$(date +%Y%m%d).tar.gz /home/sachin/mantrapath/data/

# Restore from backup
tar -xzf mantrapath-backup-20241023.tar.gz -C /
```

### Clean Data (Reset Application)
```bash
# Stop all services
cd /home/sachin/mantrapath/backend
docker-compose down

# Remove all data (WARNING: This will delete all user data!)
sudo rm -rf /home/sachin/mantrapath/data/*

# Restart services (will create fresh data)
docker-compose up -d
```

### Partial Data Cleanup
```bash
# Clean only cache data (keeps user data)
rm -rf /home/sachin/mantrapath/data/redis/*
rm -rf /home/sachin/mantrapath/data/nats/*
rm -rf /home/sachin/mantrapath/data/ai-models/*
rm -rf /home/sachin/mantrapath/data/models-cache/*

# Clean only AI models (will re-download)
rm -rf /home/sachin/mantrapath/data/voice-models/*
rm -rf /home/sachin/mantrapath/data/models-data/*
```

## 📊 Disk Usage

### Check Data Size
```bash
# Check total data size
du -sh /home/sachin/mantrapath/data/

# Check individual directory sizes
du -sh /home/sachin/mantrapath/data/*

# Check database size specifically
du -sh /home/sachin/mantrapath/data/postgres/
```

### Monitor Growth
```bash
# Watch data growth in real-time
watch -n 5 'du -sh /home/sachin/mantrapath/data/*'
```

## 🔄 Migration

### Moving Data to Different Server
1. **Stop services**: `docker-compose down`
2. **Copy data**: `scp -r /home/sachin/mantrapath/data/ user@newserver:/home/sachin/mantrapath/`
3. **Update paths**: Modify docker-compose.yml if needed
4. **Start services**: `docker-compose up -d`

### Changing Data Location
1. **Stop services**: `docker-compose down`
2. **Move data**: `sudo mv /home/sachin/mantrapath/data /new/location/`
3. **Update docker-compose.yml**: Change volume paths
4. **Start services**: `docker-compose up -d`

## 🚨 Important Notes

### Permissions
- Data directories are owned by the container user
- Use `sudo` when modifying data outside containers
- Container user: `999:999` (postgres), `1001:1001` (redis)

### Security
- Data is stored in plain text (not encrypted)
- Ensure proper file permissions: `chmod 700 /home/sachin/mantrapath/data/`
- Consider encryption for production deployments

### Performance
- Host volumes may be slower than named volumes
- Consider using SSD storage for better performance
- Monitor disk I/O for bottlenecks

## 🐛 Troubleshooting

### Permission Issues
```bash
# Fix ownership
sudo chown -R 999:999 /home/sachin/mantrapath/data/postgres/
sudo chown -R 1001:1001 /home/sachin/mantrapath/data/redis/
```

### Disk Space Issues
```bash
# Check disk usage
df -h /home/sachin/mantrapath/data/

# Clean up old logs
find /home/sachin/mantrapath/data/ -name "*.log" -mtime +30 -delete
```

### Corrupted Data
```bash
# Stop services
docker-compose down

# Backup current data
cp -r /home/sachin/mantrapath/data /home/sachin/mantrapath/data-backup-$(date +%Y%m%d)

# Remove corrupted data
rm -rf /home/sachin/mantrapath/data/postgres/*

# Restart services (will recreate database)
docker-compose up -d
```

## 📈 Monitoring

### Health Checks
```bash
# Check if data directories exist
ls -la /home/sachin/mantrapath/data/

# Check if services can access data
docker-compose exec postgres ls -la /var/lib/postgresql/data/
docker-compose exec redis ls -la /data/
```

### Logs
```bash
# Check service logs
docker-compose logs postgres
docker-compose logs redis
docker-compose logs nats
```

---

**Data Directory**: `/home/sachin/mantrapath/data/`  
**Last Updated**: October 23, 2025  
**Version**: 1.0


