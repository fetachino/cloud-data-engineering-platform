# Warehouse Model

Milestone 2 adds an analytics schema built by dbt in PostgreSQL. Operational tables remain the source of truth and are not replaced.

## Layers

- Sources: normalized operational tables in `public`, populated by the Kafka ingestion consumer.
- Staging: `stg_*` models that rename fields and standardize analytics-friendly column names.
- Intermediate: focused rollups for order items and payment state.
- Marts: dimensional and fact models in the `analytics` schema.

## Keys

The marts preserve operational UUIDs as natural keys because Milestone 1 already creates durable event-derived identifiers. Additional surrogate keys are not introduced until there is a concrete cross-source integration need.

## Marts

- `dim_customers`
- `dim_products`
- `fct_orders`
- `fct_order_items`
- `fct_payments`

The models derive order totals, quantities, completed payment amounts, payment status, and shipment status from existing operational records. They do not fabricate customer demographics, product margins, fulfillment SLAs, or revenue fields not present in Milestone 1.
