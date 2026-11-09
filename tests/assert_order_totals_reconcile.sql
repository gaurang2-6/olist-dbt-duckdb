-- Payments should cover items + freight for delivered orders. A handful of raw orders don't
-- reconcile (vouchers, rounding), so this warns above 1 BRL and only fails if it spreads.
{{ config(severity = 'error', error_if = '>500', warn_if = '>0') }}

select order_id, order_value, amount_paid
from {{ ref('fct_orders') }}
where status = 'delivered'
  and abs(order_value - coalesce(amount_paid, 0)) > 1
