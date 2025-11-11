"""
MongoDB client for database operations
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from loguru import logger
from config import settings

class MongoDBClient:
    """MongoDB client wrapper"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client.get_default_database()
            
            # Test connection
            await self.client.server_info()
            logger.success("✅ MongoDB connected successfully")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    def get_collection(self, collection_name: str):
        """Get a collection"""
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db[collection_name]

# Global client instance
mongodb_client = MongoDBClient()
