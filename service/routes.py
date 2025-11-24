######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
ShopCart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete ShopCart
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import jsonify, request, abort, render_template
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Namespace, Resource, fields
from service.models import ShopCarts, Items
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="ShopCarts Demo REST API Service",
            version="1.0",
            # The host application owns misc routes like `/`, `/admin`, `/health`,
            # while the Flask-RESTX Api manages the REST resources under `/api/shopcarts`.
            paths="/api/shopcarts",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# ADMIN UI
######################################################################
@app.route("/admin", methods=["GET"])
def admin_ui():
    """Serve the single-page admin UI"""
    return render_template("admin.html")


############################################################
# Health Endpoint
############################################################
@app.route("/health", methods=["GET"])
def health():
    """Health status used by Kubernetes probes"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# Configure Swagger / Flask-RESTX
#
# NOTE:
#   - The plain Flask routes above (`/`, `/admin`, `/health`) belong to
#     the host application and are not part of the REST API surface.
#   - The Flask-RESTX `Api` and namespaces below define the REST
#     resources (e.g., `/api/shopcarts`) under the `/api` prefix and
#     should not register misc/host routes to avoid collisions with the
#     root URL.
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="ShopCarts REST API Service",
    description="ShopCarts service with Swagger (Flask-RESTX)",
    doc="/apidocs",
    prefix="/api",
)

# Namespaces
shopcarts_ns = Namespace("shopcarts", path="/shopcarts")
api.add_namespace(shopcarts_ns)


######################################################################
#  S W A G G E R   D A T A   M O D E L S
######################################################################

# Define the model so that the docs reflect what can be sent
shopcart_create_model = shopcarts_ns.model(
    "ShopcartCreate",
    {
        "customer_id": fields.Integer(
            required=True, description="The customer identifier"
        ),
    },
)

shopcart_model = shopcarts_ns.inherit(
    "Shopcart",
    shopcart_create_model,
    {
        "shopcart_id": fields.Integer(
            readOnly=True,
            description="The unique identifier assigned internally by service",
        ),
    },
)

# Item Models
item_create_model = shopcarts_ns.model(
    "ItemCreate",
    {
        "product_id": fields.Integer(
            required=True, description="The product identifier"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the product", min=1
        ),
        "price": fields.Float(
            required=True, description="The total price for this item"
        ),
    },
)

item_model = shopcarts_ns.model(
    "Item",
    {
        "item_id": fields.Integer(
            readOnly=True,
            description="The unique identifier assigned internally by service",
        ),
        "shopcart_id": fields.Integer(
            readOnly=True, description="The shopcart identifier this item belongs to"
        ),
        "product_id": fields.Integer(
            required=True, description="The product identifier"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the product", min=1
        ),
        "price": fields.String(
            readOnly=True, description="The total price for this item (as string)"
        ),
    },
)

item_update_model = shopcarts_ns.model(
    "ItemUpdate",
    {
        "quantity": fields.Integer(
            required=True, description="The new quantity for the item", min=1
        ),
        "unit_price": fields.Float(
            required=False,
            description="Unit price (optional, used to recalculate total price)",
        ),
    },
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@shopcarts_ns.route("")
class ShopcartCollectionResources(Resource):
    """Handles interactions with the ShopCarts collection"""

    @shopcarts_ns.doc("list_shopcarts")
    @shopcarts_ns.marshal_list_with(shopcart_model)
    def get(self):
        """Returns filtered list of Shopcarts"""
        app.logger.info("Request for shopcart list")

        customer_id = request.args.get("customer_id", type=int)

        if customer_id is not None:
            app.logger.info("Filtering shopcarts by customer_id=%s", customer_id)
            shopcarts = ShopCarts.find_by_customer_id(customer_id).all()
        else:
            shopcarts = ShopCarts.all()

        results = [sc.serialize() for sc in shopcarts]
        return results, status.HTTP_200_OK

    ######################################################################
    # CREATE A SHOPCART
    ######################################################################
    @shopcarts_ns.doc("create_shopcart")
    @shopcarts_ns.response(400, "The posted data was not valid")
    @shopcarts_ns.expect(shopcart_create_model, validate=False)
    @shopcarts_ns.marshal_with(shopcart_model, code=status.HTTP_201_CREATED)
    def post(self):
        """
        Create a ShopCart
        This endpoint will create a ShopCart based the data in the body that is posted
        """
        app.logger.info("Request to Create a ShopCart...")
        check_content_type("application/json")

        shopcart = ShopCarts()
        # Get the data from the request and deserialize it
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        shopcart.deserialize(data)

        if ShopCarts.find_by_customer_id(shopcart.customer_id).first():
            abort(
                status.HTTP_409_CONFLICT,
                f"Shopcart with customer_id '{shopcart.customer_id}' already exists.",
            )

        # Save the new ShopCart to the database
        shopcart.create()
        app.logger.info("ShopCart with new id [%s] saved!", shopcart.shopcart_id)

        # Return the location of the new ShopCart
        location_url = api.url_for(
            ShopcartResource, shopcart_id=shopcart.shopcart_id, _external=True
        )

        return (
            shopcart.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
# READ A SHOPCART
######################################################################
@shopcarts_ns.route("/<int:shopcart_id>")
@shopcarts_ns.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """Handles a single ShopCart resource"""

    @shopcarts_ns.doc("get_shopcart")
    @shopcarts_ns.response(404, "Shopcart not found")
    @shopcarts_ns.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart

        This endpoint will return a Shopcart based on it's id
        """
        app.logger.info("Request to Retrieve a shopcart with id [%s]", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        app.logger.info("Returning shopcart: %s", shopcart.shopcart_id)
        return shopcart.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING SHOPCART
    ######################################################################
    @shopcarts_ns.doc("update_shopcart")
    @shopcarts_ns.response(404, "Shopcart not found")
    @shopcarts_ns.response(400, "The posted Shopcart data was not valid")
    @shopcarts_ns.expect(shopcart_create_model, validate=False)
    @shopcarts_ns.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update a Shopcart based the body that is posted
        """
        app.logger.info("Request to Update a shopcart with id [%s]", shopcart_id)
        check_content_type("application/json")

        # Attempt to find the Shopcart and abort if not found
        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Parse the incoming payload
        data = request.get_json()
        app.logger.info("Processing: %s", data)

        # Detect customer_id conflicts before mutating the current record.
        # This avoids triggering a database-level unique constraint violation
        # when SQLAlchemy flushes pending changes.
        new_customer_id = data.get("customer_id", shopcart.customer_id)
        conflict = (
            ShopCarts.find_by_customer_id(new_customer_id)
            .filter(ShopCarts.shopcart_id != shopcart_id)
            .first()
        )
        if conflict:
            abort(
                status.HTTP_409_CONFLICT,
                f"Shopcart with customer_id '{new_customer_id}' already exists.",
            )

        # No conflict: safely apply the update
        shopcart.deserialize(data)

        # Save the updates to the database
        shopcart.update()

        app.logger.info("Shopcart with ID: %d updated.", shopcart.shopcart_id)
        return shopcart.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A SHOPCART
    ######################################################################
    @shopcarts_ns.doc("delete_shopcart")
    @shopcarts_ns.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a ShopCart

        This endpoint will delete a ShopCart based the id specified in the path
        """
        app.logger.info("Request to Delete a shopcart with id [%s]", shopcart_id)

        # Delete the ShopCart if it exists
        shopcart = ShopCarts.find(shopcart_id)
        if shopcart:
            app.logger.info("ShopCart with ID: %d found.", shopcart.shopcart_id)
            shopcart.delete()

        app.logger.info("ShopCart with ID: %d delete complete.", shopcart_id)
        return {}, status.HTTP_204_NO_CONTENT


def check_content_type(content_type) -> None:
    """Checks that media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


def validate_item_data(data):
    """Validate and return sanitized quantity and unit_price"""
    if data is None:
        abort(status.HTTP_400_BAD_REQUEST, "Request body must be valid JSON.")

    if "quantity" not in data:
        abort(status.HTTP_400_BAD_REQUEST, "Field 'quantity' is required.")

    try:
        quantity = int(data["quantity"])
    except (TypeError, ValueError):
        abort(status.HTTP_400_BAD_REQUEST, "Quantity must be an integer.")

    if quantity < 1:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid quantity: must be at least 1.")

    unit_price = None
    if "unit_price" in data and data["unit_price"] is not None:
        try:
            unit_price = Decimal(str(data["unit_price"]))
        except (InvalidOperation, ValueError) as error:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid unit_price value: {error}")

    return quantity, unit_price


def compute_new_price(item, quantity, unit_price):
    """Compute updated total price for item"""
    # Infer price if not given
    if unit_price is None:
        unit_price = item.price / item.quantity

    if unit_price < 0:
        abort(status.HTTP_400_BAD_REQUEST, "unit_price must not be negative.")

    return (unit_price * Decimal(quantity)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


######################################################################
# READ/UPDATE/DELETE AN ITEM
######################################################################
@shopcarts_ns.route("/<int:shopcart_id>/items/<int:item_id>")
@shopcarts_ns.param("shopcart_id", "The Shopcart identifier")
@shopcarts_ns.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """Retrieve/Update/Delete a single Item in a ShopCart"""

    @shopcarts_ns.doc("get_item")
    @shopcarts_ns.response(404, "Shopcart or Item not found")
    @shopcarts_ns.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """Retrieve the details for an item in a shopcart"""
        app.logger.info(
            "Request to retrieve item [%s] from shopcart [%s]", item_id, shopcart_id
        )

        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Find first item with item_id. None if not exists.
        item = next((itm for itm in shopcart.items if itm.item_id == item_id), None)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
            )

        result = item.serialize()
        result["price"] = str(result["price"])
        app.logger.info("Returning item [%s] from shopcart [%s]", item_id, shopcart_id)
        return result, status.HTTP_200_OK

    @shopcarts_ns.doc("update_item")
    @shopcarts_ns.response(404, "Shopcart or Item not found")
    @shopcarts_ns.response(400, "The posted Item data was not valid")
    @shopcarts_ns.expect(item_update_model, validate=False)
    @shopcarts_ns.marshal_with(item_model)
    def put(self, shopcart_id, item_id):
        """Update the quantity or price for an item in a shopcart"""
        app.logger.info(
            "Request to update item [%s] in shopcart [%s]", item_id, shopcart_id
        )
        check_content_type("application/json")

        # Attempt to find the ShopCart and abort if not found
        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Attempt to find the Item within this shopcart and abort if not found
        item = next((itm for itm in shopcart.items if itm.item_id == item_id), None)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
            )

        # Update the Item with the new data
        # Use silent=True so invalid JSON yields None, allowing
        # validate_item_data to emit a consistent 400 error.
        data = request.get_json(silent=True)
        new_quantity, unit_price = validate_item_data(data)
        new_price = compute_new_price(item, new_quantity, unit_price)

        item.quantity = new_quantity
        item.price = new_price
        shopcart.update()

        response = item.serialize()
        response["price"] = str(response["price"])
        app.logger.info(
            "Item [%s] in shopcart [%s] updated to quantity=%s price=%s",
            item_id,
            shopcart_id,
            new_quantity,
            new_price,
        )
        return response, status.HTTP_200_OK

    @shopcarts_ns.doc("delete_item")
    @shopcarts_ns.response(204, "Item deleted")
    @shopcarts_ns.response(404, "Shopcart or Item not found")
    def delete(self, shopcart_id, item_id):
        """
        Delete an Item from a ShopCart

        This endpoint will delete an Item based on the shopcart_id and item_id
        specified in the path.
        """
        app.logger.info(
            "Request to delete item [%s] from shopcart [%s]", item_id, shopcart_id
        )

        # Verify the shopcart exists
        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Find the item within that shopcart
        item = next((itm for itm in shopcart.items if itm.item_id == item_id), None)
        if item:
            app.logger.info(
                "Item [%s] found in shopcart [%s]. Proceeding with delete.",
                item_id,
                shopcart_id,
            )
            item.delete()
            app.logger.info(
                "Item [%s] successfully deleted from shopcart [%s].",
                item_id,
                shopcart_id,
            )
        else:
            app.logger.warning(
                "Item [%s] not found in shopcart [%s]. Nothing to delete.",
                item_id,
                shopcart_id,
            )

        return {}, status.HTTP_204_NO_CONTENT


######################################################################
# CLEAR SHOP CART
######################################################################
@shopcarts_ns.route("/<int:shopcart_id>/clear")
@shopcarts_ns.param("shopcart_id", "The Shopcart identifier")
class ShopcartClear(Resource):
    """Clear all items from a ShopCart (idempotent)"""

    @shopcarts_ns.doc("clear_shopcart")
    @shopcarts_ns.response(404, "Shopcart not found")
    @shopcarts_ns.marshal_with(shopcart_model)
    def post(self, shopcart_id: int):
        """POST /api/shopcarts/<id>/clear — remove all items from a cart (idempotent)."""
        app.logger.info("Request to clear shopcart id=%s", shopcart_id)

        cart = ShopCarts.find(shopcart_id)
        if cart is None:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Remove all items; cascade will delete-orphan on commit
        if cart.items:
            cart.items.clear()

        # Persist (also updates updated_at per model.update())
        cart.update()

        # Return the canonical representation used by GET /shopcarts/<id>
        return cart.serialize(), status.HTTP_200_OK


######################################################################
# LIST AN ITEM
######################################################################
@shopcarts_ns.route("/<int:shopcart_id>/items")
@shopcarts_ns.param("shopcart_id", "The Shopcart identifier")
class ItemsCollection(Resource):
    """List and Create Items within a ShopCart"""

    @shopcarts_ns.doc("list_items")
    @shopcarts_ns.response(404, "Shopcart not found")
    @shopcarts_ns.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """List all items in a shopcart"""
        app.logger.info("Request to list items for shopcart [%s]", shopcart_id)

        shopcart = ShopCarts.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Let the model handle serialization
        results = [item.serialize() for item in shopcart.items]
        for item in results:
            item["price"] = str(item["price"])

        app.logger.info(
            "Returning %d items for shopcart [%s]", len(results), shopcart_id
        )
        return results, status.HTTP_200_OK

    ######################################################################
    # CREATE AN ITEM
    ######################################################################
    @shopcarts_ns.doc("create_item")
    @shopcarts_ns.response(404, "Shopcart not found")
    @shopcarts_ns.response(400, "The posted data was not valid")
    @shopcarts_ns.expect(item_create_model, validate=False)
    @shopcarts_ns.marshal_with(item_model, code=status.HTTP_201_CREATED)
    def post(self, shopcart_id):
        """Create an Item inside a ShopCart"""
        app.logger.info("Request to Create an Item inside a ShopCart...")
        check_content_type("application/json")

        item = Items()
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        item.deserialize(data)
        item.shopcart_id = shopcart_id
        # Save the new ShopCart to the database
        item.create()
        app.logger.info("ShopCart Item with new id [%s] saved!", item.item_id)

        location_url = api.url_for(
            ItemResource,
            shopcart_id=shopcart_id,
            item_id=item.item_id,
            _external=True,
        )

        return (
            {**item.serialize(), "price": str(item.price)},
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )
