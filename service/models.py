"""Database models for the ShopCart resource."""

import logging
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates, relationship

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def utc_now():
    """Return current time in UTC as a timezone-aware datetime"""
    return datetime.now(timezone.utc)


class DataValidationError(Exception):
    """Used for any data validation errors"""


class ShopCarts(db.Model):
    """Represents a customer's shopcart"""

    __tablename__ = "shopcarts"

    ##################################################
    # Table Schema
    ##################################################
    shopcart_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    items = relationship(
        "Items",
        back_populates="shopcart",
        cascade="all, delete-orphan",
        order_by="Items.item_id",
    )

    def __repr__(self):
        return f"<ShopCart id={self.shopcart_id} customer={self.customer_id}>"

    def create(self):
        """Persist the shopcart to the database"""
        logger.info("Creating shopcart for customer_id=%s", self.customer_id)
        # self.shopcart_id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Save updates to this shopcart"""
        logger.info("Updating shopcart id=%s", self.shopcart_id)
        self.updated_at = utc_now()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Delete this shopcart and cascade to its items"""
        logger.info("Deleting shopcart id=%s", self.shopcart_id)

        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self) -> dict:
        """Serializes a ShopCart into a dictionary"""
        return {"shopcart_id": self.shopcart_id, "customer_id": self.customer_id}

    def deserialize(self, data: dict):
        """
        Deserializes a ShopCart from a dictionary
        Args:
            data (dict): A dictionary containing the ShopCart data
        """
        try:
            self.customer_id = data["customer_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Return all shopcarts"""
        logger.info("Fetching all shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, shopcart_id):
        """Find a shopcart by shopcart id"""
        logger.info("Looking up shopcart id=%s", shopcart_id)
        return cls.query.session.get(cls, shopcart_id)


class Items(db.Model):
    """Represents an item in a shopcart"""

    __tablename__ = "items"

    ##################################################
    # Table Schema
    ##################################################
    item_id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer,
        db.ForeignKey("shopcarts.shopcart_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    shopcart = relationship("ShopCarts", back_populates="items")

    def __repr__(self):
        return (
            f"<Item id={self.item_id} product={self.product_id} "
            f"qty={self.quantity} cart={self.shopcart_id}>"
        )

    def create(self):
        """Persist the shopcart to the database"""
        logger.info("Creating shopcart item for shopcart_id=%s", self.shopcart_id)
        # self.shopcart_id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Delete this item"""
        logger.info(
            "Deleting item id=%s from shopcart_id=%s", self.item_id, self.shopcart_id
        )
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting item: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Save updates to this item"""
        logger.info("Updating item id=%s", self.item_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self) -> dict:
        """Serializes a Item into a dictionary"""
        return {
            "item_id": self.item_id,
            "shopcart_id": self.shopcart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a ShopCart from a dictionary
        Args:
            data (dict): A dictionary containing the ShopCart data
        """
        try:
            self.product_id = int(data["product_id"])
            self.quantity = int(data["quantity"])
            self.price = float(data["price"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    @validates("quantity")
    def validate_quantity(self, key, quantity):  # pylint: disable=unused-argument
        """Validate that quantity is at least 1 before saving to the database."""
        if quantity is None or int(quantity) < 1:
            raise DataValidationError("Invalid quantity: must be at least 1")
        return int(quantity)
