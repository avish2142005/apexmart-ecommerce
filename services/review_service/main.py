from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from services.common.database import get_db, Base, engine
from services.common.models import ReviewModel, ProductModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "review-service"

app = FastAPI(title="Review & Rating Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class SubmitReviewRequest(BaseModel):
    product_id: int
    user_id: int
    user_name: str
    rating: int # 1 to 5
    title: str
    comment: str

class ModerateReviewRequest(BaseModel):
    status: str # APPROVED, REJECTED

@app.post("/", status_code=status.HTTP_201_CREATED)
def submit_review(req: SubmitReviewRequest, db: Session = Depends(get_db)):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    review = ReviewModel(
        product_id=req.product_id,
        user_id=req.user_id,
        user_name=req.user_name,
        rating=req.rating,
        title=req.title,
        comment=req.comment,
        status="APPROVED"
    )
    db.add(review)

    # Re-calculate product average rating
    all_ratings = db.query(ReviewModel.rating).filter(
        ReviewModel.product_id == req.product_id,
        ReviewModel.status == "APPROVED"
    ).all()
    ratings_list = [r[0] for r in all_ratings] + [req.rating]
    avg_rating = round(sum(ratings_list) / len(ratings_list), 1)

    product = db.query(ProductModel).filter(ProductModel.id == req.product_id).first()
    if product:
        product.rating = avg_rating
        product.rating_count = len(ratings_list)

    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "product_id": review.product_id,
        "user_name": review.user_name,
        "rating": review.rating,
        "title": review.title,
        "comment": review.comment,
        "created_at": review.created_at.isoformat()
    }

@app.get("/product/{product_id}")
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(ReviewModel).filter(
        ReviewModel.product_id == product_id,
        ReviewModel.status == "APPROVED"
    ).order_by(ReviewModel.created_at.desc()).all()

    # Aggregate breakdown
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        counts[r.rating] = counts.get(r.rating, 0) + 1

    total = len(reviews)
    avg = round(sum(r.rating for r in reviews) / total, 1) if total > 0 else 5.0

    return {
        "product_id": product_id,
        "total_reviews": total,
        "average_rating": avg,
        "rating_breakdown": {
            "5_star": {"count": counts[5], "pct": round(counts[5]/total*100, 1) if total else 0},
            "4_star": {"count": counts[4], "pct": round(counts[4]/total*100, 1) if total else 0},
            "3_star": {"count": counts[3], "pct": round(counts[3]/total*100, 1) if total else 0},
            "2_star": {"count": counts[2], "pct": round(counts[2]/total*100, 1) if total else 0},
            "1_star": {"count": counts[1], "pct": round(counts[1]/total*100, 1) if total else 0},
        },
        "reviews": [{
            "id": r.id,
            "user_name": r.user_name,
            "rating": r.rating,
            "title": r.title,
            "comment": r.comment,
            "helpful_votes": r.helpful_votes,
            "verified_purchase": r.verified_purchase,
            "created_at": r.created_at.isoformat()
        } for r in reviews]
    }

@app.post("/{review_id}/vote")
def vote_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.helpful_votes += 1
    db.commit()
    return {"review_id": review.id, "helpful_votes": review.helpful_votes}
