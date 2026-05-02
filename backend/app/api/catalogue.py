from fastapi import APIRouter, HTTPException
import sqlite3
import json
from pathlib import Path

router = APIRouter()

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "database" / "messier.db"
    return sqlite3.connect(db_path)

@router.get("/messier")
def get_messier_catalogue():
    """Get all Messier objects from the catalogue"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects ORDER BY messier_number")
        rows = cursor.fetchall()
        
        objects = []
        for row in rows:
            obj = dict(row)
            obj['best_months'] = json.loads(obj['best_months'])
            objects.append(obj)
        
        conn.close()
        
        return {"objects": objects, "count": len(objects)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messier/{object_id}")
def get_messier_object(object_id: str):
    """Get a specific Messier object by ID"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects WHERE id = ?", (object_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Object {object_id} not found")
        
        obj = dict(row)
        obj['best_months'] = json.loads(obj['best_months'])
        
        conn.close()
        
        return obj
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
