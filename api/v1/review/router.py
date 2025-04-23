# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List

# from core.deps import get_db
# from .domain import ReviewDomain
# from .schema import AIReviewCreate, AIReviewUpdate, AIReviewOut

# router = APIRouter(prefix="/reviews", tags=["reviews"])

# @router.post("/", response_model=AIReviewOut, status_code=status.HTTP_201_CREATED)
# async def create_review(review_data: AIReviewCreate, db: AsyncSession = Depends(get_db)):
#     """
#     Create a new AI review for a submission.
#     """
#     review_domain = ReviewDomain(db)
#     return await review_domain.create_review(review_data)

# @router.get("/{review_id}", response_model=AIReviewOut)
# async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Get a review by ID.
#     """
#     review_domain = ReviewDomain(db)
#     return await review_domain.get_review(review_id)

# @router.get("/submission/{submission_id}", response_model=List[AIReviewOut])
# async def get_reviews_by_submission(submission_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Get all reviews for a submission.
#     """
#     review_domain = ReviewDomain(db)
#     return await review_domain.get_reviews_by_submission(submission_id)

# @router.put("/{review_id}", response_model=AIReviewOut)
# async def update_review(review_id: int, review_update: AIReviewUpdate, db: AsyncSession = Depends(get_db)):
#     """
#     Update an existing review.
#     """
#     review_domain = ReviewDomain(db)
#     return await review_domain.update_review(review_id, review_update)

# @router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_review(review_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Delete a review.
#     """
#     review_domain = ReviewDomain(db)
#     await review_domain.delete_review(review_id)
#     return {"detail": "Review deleted successfully"}

# @router.post("/generate/{submission_id}", response_model=AIReviewOut)
# async def generate_review(submission_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Generate an AI code review for a submission using Gemini.
#     """
#     review_domain = ReviewDomain(db)
#     return await review_domain.generate_review(submission_id)
