export interface Overview {
  completed_revenue: number;
  gross_order_value: number;
  total_orders: number;
  completed_payments: number;
  failed_payments: number;
  average_order_value: number | null;
  total_customers: number;
  total_products: number;
  delivered_shipments: number;
  total_shipments: number;
}

export interface OrderPoint {
  order_date: string;
  order_count: number;
  gross_order_value: number;
  completed_revenue: number;
}

export interface Product {
  product_id: string;
  product_name: string;
  category: string;
  units_ordered: number;
  gross_ordered_amount: number;
}

export interface Customer {
  customer_id: string;
  email: string;
  customer_name: string;
  order_count: number;
  lifetime_completed_payment_amount: number;
  average_order_value: number | null;
  most_recent_order_at: string | null;
}

export interface PaymentStatus {
  payment_status: string;
  payment_count: number;
  total_amount: number;
}

export interface ShipmentStatus {
  shipment_status: string;
  shipment_count: number;
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`);
  if (!response.ok) throw new Error(`Analytics API returned ${response.status}`);
  return response.json() as Promise<T>;
}

export const analyticsApi = {
  overview: () => get<Overview>("/api/v1/analytics/overview"),
  orders: () => get<OrderPoint[]>("/api/v1/analytics/orders?limit=90"),
  products: () => get<Product[]>("/api/v1/analytics/products?limit=8"),
  customers: () => get<Customer[]>("/api/v1/analytics/customers?limit=8"),
  payments: () => get<PaymentStatus[]>("/api/v1/analytics/payments"),
  shipments: () => get<ShipmentStatus[]>("/api/v1/analytics/shipments"),
};
