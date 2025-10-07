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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import ShopCarts
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
            # TODO: Uncomment this code when list_shopcarts is implemented
            # paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Todo: Place your REST API code here ...
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Create a ShopCart
    This endpoint will create a ShopCart based the data in the body that is posted
    """
    app.logger.info("Request to Create a ShopCart...")
    # check_content_type("application/json")

    shopcart = ShopCarts()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)

    # Save the new ShopCart to the database
    shopcart.create()
    app.logger.info("ShopCart with new id [%s] saved!", shopcart.shopcart_id)

    # Return the location of the new ShopCart
    # location_url = url_for(
    # "get_shopcarts", shopcart_id=shopcart.shopcart_id, _external=True
    # )
    # adjust later
    location_url = f"/shopcarts/{shopcart.shopcart_id}"

    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )
