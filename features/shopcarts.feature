Feature: Manage customer shopcarts from an Admin web page
  As an eCommerce manager
  I need a simple web page to manage customer shopcarts and items
  So that I can help customers when they call support

  Scenario: The admin page is available
    When I visit the "Admin Page"
    Then I should see "ShopCarts Admin" in the title

  Scenario: Create a new shopcart (Create)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "1001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    And I should see "1001" in the "Customer ID" field
    And the "Shopcart ID" field should not be empty

  Scenario: Retrieve an existing shopcart (Read)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "2001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I clear the "Customer ID" field
    And I clear the "Shopcart ID" field
    And I paste the "Shopcart ID" field
    And I press the "Retrieve Shopcart" button
    Then I should see the message "Success"
    And I should see "2001" in the "Customer ID" field

  Scenario: Update the customer on a shopcart (Update)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "3001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I change "Customer ID" to "3002"
    And I press the "Update Shopcart" button
    Then I should see the message "Success"
    And I should see "3002" in the "Customer ID" field

  Scenario: Delete a shopcart (Delete)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "4001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Delete Shopcart" button
    Then I should see the message "Success"
    When I clear the "Customer ID" field
    And I clear the "Shopcart ID" field
    And I press the "List Shopcarts" button
    Then I should not see "4001" in the shopcarts results

  Scenario: List all shopcarts (List)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "5001"
    And I press the "Create Shopcart" button
    And I set the "Customer ID" to "5002"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I clear the "Customer ID" field
    And I press the "List Shopcarts" button
    Then I should see the message "Success"
    And I should see "5001" in the shopcarts results
    And I should see "5002" in the shopcarts results
  
  Scenario: Add a new item to a shopcart (Create)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "8001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I click the "Items" tab
    And I paste the "Item Shopcart ID" field
    And I set the "Product ID" to "111"
    And I set the "Quantity" to "3"
    And I set the "Unit Price" to "15.00"
    And I press the "Create Item" button
    Then I should see the message "Success"
    When I press the "List Items" button
    Then I should see the message "Success"
    And I should see "111" in the items results

Scenario: Retrieve items from a shopcart (Read)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "8002"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I click the "Items" tab
    And I paste the "Item Shopcart ID" field
    And I set the "Product ID" to "222"
    And I set the "Quantity" to "1"
    And I set the "Unit Price" to "20.00"
    And I press the "Create Item" button
    Then I should see the message "Success"
    When I press the "List Items" button
    Then I should see the message "Success"
    And I should see "222" in the items results

Scenario: Update an item in a shopcart (Update)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "8003"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I click the "Items" tab
    And I paste the "Item Shopcart ID" field
    And I set the "Product ID" to "333"
    And I set the "Quantity" to "1"
    And I set the "Unit Price" to "5.00"
    And I press the "Create Item" button
    Then I should see the message "Success"

    # Update item
    When I change "Quantity" to "4"
    And I press the "Update Item" button
    Then I should see the message "Success"

    # Confirm change
    When I press the "List Items" button
    Then I should see the message "Success"
    And I should see "333" in the items results

Scenario: Delete an item from a shopcart (Delete)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "8004"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I click the "Items" tab
    And I paste the "Item Shopcart ID" field
    And I set the "Product ID" to "444"
    And I set the "Quantity" to "2"
    And I set the "Unit Price" to "9.99"
    And I press the "Create Item" button
    Then I should see the message "Success"

    # Delete item
    When I press the "Delete Item" button
    Then I should see the message "Success"

    # Confirm deletion
    When I press the "List Items" button
    Then I should see the message "Success"
    And I should not see "444" in the items results
  Scenario: Find a shopcart by customer id (Query)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "6001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I clear the "Shopcart ID" field
    And I set the "Customer ID" to "6001"
    And I press the "Search Shopcarts" button
    Then I should see the message "Success"
    And I should see "6001" in the shopcarts results

    Scenario: Clear all items from a shopcart (Action)
    When I visit the "Admin Page"
    And I set the "Customer ID" to "7001"
    And I press the "Create Shopcart" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I click the "Items" tab
    And I paste the "Item Shopcart ID" field
    And I set the "Product ID" to "123"
    And I set the "Quantity" to "2"
    And I set the "Unit Price" to "10.00"
    And I press the "Create Item" button
    Then I should see the message "Success"
    When I press the "List Items" button
    Then I should see the message "Success"
    And I should see "123" in the items results


    When I click the "Shopcarts" tab
    And I press the "Clear Cart Items" button
    Then I should see the message "Success"


    When I click the "Items" tab
    And I press the "List Items" button
    Then I should see the message "Success"
    And I should not see "123" in the items results