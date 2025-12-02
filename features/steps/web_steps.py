######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
######################################################################

# flake8: noqa
# pylint: disable=function-redefined, missing-function-docstring

"""
Web Steps for ShopCarts Admin UI
"""

import re
from typing import Any

from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = ""  # we use field names directly as element ids

# Mapping from human-friendly button names in the feature file
# to actual HTML button IDs in admin.html
BUTTON_MAP = {
    "Create Shopcart": "create-cart-btn",
    "Retrieve Shopcart": "retrieve-cart-btn",
    "Update Shopcart": "update-cart-btn",
    "Delete Shopcart": "delete-cart-btn",
    "List Shopcarts": "search-carts-btn",
    "Search Shopcarts": "search-carts-btn",
    "Clear Cart Items": "clear-cart-btn",
    "Clear Cart Form": "clear-cart-form-btn",
    "Create Item": "create-item-btn",
    "Retrieve Item": "retrieve-item-btn",
    "Update Item": "update-item-btn",
    "Delete Item": "delete-item-btn",
    "List Items": "list-items-btn",
    "Clear Item Form": "clear-item-form-btn",
}


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging"""
    filename = re.sub(r"[^\w\s]", "", filename)
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


# -------------------- NAVIGATION --------------------


@when('I visit the "Admin Page"')
def step_impl(context: Any) -> None:
    """Open the admin UI"""
    context.driver.get(f"{context.base_url}/admin")


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


# -------------------- FORM FIELDS --------------------


def field_id(name: str) -> str:
    """Convert a human field name into an HTML id"""
    return ID_PREFIX + name.lower().replace(" ", "_")


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = field_id(element_name)
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = field_id(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I clear the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = field_id(element_name)
    element = context.driver.find_element(By.ID, element_id)
    element.clear()


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = field_id(element_name)
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('the "{element_name}" field should not be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = field_id(element_name)
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") != ""


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = field_id(element_name)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


# -------------------- COPY / PASTE --------------------


@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = field_id(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value").strip()


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = field_id(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


# -------------------- BUTTONS --------------------


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = BUTTON_MAP.get(button)
    assert button_id, f"Unknown button label in feature file: {button}"
    context.driver.find_element(By.ID, button_id).click()


# -------------------- FLASH MESSAGE --------------------


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


# -------------------- RESULTS TABLES --------------------


@then('I should see "{text}" in the shopcarts results')
def step_impl(context: Any, text: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "shopcarts_results"), text
        )
    )
    assert found


@then('I should not see "{text}" in the shopcarts results')
def step_impl(context: Any, text: str) -> None:
    element = context.driver.find_element(By.ID, "shopcarts_results")
    assert text not in element.text


@then('I should see "{text}" in the items results')
def step_impl(context: Any, text: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "items_results"), text
        )
    )
    assert found


@then('I should not see "{text}" in the items results')
def step_impl(context: Any, text: str) -> None:
    element = context.driver.find_element(By.ID, "items_results")
    assert text not in element.text


@when('I click the "{tab_name}" tab')
def step_impl(context, tab_name):
    tab_id_map = {"Shopcarts": "tab-shopcarts", "Items": "tab-items"}
    selector = f'a[href="#{tab_id_map[tab_name]}"]'
    element = context.driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
