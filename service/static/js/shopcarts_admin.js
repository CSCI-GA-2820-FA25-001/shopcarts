$(function () {
  function flash(message) {
    $("#flash_message").empty().text(message || "");
  }

  function update_cart_form(res) {
    if (!res) return;
    $("#shopcart_id").val(res.shopcart_id || "");
    $("#customer_id").val(res.customer_id || "");
  }

  function clear_cart_form() {
    $("#shopcart_id").val("");
    $("#customer_id").val("");
  }

  function update_item_form(res) {
    if (!res) return;
    $("#item_id").val(res.item_id || "");
    $("#product_id").val(res.product_id || "");
    $("#quantity").val(res.quantity || "");
  }

  function clear_item_form() {
    $("#item_id").val("");
    $("#product_id").val("");
    $("#quantity").val("");
    $("#unit_price").val("");
  }

  $("#create-cart-btn").click(function () {
    const customer_id = parseInt($("#customer_id").val());
    $("#flash_message").empty();

    $.ajax({
      type: "POST",
      url: "/shopcarts",
      contentType: "application/json",
      data: JSON.stringify({ customer_id: customer_id })
    })
      .done(function (res) {
        update_cart_form(res);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Create failed");
      });
  });

  $("#retrieve-cart-btn").click(function () {
    const id = $("#shopcart_id").val();
    $("#flash_message").empty();

    $.ajax({ type: "GET", url: `/shopcarts/${id}` })
      .done(function (res) {
        update_cart_form(res);
        flash("Success");
      })
      .fail(function (res) {
        clear_cart_form();
        flash((res.responseJSON && res.responseJSON.message) || "Not found");
      });
  });

  $("#update-cart-btn").click(function () {
    const id = $("#shopcart_id").val();
    const customer_id = parseInt($("#customer_id").val());
    $("#flash_message").empty();

    $.ajax({
      type: "PUT",
      url: `/shopcarts/${id}`,
      contentType: "application/json",
      data: JSON.stringify({ customer_id: customer_id })
    })
      .done(function (res) {
        update_cart_form(res);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Update failed");
      });
  });

  $("#delete-cart-btn").click(function () {
    const id = $("#shopcart_id").val();
    $("#flash_message").empty();

    if (!id) return;
    $.ajax({ type: "DELETE", url: `/shopcarts/${id}` })
      .done(function () {
        clear_cart_form();
        flash("Success");
      })
      .fail(function () {
        flash("Server error");
      });
  });

  $("#search-carts-btn").click(function () {
    const customer_id = $("#customer_id").val();
    let qs = "";
    if (customer_id) qs = `customer_id=${customer_id}`;
    $("#flash_message").empty();

    $.ajax({ type: "GET", url: `/shopcarts?${qs}` })
      .done(function (res) {
        $("#shopcarts_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-2">Shopcart ID</th>';
        table += '<th class="col-md-2">Customer ID</th>';
        table += '</tr></thead><tbody>';
        for (let i = 0; i < res.length; i++) {
          let sc = res[i];
          table += `<tr id="row_${i}"><td>${sc.shopcart_id}</td><td>${sc.customer_id}</td></tr>`;
        }
        table += '</tbody></table>';
        $("#shopcarts_results").append(table);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Search failed");
      });
  });

  $("#clear-cart-btn").click(function () {
    const id = $("#shopcart_id").val();
    $("#flash_message").empty();
    if (!id) return;
    $.ajax({ type: "POST", url: `/shopcarts/${id}/clear` })
      .done(function (res) {
        update_cart_form(res);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Clear failed");
      });
  });

  function getItemCartId() {
    return $("#item_shopcart_id").val() || $("#shopcart_id").val();
  }

  $("#create-item-btn").click(function () {
    const sid = getItemCartId();
    const product_id = parseInt($("#product_id").val());
    const quantity = parseInt($("#quantity").val());
    const unit_price = parseFloat($("#unit_price").val());
    const price = isNaN(unit_price) || isNaN(quantity) ? null : (unit_price * quantity).toFixed(2);

    $("#flash_message").empty();
    $.ajax({
      type: "POST",
      url: `/shopcarts/${sid}/items`,
      contentType: "application/json",
      data: JSON.stringify({ product_id, quantity, price })
    })
      .done(function (res) {
        update_item_form(res);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Create item failed");
      });
  });

  $("#retrieve-item-btn").click(function () {
    const sid = getItemCartId();
    const item_id = $("#item_id").val();
    $("#flash_message").empty();
    $.ajax({ type: "GET", url: `/shopcarts/${sid}/items/${item_id}` })
      .done(function (res) {
        update_item_form(res);
        flash("Success");
      })
      .fail(function (res) {
        clear_item_form();
        flash((res.responseJSON && res.responseJSON.message) || "Item not found");
      });
  });

  $("#update-item-btn").click(function () {
    const sid = getItemCartId();
    const item_id = $("#item_id").val();
    const quantity = parseInt($("#quantity").val());
    const unit_price = parseFloat($("#unit_price").val());
    $("#flash_message").empty();
    $.ajax({
      type: "PUT",
      url: `/shopcarts/${sid}/items/${item_id}`,
      contentType: "application/json",
      data: JSON.stringify({ quantity, unit_price })
    })
      .done(function (res) {
        update_item_form(res);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "Update item failed");
      });
  });

  $("#delete-item-btn").click(function () {
    const sid = getItemCartId();
    const item_id = $("#item_id").val();
    $("#flash_message").empty();
    if (!sid || !item_id) return;
    $.ajax({ type: "DELETE", url: `/shopcarts/${sid}/items/${item_id}` })
      .done(function () {
        clear_item_form();
        flash("Success");
      })
      .fail(function () {
        flash("Server error");
      });
  });

  $("#list-items-btn").click(function () {
    const sid = getItemCartId();
    $("#flash_message").empty();
    $.ajax({ type: "GET", url: `/shopcarts/${sid}/items` })
      .done(function (res) {
        $("#items_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-2">Item ID</th>';
        table += '<th class="col-md-2">Product ID</th>';
        table += '<th class="col-md-2">Quantity</th>';
        table += '<th class="col-md-2">Price</th>';
        table += '</tr></thead><tbody>';
        for (let i = 0; i < res.length; i++) {
          const it = res[i];
          table += `<tr id="item_row_${i}"><td>${it.item_id}</td><td>${it.product_id}</td><td>${it.quantity}</td><td>${it.price}</td></tr>`;
        }
        table += '</tbody></table>';
        $("#items_results").append(table);
        flash("Success");
      })
      .fail(function (res) {
        flash((res.responseJSON && res.responseJSON.message) || "List items failed");
      });
  });
});
