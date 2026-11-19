export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'customer' | 'admin' | 'support_agent';
  phone?: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
    country?: string;
  };
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  discount_pct: number;
  discounted_price: number;
  stock: number;
  in_stock: boolean;
  rating: number;
  rating_count: number;
  image_url: string;
  images: string[];
  specs: Record<string, string>;
  is_featured: boolean;
}

export interface CartItem {
  cart_item_id: number;
  product_id: number;
  name: string;
  slug: string;
  category: string;
  brand: string;
  price: number;
  discount_pct: number;
  effective_price: number;
  quantity: number;
  item_total: number;
  image_url: string;
  available_stock: number;
  in_stock: boolean;
}

export interface CartData {
  items: CartItem[];
  item_count: number;
  subtotal: number;
  user_id?: number;
  session_id?: string;
}

export interface PricingSummary {
  subtotal: number;
  discount_amount: number;
  coupon_applied?: {
    code: string;
    discount_value: number;
    discount_type: string;
    saved_amount: number;
  };
  tax_amount: number;
  tax_rate_pct: number;
  shipping_fee: number;
  free_shipping_eligible: boolean;
  amount_needed_for_free_shipping: number;
  final_amount: number;
}

export interface SagaStep {
  step: number;
  name: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  service: string;
}

export interface SagaCheckoutResult {
  saga_id: string;
  order_number: string;
  status: 'SUCCESS' | 'COMPENSATED_FAILED';
  steps: SagaStep[];
  final_amount: number;
  tracking_number?: string;
  carrier?: string;
  estimated_delivery?: string;
  error?: string;
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  price: number;
  quantity: number;
  image_url?: string;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  status: 'PLACED' | 'CONFIRMED' | 'PROCESSING' | 'SHIPPED' | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'CANCELLED' | 'RETURNED';
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  shipping_fee: number;
  final_amount: number;
  shipping_address: {
    full_name: string;
    phone: string;
    street: string;
    city: string;
    state: string;
    pincode: string;
  };
  payment_method: string;
  payment_status: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface ShipmentMilestone {
  status: string;
  title: string;
  location: string;
  timestamp: string;
  completed: boolean;
}

export interface Shipment {
  shipment_id: string;
  order_number: string;
  tracking_number: string;
  carrier: string;
  status: string;
  estimated_delivery?: string;
  current_location: string;
  milestones: ShipmentMilestone[];
  created_at: string;
}

export interface Review {
  id: number;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  helpful_votes: number;
  verified_purchase: boolean;
  created_at: string;
}

export interface SupportTicket {
  id: number;
  ticket_id: string;
  user_id: number;
  user_email: string;
  order_number?: string;
  subject: string;
  category: string;
  message: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  responses: Array<{
    sender_name: string;
    sender_role: string;
    message: string;
    timestamp: string;
  }>;
  created_at: string;
}

export interface ServiceHealthItem {
  service_name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL';
  error_rate_pct: number;
  avg_latency_ms: number;
  total_requests: number;
  failed_requests: number;
  last_seen?: string;
  dependencies: string[];
}

export interface TelemetryLog {
  timestamp: string;
  service_name: string;
  endpoint: string;
  http_method: string;
  status_code: number;
  response_time_ms: number;
  error_message: string;
  correlation_id: string;
  transaction_id: string;
  severity: 'INFO' | 'MEDIUM' | 'HIGH';
}
