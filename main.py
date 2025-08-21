from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from fuzzywuzzy import fuzz, process
from typing import List, Dict, Optional
import os

app = FastAPI(
    title="Name Similarity Checker",
    description="API to check name similarity against a blacklist",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NameCheckRequest(BaseModel):
    name: str
    threshold: Optional[float] = 80.0

class SimilarityResult(BaseModel):
    blacklist_name: str
    similarity_score: float
    category: str
    notes: str

class NameCheckResponse(BaseModel):
    input_name: str
    is_match: bool
    matches: List[SimilarityResult]
    highest_similarity: float

# Global variable to store blacklist data
blacklist_df = None

def load_blacklist():
    """Load the blacklist from CSV file"""
    global blacklist_df
    csv_path = "blacklist.csv"
    if os.path.exists(csv_path):
        blacklist_df = pd.read_csv(csv_path)
        return True
    return False

@app.on_event("startup")
async def startup_event():
    """Load blacklist data on startup"""
    if not load_blacklist():
        print("Warning: blacklist.csv not found. Some endpoints may not work.")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Name Similarity Checker API",
        "description": "Check name similarity against blacklist",
        "endpoints": {
            "/check-name": "POST - Check a name against the blacklist",
            "/blacklist": "GET - View all blacklisted names",
            "/similarity/{name}": "GET - Get similarity scores for a name"
        }
    }

@app.post("/check-name", response_model=NameCheckResponse)
async def check_name(request: NameCheckRequest):
    """
    Check if a name is similar to any name in the blacklist
    """
    if blacklist_df is None:
        raise HTTPException(status_code=500, detail="Blacklist not loaded")
    
    input_name = request.name.strip()
    threshold = request.threshold
    
    matches = []
    highest_similarity = 0.0
    
    for _, row in blacklist_df.iterrows():
        blacklist_name = str(row['name'])
        
        # Calculate different similarity scores
        ratio = fuzz.ratio(input_name, blacklist_name)
        partial_ratio = fuzz.partial_ratio(input_name, blacklist_name)
        token_sort_ratio = fuzz.token_sort_ratio(input_name, blacklist_name)
        token_set_ratio = fuzz.token_set_ratio(input_name, blacklist_name)
        
        # Take the highest similarity score
        similarity_score = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
        
        if similarity_score > highest_similarity:
            highest_similarity = similarity_score
        
        if similarity_score >= threshold:
            matches.append(SimilarityResult(
                blacklist_name=blacklist_name,
                similarity_score=similarity_score,
                category=str(row['category']),
                notes=str(row['notes'])
            ))
    
    # Sort matches by similarity score (highest first)
    matches.sort(key=lambda x: x.similarity_score, reverse=True)
    
    return NameCheckResponse(
        input_name=input_name,
        is_match=len(matches) > 0,
        matches=matches,
        highest_similarity=highest_similarity
    )

@app.get("/similarity/{name}")
async def get_similarity_scores(name: str):
    """
    Get similarity scores for a name against all blacklisted names
    """
    if blacklist_df is None:
        raise HTTPException(status_code=500, detail="Blacklist not loaded")
    
    input_name = name.strip()
    results = []
    
    for _, row in blacklist_df.iterrows():
        blacklist_name = str(row['name'])
        
        # Calculate different similarity scores
        ratio = fuzz.ratio(input_name, blacklist_name)
        partial_ratio = fuzz.partial_ratio(input_name, blacklist_name)
        token_sort_ratio = fuzz.token_sort_ratio(input_name, blacklist_name)
        token_set_ratio = fuzz.token_set_ratio(input_name, blacklist_name)
        
        results.append({
            "blacklist_name": blacklist_name,
            "category": str(row['category']),
            "similarity_scores": {
                "ratio": ratio,
                "partial_ratio": partial_ratio,
                "token_sort_ratio": token_sort_ratio,
                "token_set_ratio": token_set_ratio,
                "max_score": max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
            }
        })
    
    # Sort by max similarity score
    results.sort(key=lambda x: x["similarity_scores"]["max_score"], reverse=True)
    
    return {
        "input_name": input_name,
        "results": results
    }

@app.get("/blacklist")
async def get_blacklist():
    """
    Get all names in the blacklist
    """
    if blacklist_df is None:
        raise HTTPException(status_code=500, detail="Blacklist not loaded")
    
    return {
        "total_entries": len(blacklist_df),
        "blacklist": blacklist_df.to_dict('records')
    }

@app.post("/add-to-blacklist")
async def add_to_blacklist(name: str, category: str, notes: str = ""):
    """
    Add a new name to the blacklist
    """
    global blacklist_df
    
    if blacklist_df is None:
        raise HTTPException(status_code=500, detail="Blacklist not loaded")
    
    # Check if name already exists
    if name in blacklist_df['name'].values:
        raise HTTPException(status_code=400, detail="Name already exists in blacklist")
    
    # Add new entry
    new_entry = pd.DataFrame({
        'name': [name],
        'category': [category],
        'notes': [notes]
    })
    
    blacklist_df = pd.concat([blacklist_df, new_entry], ignore_index=True)
    
    # Save to CSV
    blacklist_df.to_csv("blacklist.csv", index=False)
    
    return {
        "message": "Name added to blacklist successfully",
        "name": name,
        "category": category,
        "notes": notes
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)