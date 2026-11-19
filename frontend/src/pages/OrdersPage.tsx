import React, { useState, useEffect } from 'react';
import { 
  Package, Truck, RotateCcw, AlertCircle, CheckCircle2, 
  ExternalLink, Calendar, ShieldCheck, XCircle 
} from 'lucide-react';
import { Order } from '../types';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

interface OrdersPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const OrdersPage: React.FC<OrdersPageProps> = ({ onNavigate }) => {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get('/orders/', { params: { user_id: user?.id || 2 } });
      setOrders(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [user]);

  const handleCancelOrder = async (orderNumber: string) => {
    if (!window.confirm(`Are you sure you want to cancel order ${orderNumber}? A full refund will be initiated.`)) {
      return;
    }
    try {
      await api.post(`/orders/${orderNumber}/cancel`, { reason: 'Customer requested cancellation' });
      fetchOrders();
    } catch (err: any) {
      alert(err.message || 'Error cancelling order');
    }
  };

  const filteredOrders = filterStatus === 'ALL'
    ? orders
    : orders.filter(o => o.status === filterStatus);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DELIVERED':
        return <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded">Delivered</span>;
      case 'CONFIRMED':
      case 'PROCESSING':
        return <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-1 rounded">Confirmed & Processing</span>;
      case 'SHIPPED':
      case 'OUT_FOR_DELIVERY':
        return <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded">In Transit</span>;
      case 'CANCELLED':
        return <span className="bg-red-100 text-red-800 text-xs font-bold px-2.5 py-1 rounded">Cancelled (Refunded)</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 text-xs font-bold px-2.5 py-1 rounded">{status}</span>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Orders & Fulfillment History</h1>
          <p className="text-xs text-gray-500 mt-0.5">Track, cancel, or raise support inquiries on your shipments</p>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 bg-white p-1 rounded-lg border border-gray-200 text-xs">
          {['ALL', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                filterStatus === st ? 'bg-amazon-dark text-white' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-gray-200 text-center text-gray-500 text-sm">
          Loading order history...
        </div>
      ) : filteredOrders.length > 0 ? (
        <div className="space-y-4">
          {filteredOrders.map((order) => (
            <div key={order.id} className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              {/* Order Card Header */}
              <div className="bg-gray-50 px-6 py-3.5 border-b border-gray-200 flex flex-wrap items-center justify-between gap-4 text-xs">
                <div className="flex flex-wrap gap-6 text-gray-600">
                  <div>
                    <span className="block text-gray-400">Order Placed</span>
                    <span className="font-semibold text-gray-900">
                      {new Date(order.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="block text-gray-400">Total Amount</span>
                    <span className="font-bold text-gray-900">
                      ₹{order.final_amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div>
                    <span className="block text-gray-400">Ship To</span>
                    <span className="font-semibold text-gray-900">
                      {order.shipping_address?.full_name || 'Customer'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="block text-gray-400 font-mono">ORDER # {order.order_number}</span>
                    <span className="text-[10px] text-gray-500">Method: {order.payment_method}</span>
                  </div>
                  {getStatusBadge(order.status)}
                </div>
              </div>

              {/* Order Items & Actions */}
              <div className="p-6 divide-y divide-gray-100">
                {order.items.map((item) => (
                  <div key={item.id} className="py-4 first:pt-0 last:pb-0 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4 min-w-0">
                      <img
                        src={item.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120'}
                        alt={item.product_name}
                        className="w-16 h-16 object-contain rounded bg-gray-50 border border-gray-100 p-1 shrink-0"
                      />
                      <div className="min-w-0">
                        <h4 className="font-semibold text-sm text-gray-900 truncate max-w-md">
                          {item.product_name}
                        </h4>
                        <p className="text-xs text-gray-500 mt-0.5">
                          Qty: {item.quantity} × ₹{item.price.toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2 text-xs">
                      <button
                        onClick={() => onNavigate('track', { trackingNumber: order.order_number })}
                        className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold px-4 py-2 rounded-md shadow-sm transition-colors flex items-center gap-1.5"
                      >
                        <Truck className="w-3.5 h-3.5" /> Track Package
                      </button>
                      <button
                        onClick={() => onNavigate('support', { orderNumber: order.order_number })}
                        className="border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium px-3 py-2 rounded-md transition-colors"
                      >
                        Need Help?
                      </button>
                      {order.status !== 'CANCELLED' && order.status !== 'DELIVERED' && (
                        <button
                          onClick={() => handleCancelOrder(order.order_number)}
                          className="text-red-600 hover:bg-red-50 border border-red-200 font-medium px-3 py-2 rounded-md transition-colors"
                        >
                          Cancel Order
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white p-16 rounded-xl border border-gray-200 text-center space-y-4">
          <Package className="w-12 h-12 text-gray-300 mx-auto" />
          <h3 className="text-base font-bold text-gray-800">No orders found in this view</h3>
          <p className="text-xs text-gray-500">Your placed orders will show up here along with live shipping statuses.</p>
          <button
            onClick={() => onNavigate('home')}
            className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold text-xs px-5 py-2.5 rounded-lg shadow"
          >
            Explore Catalog
          </button>
        </div>
      )}
    </div>
  );
};
