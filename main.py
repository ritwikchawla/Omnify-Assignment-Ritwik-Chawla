from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

app = FastAPI()

# Models
class FitnessClass(BaseModel):
    id: str
    name: str
    datetime: datetime
    instructor: str
    available_slots: int

class BookingRequest(BaseModel):
    class_id: str
    client_name: str
    client_email: EmailStr

class Booking(BaseModel):
    id: str
    class_id: str
    class_name: str
    client_name: str
    client_email: EmailStr
    booked_at: datetime

# In-memory "database"
fitness_classes: List[FitnessClass] = [
    FitnessClass(id="1", name="Yoga", datetime=datetime(2025, 6, 10, 9, 0), instructor="Alice", available_slots=5),
    FitnessClass(id="2", name="Zumba", datetime=datetime(2025, 6, 10, 11, 0), instructor="Bob", available_slots=3),
    FitnessClass(id="3", name="HIIT", datetime=datetime(2025, 6, 10, 18, 0), instructor="Charlie", available_slots=4),
]

bookings: List[Booking] = []

# Endpoints

@app.get("/classes", response_model=List[FitnessClass])
def get_classes():
    return fitness_classes

@app.post("/book", response_model=Booking)
def book_class(booking_req: BookingRequest):
    # Find class
    target_class = next((cls for cls in fitness_classes if cls.id == booking_req.class_id), None)
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check slot availability
    if target_class.available_slots <= 0:
        raise HTTPException(status_code=400, detail="No slots available for this class")

    # Reduce slot and confirm booking
    target_class.available_slots -= 1
    booking = Booking(
        id=str(uuid4()),
        class_id=target_class.id,
        class_name=target_class.name,
        client_name=booking_req.client_name,
        client_email=booking_req.client_email,
        booked_at=datetime.now()
    )
    bookings.append(booking)
    return booking

@app.get("/bookings", response_model=List[Booking])
def get_bookings(email: EmailStr = Query(..., description="Client email to search bookings")):
    return [b for b in bookings if b.client_email == email]
