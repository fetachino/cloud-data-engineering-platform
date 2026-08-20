import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { analyticsApi, type OrderPoint, type Overview, type PaymentStatus, type Product, type ShipmentStatus } from "./api";
import "./styles.css";

interface DashboardData {
  overview: Overview;
  orders: OrderPoint[];
  products: Product[];
  payments: PaymentStatus[];
  shipments: ShipmentStatus[];
}

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const compactDate = (value: string) => new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(`${value}T00:00:00`));

function KpiCard({ label, value, detail, accent }: { label: string; value: string; detail: string; accent: string }) {
  return <article className="kpi-card" style={{ "--accent": accent } as CSSProperties}>
    <p className="eyebrow">{label}</p><strong>{value}</strong><span>{detail}</span>
  </article>;
}

function EmptyState({ label }: { label: string }) { return <div className="empty-state">No {label} available for this period.</div>; }

function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsApi.overview(), analyticsApi.orders(), analyticsApi.products(),
      analyticsApi.payments(), analyticsApi.shipments(),
    ]).then(([overview, orders, products, payments, shipments]) => {
      setData({ overview, orders, products, payments, shipments });
    }).catch(() => setError("The analytics API could not be reached. Check that the API and warehouse are running."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <main className="state-page"><div className="loader" /><p>Loading warehouse signals...</p></main>;
  if (error) return <main className="state-page error-state"><span className="status-dot" />{error}</main>;
  if (!data) return <main className="state-page">No analytics data returned.</main>;

  const { overview, orders, products, payments, shipments } = data;
  return <main className="dashboard-shell">
    <header className="topbar">
      <div className="brand-mark">CD</div>
      <div><p className="eyebrow">Cloud Data Engineering Platform</p><h1>Commerce intelligence</h1></div>
      <div className="live-status"><span className="status-dot" />Warehouse connected</div>
    </header>
    <section className="intro"><div><p className="eyebrow">Analytics workspace / hosted preview</p><h2>Make every event count.</h2><p className="intro-copy">A clear view from Kafka ingestion through dbt models to the metrics your business can act on.</p></div><div className="pipeline-note"><span>DATA FLOW</span><b>Kafka</b><i>→</i><b>PostgreSQL</b><i>→</i><b>dbt</b><i>→</i><b>API</b></div></section>
    <section className="kpi-grid" aria-label="Key performance indicators">
      <KpiCard label="Completed revenue" value={currency.format(overview.completed_revenue)} detail={`${overview.completed_payments} successful payments`} accent="#0e8077" />
      <KpiCard label="Gross order value" value={currency.format(overview.gross_order_value)} detail={`${overview.total_orders} orders captured`} accent="#de6b48" />
      <KpiCard label="Average order value" value={overview.average_order_value === null ? "—" : currency.format(overview.average_order_value)} detail="Across all orders" accent="#5871a8" />
      <KpiCard label="Customers" value={overview.total_customers.toLocaleString()} detail={`${overview.total_products} products in catalog`} accent="#b08b37" />
    </section>
    <section className="chart-grid">
      <article className="panel trend-panel"><div className="panel-heading"><div><p className="eyebrow">Order performance</p><h3>Revenue movement</h3></div><span className="legend"><i className="legend-swatch teal" />Completed revenue</span></div>{orders.length ? <ResponsiveContainer width="100%" height={260}><AreaChart data={orders}><defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0e8077" stopOpacity={0.24} /><stop offset="100%" stopColor="#0e8077" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#e8e4db" vertical={false} /><XAxis dataKey="order_date" tickFormatter={compactDate} tickLine={false} axisLine={false} /><YAxis tickFormatter={(value) => `$${value}`} tickLine={false} axisLine={false} width={55} /><Tooltip formatter={(value) => currency.format(Number(value ?? 0))} labelFormatter={(value) => compactDate(String(value))} /><Area type="monotone" dataKey="completed_revenue" stroke="#0e8077" fill="url(#revenueFill)" strokeWidth={3} /></AreaChart></ResponsiveContainer> : <EmptyState label="order trends" />}</article>
      <article className="panel status-panel"><div className="panel-heading"><div><p className="eyebrow">Payment health</p><h3>Attempt outcomes</h3></div></div>{payments.length ? <div className="status-chart"><ResponsiveContainer width="52%" height={190}><PieChart><Pie data={payments} dataKey="payment_count" nameKey="payment_status" innerRadius={55} outerRadius={82} paddingAngle={4}>{payments.map((entry) => <Cell key={entry.payment_status} fill={entry.payment_status === "completed" ? "#0e8077" : "#de6b48"} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer><div className="status-list">{payments.map((payment) => <div className="status-row" key={payment.payment_status}><span><i className={`legend-swatch ${payment.payment_status}`} />{payment.payment_status}</span><strong>{payment.payment_count}</strong></div>)}</div></div> : <EmptyState label="payment outcomes" />}</article>
    </section>
    <section className="lower-grid">
      <article className="panel product-panel"><div className="panel-heading"><div><p className="eyebrow">Product performance</p><h3>Top products by revenue</h3></div><span className="subtle">{products.length} shown</span></div>{products.length ? <div className="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Units</th><th className="number">Revenue</th></tr></thead><tbody>{products.map((product) => <tr key={product.product_id}><td><b>{product.product_name}</b><small>{product.product_id.slice(0, 8)}...</small></td><td>{product.category}</td><td>{product.units_ordered}</td><td className="number">{currency.format(product.gross_ordered_amount)}</td></tr>)}</tbody></table></div> : <EmptyState label="products" />}</article>
      <article className="panel fulfillment-panel"><div className="panel-heading"><div><p className="eyebrow">Fulfillment</p><h3>Shipment status</h3></div></div>{shipments.length ? <div className="fulfillment-list">{shipments.map((shipment) => <div className="fulfillment-row" key={shipment.shipment_status}><div><span>{shipment.shipment_status.replace("_", " ")}</span><small>{Math.round((shipment.shipment_count / overview.total_orders) * 100)}% of orders</small></div><strong>{shipment.shipment_count}</strong><div className="progress"><span style={{ width: `${(shipment.shipment_count / overview.total_orders) * 100}%` }} /></div></div>)}</div> : <EmptyState label="shipment statuses" />}</article>
    </section>
    <footer><span>Source: dbt analytics schema</span><span>Read-only synthetic analytics preview</span></footer>
  </main>;
}

export default Dashboard;
