import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const overview = {
  completed_revenue: 174.93, gross_order_value: 199.92, total_orders: 4,
  completed_payments: 3, failed_payments: 1, average_order_value: 49.98,
  total_customers: 1, total_products: 4, delivered_shipments: 2, total_shipments: 4,
};
const response = (body: unknown) => Promise.resolve({ ok: true, json: () => Promise.resolve(body) } as Response);

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn((url: string) => {
    if (url.includes("overview")) return response(overview);
    if (url.includes("orders")) return response([{ order_date: "2026-01-01", order_count: 4, gross_order_value: 199.92, completed_revenue: 174.93 }]);
    if (url.includes("products")) return response([{ product_id: "1", product_name: "Keyboard", category: "Accessories", units_ordered: 2, gross_ordered_amount: 49.98 }]);
    if (url.includes("customers")) return response([]);
    if (url.includes("payments")) return response([{ payment_status: "completed", payment_count: 3, total_amount: 174.93 }]);
    return response([{ shipment_status: "delivered", shipment_count: 2 }]);
  }));
});

describe("analytics dashboard", () => {
  it("renders KPIs and a representative product table", async () => {
    render(<App />);
    expect(await screen.findByText("Commerce intelligence")).toBeInTheDocument();
    expect(screen.getByText("$174.93")).toBeInTheDocument();
    expect(screen.getByText("Keyboard")).toBeInTheDocument();
  });

  it("renders loading state before the API resolves", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));
    render(<App />);
    expect(screen.getByText("Loading warehouse signals...")).toBeInTheDocument();
  });

  it("renders a clear API error", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("offline"))));
    render(<App />);
    expect(await screen.findByText(/analytics API could not be reached/)).toBeInTheDocument();
  });
});
