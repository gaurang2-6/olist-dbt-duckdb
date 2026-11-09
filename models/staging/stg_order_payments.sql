select
    order_id || '-' || payment_sequential           as payment_key,
    order_id,
    cast(payment_sequential as integer)             as payment_sequence,
    payment_type,
    cast(payment_installments as integer)           as installments,
    cast(payment_value as decimal(10, 2))           as amount
from {{ source('olist', 'order_payments') }}
