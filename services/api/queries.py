"""Warehouse-only analytics queries.

Every dashboard metric is aggregated in PostgreSQL against dbt marts. This keeps
the API contract aligned with the modeled warehouse and avoids N+1 application work.
"""

from datetime import date
from typing import Any

from psycopg import Connection

from services.observability.metrics import track_database_query


@track_database_query("overview")
def fetch_overview(connection: Connection[Any]) -> dict[str, Any]:
    row = connection.execute(
        """
        select
            coalesce((select sum(amount) from analytics.fct_payments
                where payment_status = 'completed'), 0)::double precision as completed_revenue,
            coalesce((select sum(order_total) from analytics.fct_orders), 0)::double precision
                as gross_order_value,
            (select count(*) from analytics.fct_orders)::int as total_orders,
            (select count(*) from analytics.fct_payments
                where payment_status = 'completed')::int as completed_payments,
            (select count(*) from analytics.fct_payments
                where payment_status = 'failed')::int as failed_payments,
            (select avg(order_total) from analytics.fct_orders)::double precision
                as average_order_value,
            (select count(*) from analytics.dim_customers)::int as total_customers,
            (select count(*) from analytics.dim_products)::int as total_products,
            (select count(*) from analytics.fct_orders
                where shipment_status = 'delivered')::int as delivered_shipments,
            (select count(*) from analytics.fct_orders
                where shipment_status is not null)::int as total_shipments
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("Warehouse overview query returned no row")
    return dict(row)


@track_database_query("orders")
def fetch_orders(
    connection: Connection[Any], start_date: date | None, end_date: date | None, limit: int
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        select
            order_created_at::date as order_date,
            count(*)::int as order_count,
            coalesce(sum(order_total), 0)::double precision as gross_order_value,
            coalesce(sum(completed_payment_amount), 0)::double precision as completed_revenue
        from analytics.fct_orders
        where (%s::date is null or order_created_at::date >= %s::date)
          and (%s::date is null or order_created_at::date <= %s::date)
        group by order_created_at::date
        order by order_date
        limit %s
        """,
        (start_date, start_date, end_date, end_date, limit),
    ).fetchall()
    return [dict(row) for row in rows]


@track_database_query("products")
def fetch_products(connection: Connection[Any], limit: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        select product_id, product_name, category, units_ordered,
               gross_ordered_amount::double precision
        from analytics.dim_products
        order by gross_ordered_amount desc, product_name
        limit %s
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


@track_database_query("customers")
def fetch_customers(connection: Connection[Any], limit: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        select
            customer_id,
            email,
            concat_ws(' ', first_name, last_name) as customer_name,
            order_count,
            lifetime_completed_payment_amount::double precision,
            case when order_count > 0
                then lifetime_completed_payment_amount / order_count
                else null
            end::double precision as average_order_value,
            most_recent_order_at
        from analytics.dim_customers
        order by lifetime_completed_payment_amount desc, customer_name
        limit %s
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


@track_database_query("payments")
def fetch_payment_statuses(connection: Connection[Any]) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        select payment_status, count(*)::int as payment_count,
               coalesce(sum(amount), 0)::double precision as total_amount
        from analytics.fct_payments
        group by payment_status
        order by payment_status
        """
    ).fetchall()
    return [dict(row) for row in rows]


@track_database_query("shipments")
def fetch_shipment_statuses(connection: Connection[Any]) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        select coalesce(shipment_status, 'not_shipped') as shipment_status,
               count(*)::int as shipment_count
        from analytics.fct_orders
        group by coalesce(shipment_status, 'not_shipped')
        order by shipment_status
        """
    ).fetchall()
    return [dict(row) for row in rows]
