import React from 'react';
import { 
  CheckCircle2, Package, Truck, ArrowRight, Calendar, 
  ShieldCheck, MapPin
} from 'lucide-react';
import { SagaCheckoutResult } from '../types';

interface OrderConfirmationPageProps {
  result?: SagaCheckoutResult;
  onNavigate: (page: string, params?: any) => void;
}

export const OrderConfirmationPage: React.FC<OrderConfirmationPageProps> = ({ 
  result, 
  onNavigate 
}) => {
  const orderNumber = result?.order_number || 'ORD-20261119-SEED01';
  const trackingNumber = result?.tracking_number || 'TRK-BLR-892147';
  const carrier = result?.carrier || 'Amazon Logistics';
  const eta = result?.estimated_delivery || 'Saturday, 22 November 2026';
  const finalAmount = result?.final_amount || 26991.0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Success Hero Header */}
      <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm text-center space-y-4">
        <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
          <CheckCircle2 className="w-10 h-10" />
        </div>

        <div className="space-y-1">
          <h1 className="text-3xl font-extrabold text-gray-900">Order Placed, Thank You!</h1>
          <p className="text-sm text-gray-500">
            Confirmation has been sent to your registered email address and mobile number.
          </p>
        </div>

        {/* Quick Order Info Grid */}
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 grid grid-cols-2 sm:grid-cols-4 gap-4 text-left text-xs">
          <div>
            <span className="text-gray-400 block font-medium">Order Number:</span>
            <span className="font-mono font-bold text-gray-900">{orderNumber}</span>
          </div>
          <div>
            <span className="text-gray-400 block font-medium">Carrier:</span>
            <span className="font-bold text-gray-900">{carrier}</span>
          </div>
          <div>
            <span className="text-gray-400 block font-medium">Tracking Number:</span>
            <span className="font-mono font-bold text-blue-600">{trackingNumber}</span>
          </div>
          <div>
            <span className="text-gray-400 block font-medium">Estimated Delivery:</span>
            <span className="font-bold text-emerald-700">{eta}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('track', { trackingNumber: trackingNumber })}
            className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold text-xs px-6 py-2.5 rounded-lg shadow transition-colors flex items-center gap-1.5"
          >
            <Truck className="w-4 h-4" /> Track Package
          </button>
          <button
            onClick={() => onNavigate('orders')}
            className="bg-white hover:bg-gray-50 border border-gray-300 text-gray-800 font-semibold text-xs px-5 py-2.5 rounded-lg transition-colors"
          >
            View Your Orders
          </button>
          <button
            onClick={() => onNavigate('home')}
            className="text-xs text-blue-600 hover:underline px-4 py-2 font-medium"
          >
            Continue Shopping →
          </button>
        </div>
      </div>

      {/* Delivery & Protection Information */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-2 text-xs">
          <div className="flex items-center gap-2 text-gray-800 font-bold text-sm">
            <Package className="w-5 h-5 text-amber-500" />
            <span>Shipping Updates</span>
          </div>
          <p className="text-gray-600 leading-relaxed">
            Your package is being prepared at our primary fulfillment center. You will receive live WhatsApp and SMS tracking updates as it moves through each transit hub.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-2 text-xs">
          <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <span>ApexMart A-to-z Guarantee</span>
          </div>
          <p className="text-gray-600 leading-relaxed">
            Covers the condition of your item and its timely delivery. If anything is wrong with your order, easily request an exchange or return within 10 days.
          </p>
        </div>
      </div>
    </div>
  );
};
