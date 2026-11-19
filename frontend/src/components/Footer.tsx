import React from 'react';
import { ShieldCheck, Truck, RotateCcw, Headphones, Cpu, Database, Activity } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-amazon-dark text-gray-300 mt-16 border-t border-gray-800">
      {/* Trust Highlights Strip */}
      <div className="bg-amazon-light py-6 border-b border-gray-700/60">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="flex items-center gap-3">
            <Truck className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">Free & Fast Delivery</p>
              <p className="text-xs text-gray-400">On all enterprise orders above ₹499</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">100% Secure Checkout</p>
              <p className="text-xs text-gray-400">Encrypted distributed Saga protocol</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <RotateCcw className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">10-Day Hassle-Free Returns</p>
              <p className="text-xs text-gray-400">Instant refund directly to payment source</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Headphones className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">24/7 Dedicated Support</p>
              <p className="text-xs text-gray-400">Active resolution by customer engineers</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-xs">
        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">About ApexMart</h4>
          <p className="text-gray-400 leading-relaxed mb-4">
            Industrial-grade e-commerce microservices platform built with Python FastAPI, React, RabbitMQ, PostgreSQL, and comprehensive Prometheus & Grafana telemetry.
          </p>
          <div className="flex items-center gap-2 text-emerald-400">
            <Activity className="w-4 h-4" />
            <span className="font-semibold">All 15 Microservices Active</span>
          </div>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Microservices Architecture</h4>
          <ul className="space-y-1.5 text-gray-400">
            <li>• Auth & Identity Service</li>
            <li>• Product Catalog & Search</li>
            <li>• Real-Time Inventory & Reservation</li>
            <li>• Distributed Saga Checkout</li>
            <li>• Sandboxed Payment Gateway</li>
            <li>• Carrier Shipping & Live Tracking</li>
            <li>• RabbitMQ Event Messaging</li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Chaos & Observability</h4>
          <ul className="space-y-1.5 text-gray-400">
            <li>• 18 Synthetic Fault Injection Scenarios</li>
            <li>• Pre-configured Cascading Failure Modes</li>
            <li>• OpenTelemetry W3C TraceContext</li>
            <li>• Prometheus Metrics Exporter (/metrics)</li>
            <li>• Centralized Telemetry Stream (/api/telemetry)</li>
            <li>• Structured JSON Application Logs</li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Enterprise Status</h4>
          <div className="bg-gray-900 p-3 rounded border border-gray-800 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">System Gateway:</span>
              <span className="text-emerald-400 font-bold">ONLINE</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Event Broker:</span>
              <span className="text-emerald-400 font-bold">CONNECTED</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">PostgreSQL DB:</span>
              <span className="text-emerald-400 font-bold">HEALTHY</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Telemetry Stream:</span>
              <span className="text-amber-400 font-bold">STREAMING</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Copyright */}
      <div className="border-t border-gray-800 py-6 text-center text-xs text-gray-500">
        <p>© 2026 ApexMart Enterprise E-Commerce Platform. High-Performance Distributed Microservices Architecture.</p>
      </div>
    </footer>
  );
};
