from typing import List

from sqlalchemy import ForeignKey, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from employment_flask_app import db


class EmploymentData(db.Model):
    __tablename__ = "employment_data"
    DataID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    RegionName: Mapped[str] = mapped_column(String(50), nullable=False)
    Year: Mapped[int] = mapped_column(Integer, nullable=False)
    Gender: Mapped[str] = mapped_column(String(50), nullable=False)
    OccupationType: Mapped[str] = mapped_column(String(50), nullable=False)
    EmploymentPercentage: Mapped[float] = mapped_column(Float, nullable=False)
    MarginofErrorPercentage: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    Longitude: Mapped[float] = mapped_column(Float, nullable=False)
    Latitude: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('RegionName', 'Year', 'Gender', 'OccupationType',
                         'EmploymentPercentage', 'MarginofErrorPercentage',
                         'Longitude', 'Latitude',
                         name='unique_employment_data'),
    )

    def to_array(self):
        return [
            self.RegionName,
            self.Year,
            self.Gender,
            self.OccupationType,
            self.EmploymentPercentage,
            self.MarginofErrorPercentage,
            self.Longitude,
            self.Latitude
        ]

    def to_dict(self):
        return {
            self.RegionName,
            self.Year,
            self.Gender,
            self.OccupationType,
            self.EmploymentPercentage,
            self.MarginofErrorPercentage,
            self.Longitude,
            self.Latitude
        }


class PolicyRecommendation(db.Model):
    __tablename__ = "policy_recommendation"
    PolicyID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    EmploymentDisparity: Mapped[str] = mapped_column(
        String(300), nullable=False
    )
    PolicyName: Mapped[str] = mapped_column(String(50), nullable=False)
    PolicyDescription: Mapped[str] = mapped_column(String(300), nullable=False)
    PolicyFeedback: Mapped[List['PolicyFeedback']] = relationship(
        "PolicyFeedback", back_populates='PolicyRecommendation'
    )

    __table_args__ = (
        UniqueConstraint('EmploymentDisparity', 'PolicyName',
                         'PolicyDescription',
                         name='unique_policy_recommendation'),
    )

    def to_array(self):
        return {
            "PolicyID": self.PolicyID,
            "PolicyName": self.PolicyName,
            "PolicyDescription": self.PolicyDescription,
            "EmploymentDisparity": self.EmploymentDisparity,
            "PolicyFeedback": [
                feedback.to_array() for feedback in self.PolicyFeedback
            ]
        }


class PolicyFeedback(db.Model):
    __tablename__ = "policy_feedback"
    FeedbackID: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    PolicyID: Mapped[int] = mapped_column(
        ForeignKey('policy_recommendation.PolicyID')
    )
    PolicyRating: Mapped[int] = mapped_column(Integer, nullable=False)
    PolicyFeedback: Mapped[str] = mapped_column(String(300), nullable=False)
    PolicyRecommendation: Mapped["PolicyRecommendation"] = relationship(
        "PolicyRecommendation", back_populates='PolicyFeedback'
    )

    __table_args__ = (
        UniqueConstraint('PolicyRating', 'PolicyFeedback',
                         name='unique_policy_feedback'),
    )

    def to_array(self):
        return {
            "FeedbackID": self.FeedbackID,
            "PolicyID": self.PolicyID,
            "PolicyRating": self.PolicyRating,
            "PolicyFeedback": self.PolicyFeedback
        }
