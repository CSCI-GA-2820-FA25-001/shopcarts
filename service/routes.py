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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
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
            paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Todo: Place your REST API code here ...


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for shopcart list")

    shopcarts = []
    # TODO: query for next hw
    shopcarts = ShopCarts.all()
    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK

######################################################################
# CREATE A SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
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

    # Save the new ShopCart to the database
    shopcart.create()
    app.logger.info("ShopCart with new id [%s] saved!", shopcart.shopcart_id)

    # Return the location of the new ShopCart
    location_url = url_for(
        "get_shopcarts", shopcart_id=shopcart.shopcart_id, _external=True
    )

    # location_url = f"/shopcarts/{shopcart.shopcart_id}"

    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
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
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to Update a shopcart with id [%s]", shopcart_id)
    check_content_type("application/json")

    # Attempt to find the Shopcart and abort if not found
    shopcart = ShopCarts.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")

    # Update the Shopcart with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)

    # Save the updates to the database
    shopcart.update()

    app.logger.info("Shopcart with ID: %d updated.", shopcart.shopcart_id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK

######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
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

######################################################################
# READ AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_shopcart_item(shopcart_id, item_id):
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
    return jsonify(result), status.HTTP_200_OK


# @app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
# def update_shopcart_item(shopcart_id, item_id):
#     """Update the quantity for an item in a shopcart"""
#     app.logger.info(
#         "Request to update item [%s] in shopcart [%s]", item_id, shopcart_id
#     )
#     check_content_type("application/json")

#     shopcart = ShopCarts.find(shopcart_id)
#     if not shopcart:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Shopcart with id '{shopcart_id}' was not found.",
#         )

#     item = next((itm for itm in shopcart.items if itm.item_id == item_id), None)
#     if not item:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
#         )

#     data = request.get_json()
#     if data is None:
#         abort(status.HTTP_400_BAD_REQUEST, "Request body must be valid JSON.")

#     if "quantity" not in data:
#         abort(status.HTTP_400_BAD_REQUEST, "Field 'quantity' is required.")

#     try:
#         new_quantity = int(data["quantity"])
#     except (TypeError, ValueError):
#         abort(status.HTTP_400_BAD_REQUEST, "Quantity must be an integer.")

#     if new_quantity < 1:
#         abort(
#             status.HTTP_400_BAD_REQUEST,
#             "Invalid quantity: must be at least 1.",
#         )

#     # Determine the unit price from the request or infer from current price
#     if "unit_price" in data and data["unit_price"] is not None:
#         try:
#             unit_price = Decimal(str(data["unit_price"]))
#         except (InvalidOperation, ValueError) as error:
#             abort(
#                 status.HTTP_400_BAD_REQUEST,
#                 f"Invalid unit_price value: {error}",
#             )
#     else:
#         # Avoid division by zero; quantity validator already prevents zero
#         unit_price = item.price / item.quantity

#     if unit_price < 0:
#         abort(
#             status.HTTP_400_BAD_REQUEST,
#             "unit_price must not be negative.",
#         )

#     # Quantize to two decimal places using bankers rounding
#     new_price = (unit_price * Decimal(new_quantity)).quantize(
#         Decimal("0.01"),
#         rounding=ROUND_HALF_UP,
#     )

#     item.quantity = new_quantity
#     item.price = new_price
#     shopcart.update()

#     updated_item = {
#         "item_id": item.item_id,
#         "shopcart_id": item.shopcart_id,
#         "product_id": item.product_id,
#         "quantity": item.quantity,
#         "price": str(item.price),
#     }
#     app.logger.info(
#         "Item [%s] in shopcart [%s] updated to quantity=%s price=%s",
#         item_id,
#         shopcart_id,
#         new_quantity,
#         new_price,
#     )
#     return jsonify(updated_item), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_shopcart_items(shopcart_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based on the body that is posted
    """
    app.logger.info("Request to Update an item with id [%s]", item_id)
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
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    item.deserialize(data)

    # Save the updates to the database
    item.update()

    app.logger.info("Item with ID: %d updated.", item.item_id)
    return jsonify(item.serialize()), status.HTTP_200_OK


# @app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
# def list_shopcart_items(shopcart_id):
#     """List all items in a shopcart"""
#     app.logger.info("Request to list items for shopcart with id [%s]", shopcart_id)

#     shopcart = ShopCarts.find(shopcart_id)
#     if not shopcart:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Shopcart with id '{shopcart_id}' was not found.",
#         )

#     items = [item.serialize() for item in shopcart.items]

#     response_items = []
#     for item in items:
#         serialized_item = dict(item)
#         serialized_item["price"] = str(serialized_item["price"])
#         response_items.append(serialized_item)

#     app.logger.info(
#         "Returning %d items for shopcart id [%s]",
#         len(response_items),
#         shopcart_id,
#     )
#     return jsonify(response_items), status.HTTP_200_OK


######################################################################
# LIST AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_shopcart_items(shopcart_id):
    """List all items in a shopcart"""
    app.logger.info("Request to list items for shopcart [%s]", shopcart_id)

    shopcart = ShopCarts.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND,
              f"Shopcart with id '{shopcart_id}' was not found.")

    # Let the model handle serialization
    results = [item.serialize() for item in shopcart.items]

    app.logger.info("Returning %d items for shopcart [%s]",
                    len(results), shopcart_id)
    return jsonify(results), status.HTTP_200_OK

######################################################################
# CREATE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_shopcarts_item(shopcart_id):
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

    location_url = url_for(
        "get_shopcart_item",
        shopcart_id=shopcart_id,
        item_id=item.item_id,
        _external=True,
    )

    return (
        jsonify(item.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_shopcart_item(shopcart_id, item_id):
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
