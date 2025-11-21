"""
Database Schemas for H2Ok

Each Pydantic model corresponds to a MongoDB collection. The collection name is the lowercase of the class name.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class Partner(BaseModel):
    """
    Water refill partner points (collection: "partner")
    """
    name: str = Field(..., description="Partner name")
    address: str = Field(..., description="Full address")
    latitude: float = Field(..., description="Latitude (WGS84)")
    longitude: float = Field(..., description="Longitude (WGS84)")
    category: Literal["shop","cafe","university","sports","other"] = Field(..., description="Type of place")
    open_hours: Optional[str] = Field(None, description="Opening hours text, e.g. 09:00-21:00")
    has_cold: bool = Field(True, description="Cold water available")
    has_hot: bool = Field(False, description="Hot water available")
    access_type: Literal["free","ask-staff"] = Field("free", description="Access rules")
    is_new: bool = Field(False, description="Highlight as new partner")

class Update(BaseModel):
    """
    News and updates (collection: "update")
    """
    title: str
    content: str
    tag: Optional[str] = Field(None, description="Category tag")
    external_url: Optional[str] = None
