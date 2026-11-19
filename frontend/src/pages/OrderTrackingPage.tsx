import React, { useState, useEffect } from 'react';
import { 
  Truck, Package, MapPin, CheckCircle2, Clock, 
  ArrowLeft, RefreshCw, ChevronRight 
} from 'lucide-react';
import { Shipment } from '../types';
import api from '../api/client';

interface OrderTrackingPageProps {
  trackingQuery?: string;
  onNavigate: (page: string, params?: any) => void;
}

export const OrderTrackingPage: React.FC<OrderTrackingPageProps> = ({ 
  trackingQuery = 'ORD-20261119-SEED01', 
  onNavigate 
}) => {
  const [query, setQuery] = useState(trackingQuery);
  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchTracking = async (searchTarget: string) => {
    setLoading(true);
    try {
      const res = await api.get(`/shipping/track/${searchTarget}`);
      setShipment(res.data);
    } catch (e) {
      console.error(e);
      setShipment(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (trackingQuery) {
      setQuery(trackingQuery);
      fetchTracking(trackingQuery);
    }
  }, [trackingQuery]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
        <button 
          onClick={() => onNavigate('orders')}
          className="p-1.5 hover:bg-gray-100 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Shipment Live Tracking</h1>
          <p className="text-xs text-gray-500">Real-time milestones from carrier logistics network</p>
        </div>
      </div>

      {/* Search Input Bar */}
      <form 
        onSubmit={(e) => { e.preventDefault(); fetchTracking(query); }} 
        className="bg-white p-3 rounded-xl border border-gray-200 shadow-sm flex gap-2"
      >
        <input
          type="text"
          placeholder="Enter Order # or Tracking # (e.g. TRK-BLR-892147)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 text-xs p-2.5 rounded border border-gray-300 focus:outline-none font-mono"
        />
        <button
          type="submit"
          className="bg-gray-900 hover:bg-gray-800 text-white font-bold text-xs px-5 py-2.5 rounded transition-colors"
        >
          Track
        </button>
      </form>

      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-gray-200 text-center text-gray-500 text-sm">
          Fetching carrier milestones...
        </div>
      ) : shipment ? (
        <div className="space-y-6">
          {/* Status Highlight Card */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-100">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-gray-400 font-bold block">
                  Carrier: {shipment.carrier}
                </span>
                <h2 className="text-xl font-bold text-gray-900 mt-0.5">
                  Tracking # <span className="font-mono text-blue-600">{shipment.tracking_number}</span>
                </h2>
                <p className="text-xs text-gray-500">Order: {shipment.order_number}</p>
              </div>

              {/* Refresh Button */}
              <button
                onClick={() => fetchTracking(shipment.tracking_number)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold text-xs px-3.5 py-2 rounded-lg border border-gray-300 transition-colors flex items-center gap-1.5"
                title="Refresh tracking status"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block font-medium">Current Status:</span>
                <span className="font-bold text-emerald-700 text-sm">{shipment.status}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block font-medium">Current Location:</span>
                <span className="font-bold text-gray-800 text-sm">{shipment.current_location}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block font-medium">Estimated Delivery:</span>
                <span className="font-bold text-gray-800 text-sm">
                  {shipment.estimated_delivery ? new Date(shipment.estimated_delivery).toLocaleDateString() : 'In 2-3 Days'}
                </span>
              </div>
            </div>
          </div>

          {/* Stepper Timeline */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-6">
            <h3 className="font-bold text-sm text-gray-900 uppercase tracking-wider">Milestone Journey</h3>

            <div className="relative pl-6 border-l-2 border-gray-200 space-y-8 ml-2">
              {shipment.milestones && shipment.milestones.map((m, idx) => (
                <div key={idx} className="relative">
                  {/* Dot */}
                  <div className={`absolute -left-[31px] top-0.5 w-4 h-4 rounded-full border-2 ${
                    m.completed 
                      ? 'bg-emerald-600 border-white ring-4 ring-emerald-100' 
                      : 'bg-white border-gray-300'
                  }`} />

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className={`text-xs font-bold ${m.completed ? 'text-gray-900' : 'text-gray-400'}`}>
                        {m.title}
                      </h4>
                      {m.completed && (
                        <span className="text-[10px] bg-emerald-50 text-emerald-700 px-1.5 py-0.2 rounded font-semibold">
                          Completed
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-gray-500 mt-0.5">{m.location}</p>
                    {m.timestamp && (
                      <p className="text-[10px] text-gray-400 font-mono mt-0.5">
                        {new Date(m.timestamp).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white p-12 rounded-xl border border-gray-200 text-center space-y-3">
          <Truck className="w-10 h-10 text-gray-300 mx-auto" />
          <h3 className="font-bold text-base text-gray-800">No shipment record found</h3>
          <p className="text-xs text-gray-500">Check the tracking number or order number entered above.</p>
        </div>
      )}
    </div>
  );
};
