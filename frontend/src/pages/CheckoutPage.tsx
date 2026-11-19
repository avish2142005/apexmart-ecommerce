import React, { useState } from 'react';
import { 
  CreditCard, Smartphone, Building, Banknote, 
  AlertTriangle, ArrowLeft, Loader2, ShieldCheck, Lock
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { SagaCheckoutResult } from '../types';
import api from '../api/client';

interface CheckoutPageProps {
  onNavigate: (page: string, params?: any) => void;
  initialCoupon?: string;
}

export const CheckoutPage: React.FC<CheckoutPageProps> = ({ onNavigate, initialCoupon = '' }) => {
  const { cart } = useCart();
  const { user } = useAuth();

  const [address, setAddress] = useState({
    full_name: user?.full_name || 'John Doe',
    phone: user?.phone || '+919876543210',
    street: user?.address?.street || 'Flat 402, Green Glen Layout, Bellandur',
    city: user?.address?.city || 'Bengaluru',
    state: user?.address?.state || 'Karnataka',
    pincode: user?.address?.zip || '560103'
  });

  const [paymentMethod, setPaymentMethod] = useState<'CARD' | 'UPI' | 'NETBANKING' | 'COD'>('CARD');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handlePlaceOrder = async () => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const payload = {
        user_id: user?.id || 2,
        items: cart.items.map(it => ({
          product_id: it.product_id,
          quantity: it.quantity
        })),
        shipping_address: address,
        payment_method: paymentMethod,
        coupon_code: initialCoupon || undefined,
        simulate_payment_failure: false,
        idempotency_key: `IDEMP-${Date.now()}`
      };

      const res = await api.post('/checkout/initiate', payload);
      setIsProcessing(false);

      // Navigate to order confirmation
      onNavigate('order-confirmation', { result: res.data });

    } catch (err: any) {
      setIsProcessing(false);
      try {
        const parsed = JSON.parse(err.message);
        setErrorMessage(parsed.message || parsed.error || 'Payment authorization declined by provider.');
      } catch {
        setErrorMessage(err.message || 'We could not complete your payment. Please try another payment method.');
      }
    }
  };

  const deliveryFee = cart.subtotal >= 499 ? 0 : 49;
  const grandTotal = cart.subtotal + deliveryFee;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onNavigate('cart')}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Secure Checkout</h1>
            <p className="text-xs text-gray-500">Confirm delivery address and select payment</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full font-semibold">
          <Lock className="w-3.5 h-3.5" />
          <span>256-bit SSL Encrypted</span>
        </div>
      </div>

      {/* Processing Banner */}
      {isProcessing && (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-5 shadow-sm flex items-center gap-3">
          <Loader2 className="w-6 h-6 text-amber-600 animate-spin shrink-0" />
          <div>
            <p className="font-bold text-sm text-gray-900">Processing Your Order...</p>
            <p className="text-xs text-gray-600">Please do not refresh or close this window while we verify your order and payment.</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-300 rounded-xl p-5 shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-red-800 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
            <span>Payment Could Not Be Processed</span>
          </div>
          <p className="text-xs text-red-700 leading-relaxed">
            {errorMessage}
          </p>
          <p className="text-xs text-gray-600">
            Your card has not been charged and items remain safely in your cart. Please check your payment details or choose an alternate payment method below.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Form (7 cols) */}
        <div className="md:col-span-7 space-y-6">
          {/* Step 1: Delivery Address */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-amber-400 text-black text-xs font-bold flex items-center justify-center">1</span>
              Delivery Address
            </h2>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="col-span-2">
                <label className="block font-semibold text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={address.full_name}
                  onChange={(e) => setAddress({ ...address, full_name: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block font-semibold text-gray-700 mb-1">Street Address / House No.</label>
                <input
                  type="text"
                  value={address.street}
                  onChange={(e) => setAddress({ ...address, street: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={address.city}
                  onChange={(e) => setAddress({ ...address, city: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-gray-700 mb-1">State</label>
                <input
                  type="text"
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-gray-700 mb-1">PIN Code</label>
                <input
                  type="text"
                  value={address.pincode}
                  onChange={(e) => setAddress({ ...address, pincode: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Phone Number</label>
                <input
                  type="text"
                  value={address.phone}
                  onChange={(e) => setAddress({ ...address, phone: e.target.value })}
                  className="w-full p-2.5 border border-gray-300 rounded focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>
          </div>

          {/* Step 2: Payment Method */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-amber-400 text-black text-xs font-bold flex items-center justify-center">2</span>
              Payment Method
            </h2>

            <div className="space-y-2.5">
              <label 
                className={`flex items-center gap-3 p-3.5 rounded-lg border cursor-pointer transition-all ${
                  paymentMethod === 'CARD' ? 'border-amber-500 bg-amber-50/40 ring-1 ring-amber-400' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === 'CARD'}
                  onChange={() => setPaymentMethod('CARD')}
                  className="accent-amber-500"
                />
                <CreditCard className="w-5 h-5 text-gray-700" />
                <div className="text-xs">
                  <p className="font-bold text-gray-800">Credit / Debit Card</p>
                  <p className="text-gray-500">Visa, Mastercard, RuPay, American Express</p>
                </div>
              </label>

              <label 
                className={`flex items-center gap-3 p-3.5 rounded-lg border cursor-pointer transition-all ${
                  paymentMethod === 'UPI' ? 'border-amber-500 bg-amber-50/40 ring-1 ring-amber-400' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === 'UPI'}
                  onChange={() => setPaymentMethod('UPI')}
                  className="accent-amber-500"
                />
                <Smartphone className="w-5 h-5 text-gray-700" />
                <div className="text-xs">
                  <p className="font-bold text-gray-800">UPI / QR (Google Pay, PhonePe, Paytm)</p>
                  <p className="text-gray-500">Instant direct bank payment via UPI ID or QR code</p>
                </div>
              </label>

              <label 
                className={`flex items-center gap-3 p-3.5 rounded-lg border cursor-pointer transition-all ${
                  paymentMethod === 'NETBANKING' ? 'border-amber-500 bg-amber-50/40 ring-1 ring-amber-400' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === 'NETBANKING'}
                  onChange={() => setPaymentMethod('NETBANKING')}
                  className="accent-amber-500"
                />
                <Building className="w-5 h-5 text-gray-700" />
                <div className="text-xs">
                  <p className="font-bold text-gray-800">Net Banking</p>
                  <p className="text-gray-500">All major banks supported (HDFC, ICICI, SBI, Axis)</p>
                </div>
              </label>

              <label 
                className={`flex items-center gap-3 p-3.5 rounded-lg border cursor-pointer transition-all ${
                  paymentMethod === 'COD' ? 'border-amber-500 bg-amber-50/40 ring-1 ring-amber-400' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === 'COD'}
                  onChange={() => setPaymentMethod('COD')}
                  className="accent-amber-500"
                />
                <Banknote className="w-5 h-5 text-gray-700" />
                <div className="text-xs">
                  <p className="font-bold text-gray-800">Cash on Delivery (COD)</p>
                  <p className="text-gray-500">Pay cash or scan QR code at the time of doorstep delivery</p>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Right Summary (5 cols) */}
        <div className="md:col-span-5 space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4 sticky top-24">
            <h2 className="text-base font-bold text-gray-900 pb-3 border-b border-gray-100">
              Order Summary
            </h2>

            {/* Item Mini List */}
            <div className="max-h-48 overflow-y-auto space-y-3 pr-1 divide-y divide-gray-100">
              {cart.items.map((it) => (
                <div key={it.cart_item_id} className="pt-2 first:pt-0 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 min-w-0 pr-2">
                    <img src={it.image_url} alt="" className="w-9 h-9 object-contain bg-gray-50 p-1 rounded" />
                    <div className="truncate">
                      <p className="font-semibold text-gray-900 truncate">{it.name}</p>
                      <p className="text-gray-400">Qty: {it.quantity}</p>
                    </div>
                  </div>
                  <span className="font-bold text-gray-800 shrink-0">
                    ₹{it.item_total.toLocaleString('en-IN')}
                  </span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-gray-100 space-y-2 text-xs">
              <div className="flex justify-between text-gray-600">
                <span>Items ({cart.item_count}):</span>
                <span>₹{cart.subtotal.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Shipping & Delivery:</span>
                <span className="text-emerald-600 font-semibold">{deliveryFee === 0 ? 'FREE' : '₹49.00'}</span>
              </div>
              <div className="flex justify-between text-base font-extrabold text-gray-900 pt-2 border-t border-gray-200">
                <span>Order Total:</span>
                <span>₹{grandTotal.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <button
              onClick={handlePlaceOrder}
              disabled={isProcessing || cart.items.length === 0}
              className="w-full bg-amber-400 hover:bg-amber-500 disabled:bg-gray-300 text-gray-900 font-bold text-sm py-3 rounded-lg shadow transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Placing Your Order...
                </>
              ) : (
                'Place Your Order'
              )}
            </button>

            <div className="pt-2 flex items-center justify-center gap-1.5 text-[11px] text-gray-500">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Safe & Secure 100% Purchase Protection</span>
            </div>

            <p className="text-[10px] text-gray-400 text-center leading-tight">
              By placing your order, you agree to ApexMart's Conditions of Use & Sale.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
