# GeoIP Lookup Service

A containerized GeoIP lookup service using MaxMind databases.

## Prerequisites

You need MaxMind database files. The service expects these files in the `/tmp` directory inside the container:

### For IPInfo databases:
- `country.mmdb` (for country and continent lookups)
- `city.mmdb` (for city lookups)  
- `asn.mmdb` (for ASN and AS name lookups)

### For MaxMind databases:
- Uncomment the MaxMind section in `geoip_lookup.py` and comment out the IPInfo section

## Setup

1. **Create data directory and add MMDB files:**
   ```bash
   mkdir data
   # Copy your .mmdb files to the data directory
   cp /path/to/your/*.mmdb ./data/
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Or build and run manually:**
   ```bash
   docker build -t geoip-lookup .
   docker run -d -p 6970:6970 -v $(pwd)/data:/tmp:ro geoip-lookup
   ```

## Usage

The service provides HTTP GET endpoints with query parameters:

### Parameters:
- `lookup`: Type of lookup (`country`, `continent`, `city`, `asn`, `asname`)
- `ip`: IP address to lookup

### Examples:

```bash
# Country lookup
curl "http://localhost:6970/?lookup=country&ip=8.8.8.8"

# City lookup  
curl "http://localhost:6970/?lookup=city&ip=8.8.8.8"

# ASN lookup
curl "http://localhost:6970/?lookup=asn&ip=8.8.8.8"

# Continent lookup
curl "http://localhost:6970/?lookup=continent&ip=1.1.1.1"
```

## Database Sources

### IPInfo (Free tier available)
- Sign up at https://ipinfo.io/account/data-downloads
- Download: Country, City, ASN databases

### MaxMind (Free GeoLite2 available)
- Sign up at https://www.maxmind.com/en/geolite2/signup
- Download: GeoLite2-Country, GeoLite2-City, GeoLite2-ASN

## File Structure

```
.
├── geoip_lookup.py     # Main application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container build instructions
├── docker-compose.yml # Container orchestration
├── data/             # Directory for MMDB files (create this)
│   ├── country.mmdb  # Place your MMDB files here
│   ├── city.mmdb
│   └── asn.mmdb
└── README.md         # This file
```

## Health Check

The service includes a health check that tests the country lookup with IP 8.8.8.8.

## Notes

- Uses FastAPI and uvicorn for modern async performance
- Database files are mounted read-only for security  
- Database connections are cached at startup for better performance
- The service will return fallback values if databases are missing or lookups fail
- Interactive API documentation available at `/docs`
