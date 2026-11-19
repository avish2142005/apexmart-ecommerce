import React, { useState, useEffect } from 'react';
import { 
  Trash2, Plus, Minus, ShoppingCart, Tag, ArrowRight, 
  Check, Truck, ShieldCheck 
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { PricingSummary } from '../types';
import api from '../api/client';

interface CartPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const CartPage: React.FC<CartPageProps> = ({ onNavigate }) => {
  const { cart, updateQuantity, removeFromCart, clearCart } = useCart();
  const [couponCode, setCouponCode] = useState('');
  const [pricing, setPricing] = useState<PricingSummary>({
    subtotal: cart.subtotal,
    discount_amount: 0,
    tax_amount: 0,
    tax_rate_pct: 18,
    shipping_fee: cart.subtotal >= 499 ? 0 : 49,
    free_shipping_eligible: cart.subtotal >= 499,
    amount_needed_for_free_shipping: Math.max(0, 499 - cart.subtotal),
    final_amount: cart.subtotal + (cart.subtotal >= 499 ? 0 : 49)
  });
  const [couponMsg, setCouponMsg] = useState<{ text: string; error: boolean } | null>(null);

  // Recalculate pricing on cart or coupon changes
  useEffect(() => {
    const calc = async () => {
      if (cart.items.length === 0) return;
      try {
        const payload = {
          items: cart.items.map(it => ({
            product_id: it.product_id,
            price: it.effective_price,
            quantity: it.quantity
          })),
          coupon_code: couponCode.trim() || undefined
        };
        const res = await api.post('/pricing/calculate', payload);
        setPricing(res.data);
      } catch (e) {
        console.error(e);
      }
    };
    calc();
  }, [cart, couponCode]);

  const handleApplyCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!couponCode.trim()) return;
    try {
      const res = await api.post('/pricing/coupon/validate', {
        code: couponCode,
        order_amount: cart.subtotal
      });
      setCouponMsg({ text: res.data.message, error: false });
    } catch (err: any) {
      setCouponMsg({ text: err.message || 'Invalid coupon code', error: true });
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto text-gray-400">
          <ShoppingCart className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Your Shopping Cart is empty</h2>
        <p className="text-sm text-gray-500 max-w-sm mx-auto">
          Explore our collection of over 100 enterprise tech items, electronics, and tools.
        </p>
        <button
          onClick={() => onNavigate('home')}
          className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold text-xs px-6 py-3 rounded-lg shadow transition-colors inline-flex items-center gap-2"
        >
          Start Shopping <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900">Shopping Cart ({cart.item_count} items)</h1>
        <button
          onClick={clearCart}
          className="text-xs text-red-600 hover:underline flex items-center gap-1 font-semibold"
        >
          <Trash2 className="w-3.5 h-3.5" /> Clear Cart
        </button>
      </div>

      {/* Free shipping banner */}
      <div className="bg-emerald-50 border border-emerald-200 p-3.5 rounded-lg text-xs flex items-center justify-between">
        <div className="flex items-center gap-2 text-emerald-800 font-semibold">
          <Truck className="w-4 h-4 text-emerald-600" />
          {pricing.free_shipping_eligible ? (
            <span>Your order is eligible for <b>FREE Delivery</b>!</span>
          ) : (
            <span>Add ₹{pricing.amount_needed_for_free_shipping.toFixed(2)} more of eligible items to get FREE Delivery.</span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Cart Items List (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
            {cart.items.map((item) => (
              <div key={item.cart_item_id} className="p-4 sm:p-5 flex gap-4 items-center">
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-20 h-20 object-contain rounded bg-gray-50 border border-gray-100 p-1 shrink-0"
                />

                <div className="flex-1 min-w-0 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 font-mono">
                    {item.brand} • {item.category}
                  </span>
                  <h3 className="font-semibold text-sm text-gray-900 truncate">{item.name}</h3>
                  <div className="text-xs">
                    <span className="font-bold text-gray-900">₹{item.effective_price.toLocaleString('en-IN')}</span>
                    {item.discount_pct > 0 && (
                      <span className="text-[11px] text-gray-400 line-through ml-2">
                        ₹{item.price.toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-emerald-600 font-medium">In Stock</p>
                </div>

                {/* Quantity and Actions */}
                <div className="flex flex-col items-end gap-3 shrink-0">
                  <div className="flex items-center border border-gray-200 rounded-md overflow-hidden bg-gray-50">
                    <button
                      onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                      className="p-1.5 hover:bg-gray-200 transition-colors"
                    >
                      <Minus className="w-3.5 h-3.5 text-gray-600" />
                    </button>
                    <span className="px-3 text-xs font-bold text-gray-800">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                      className="p-1.5 hover:bg-gray-200 transition-colors"
                    >
                      <Plus className="w-3.5 h-3.5 text-gray-600" />
                    </button>
                  </div>

                  <span className="text-sm font-bold text-gray-900">
                    ₹{item.item_total.toLocaleString('en-IN')}
                  </span>

                  <button
                    onClick={() => removeFromCart(item.product_id)}
                    className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                  >
                    <Trash2 className="w-3 h-3" /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Order Summary & Checkout Box (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-gray-900 pb-3 border-b border-gray-100">
              Order Summary
            </h2>

            {/* Coupon Code Input */}
            <form onSubmit={handleApplyCoupon} className="space-y-2">
              <label className="block text-xs font-semibold text-gray-700">Apply Promo Coupon</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. SAVE10, SUPER50"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                  className="flex-1 text-xs p-2 border border-gray-300 rounded focus:outline-none font-mono uppercase"
                />
                <button
                  type="submit"
                  className="bg-gray-900 hover:bg-gray-800 text-white font-semibold text-xs px-3.5 py-2 rounded transition-colors"
                >
                  Apply
                </button>
              </div>
              {couponMsg && (
                <p className={`text-[11px] font-semibold ${couponMsg.error ? 'text-red-600' : 'text-emerald-600'}`}>
                  {couponMsg.text}
                </p>
              )}
            </form>

            {/* Price Calculations Breakdown */}
            <div className="space-y-2 text-xs pt-2 border-t border-gray-100">
              <div className="flex justify-between text-gray-600">
                <span>Items Subtotal:</span>
                <span>₹{pricing.subtotal.toLocaleString('en-IN')}</span>
              </div>
              {pricing.discount_amount > 0 && (
                <div className="flex justify-between text-emerald-600 font-semibold">
                  <span>Coupon Discount ({pricing.coupon_applied?.code}):</span>
                  <span>-₹{pricing.discount_amount.toLocaleString('en-IN')}</span>
                </div>
              )}
              <div className="flex justify-between text-gray-600">
                <span>Shipping Fee:</span>
                <span>{pricing.shipping_fee === 0 ? 'FREE' : `₹${pricing.shipping_fee.toFixed(2)}`}</span>
              </div>
              <div className="flex justify-between text-gray-500 text-[11px]">
                <span>Estimated GST Tax Component:</span>
                <span>₹{pricing.tax_amount.toLocaleString('en-IN')}</span>
              </div>

              <div className="flex justify-between text-base font-extrabold text-gray-900 pt-3 border-t border-gray-200">
                <span>Final Total:</span>
                <span>₹{pricing.final_amount.toLocaleString('en-IN')}</span>
              </div>
            </div>

            {/* Checkout Action */}
            <button
              onClick={() => onNavigate('checkout', { coupon_code: couponCode })}
              className="w-full bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold text-sm py-3 rounded-lg shadow transition-colors flex items-center justify-center gap-2"
            >
              Proceed to Buy ({cart.item_count} items) <ArrowRight className="w-4 h-4" />
            </button>

            <div className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1.5 pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Saga-orchestrated 100% safe checkout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
