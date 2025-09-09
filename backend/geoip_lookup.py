#!/usr/bin/python3

# Source: https://github.com/O-X-L/haproxy-geoip
# Copyright (C) 2024 Rath Pascal
# License: MIT
# Modified to use FastAPI and uvicorn

# requirements: pip install maxminddb fastapi uvicorn[standard]

import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
import maxminddb
from maxminddb import open_database

# Configuration
PORT = int(os.getenv('PORT', '6970'))
HOST = os.getenv('HOST', '0.0.0.0')

# for data schema see:
#   ipinfo: https://github.com/ipinfo/sample-database
#   maxmind: https://github.com/maxmind/MaxMind-DB/tree/main/source-data

# ipinfo - https://ipinfo.io/account/data-downloads
#DATABASES = {
#    'country': {'file': '/tmp/country.mmdb', 'attr': 'country', 'fallback': '00'},
#    'continent': {'file': '/tmp/country.mmdb', 'attr': 'continent', 'fallback': '00'},
#    'city': {'file': '/tmp/city.mmdb', 'attr': 'city', 'fallback': '-'},
#    'asn': {'file': '/tmp/asn.mmdb', 'attr': 'asn', 'fallback': '0'},
#    'asname': {'file': '/tmp/asn.mmdb', 'attr': 'name', 'fallback': '-'},
#}

# maxmind
DATABASES = {
    'country': {'file': '/tmp/country.mmdb', 'attr': 'country.iso_code', 'fallback': '00'},
    'continent': {'file': '/tmp/country.mmdb', 'attr': 'continent.code', 'fallback': '00'},
    'city': {'file': '/tmp/city.mmdb', 'attr': 'city.names.en', 'fallback': '-'},
    'asn': {'file': '/tmp/asn.mmdb', 'attr': 'autonomous_system_number', 'fallback': '0'},
    'asname': {'file': '/tmp/asn.mmdb', 'attr': 'autonomous_system_organization', 'fallback': '-'},
}

# Global database readers cache
db_readers = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Open database connections
    print("Starting GeoIP lookup service...")
    for lookup_type, db_config in DATABASES.items():
        db_file = db_config['file']
        if Path(db_file).is_file():
            try:
                db_readers[lookup_type] = open_database(db_file)
                print(f"Loaded database: {lookup_type} from {db_file}")
            except Exception as e:
                print(f"Failed to load database {lookup_type}: {e}")
        else:
            print(f"Database file not found: {db_file}")
    
    print(f"Service ready on {HOST}:{PORT}")
    yield
    
    # Shutdown: Close database connections
    print("Shutting down...")
    for reader in db_readers.values():
        reader.close()


app = FastAPI(
    title="GeoIP Lookup Service",
    description="Fast GeoIP lookup service using MaxMind databases",
    version="1.0.0",
    lifespan=lifespan
)


def _lookup_mmdb(db_config: dict, ip: str, lookup_type: str) -> str:
    """Lookup IP in MaxMind database"""
    try:
        # Use cached reader if available
        if lookup_type in db_readers:
            db_reader = db_readers[lookup_type]
        else:
            # Fallback to opening database if not cached
            if not Path(db_config['file']).is_file():
                return db_config['fallback']
            db_reader = open_database(db_config['file'])

        data = db_reader.get(ip)
        if not data:
            return db_config['fallback']

        # Navigate through nested attributes (e.g., 'country.iso_code')
        for attr in db_config['attr'].split('.'):
            if isinstance(data, dict) and attr in data:
                data = data[attr]
            else:
                return db_config['fallback']

        return str(data) if data is not None else db_config['fallback']

    except (RuntimeError, KeyError, maxminddb.InvalidDatabaseError, ValueError) as e:
        print(f"Lookup error for {ip} in {lookup_type}: {e}")
        return db_config['fallback']


@app.get("/", response_class=PlainTextResponse)
async def geoip_lookup(
    lookup: str = Query(..., description="Type of lookup: country, continent, city, asn, asname"),
    ip: str = Query(..., description="IP address to lookup")
):
    """
    Perform GeoIP lookup for the specified IP address
    
    - **lookup**: Type of data to retrieve (country, continent, city, asn, asname)
    - **ip**: IP address to lookup (IPv4 or IPv6)
    """
    
    # Validate lookup type
    if lookup not in DATABASES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported lookup type '{lookup}'. Supported types: {', '.join(DATABASES.keys())}"
        )
    
    # Validate IP format (basic check)
    if not ip or ip.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="IP address cannot be empty"
        )
    
    # Perform lookup
    result = _lookup_mmdb(DATABASES[lookup], ip.strip(), lookup)
    print(f"{lookup} | {ip} => {result}")
    
    return result


@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    """Health check endpoint"""
    return "OK"


@app.get("/info")
async def service_info():
    """Get service information and available databases"""
    available_dbs = {}
    for lookup_type, db_config in DATABASES.items():
        db_file = db_config['file']
        available_dbs[lookup_type] = {
            "file": db_file,
            "available": Path(db_file).is_file(),
            "cached": lookup_type in db_readers
        }
    
    return {
        "service": "GeoIP Lookup Service",
        "version": "1.0.0",
        "databases": available_dbs,
        "supported_lookups": list(DATABASES.keys())
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "geoip_lookup:app",
        host=HOST,
        port=PORT,
        reload=False,
        access_log=True
    )
