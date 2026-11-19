import React from 'react';
import { ShieldCheck, Truck, RotateCcw, Headphones } from 'lucide-react';

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
              <p className="text-xs text-gray-400">On all eligible orders above ₹499</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">100% Secure Checkout</p>
              <p className="text-xs text-gray-400">Encrypted payments & PCI-DSS compliance</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <RotateCcw className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">10-Day Easy Returns</p>
              <p className="text-xs text-gray-400">Instant refund directly to payment source</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Headphones className="w-8 h-8 text-amber-400 shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">24/7 Dedicated Support</p>
              <p className="text-xs text-gray-400">Active resolution by customer specialists</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-xs">
        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Get to Know Us</h4>
          <ul className="space-y-2 text-gray-400">
            <li className="hover:text-white cursor-pointer transition-colors">About ApexMart</li>
            <li className="hover:text-white cursor-pointer transition-colors">Careers & Culture</li>
            <li className="hover:text-white cursor-pointer transition-colors">Press Releases</li>
            <li className="hover:text-white cursor-pointer transition-colors">ApexMart Science & Tech</li>
            <li className="hover:text-white cursor-pointer transition-colors">Corporate Governance</li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Connect with Us</h4>
          <ul className="space-y-2 text-gray-400">
            <li className="hover:text-white cursor-pointer transition-colors">Facebook</li>
            <li className="hover:text-white cursor-pointer transition-colors">Twitter (X)</li>
            <li className="hover:text-white cursor-pointer transition-colors">Instagram</li>
            <li className="hover:text-white cursor-pointer transition-colors">YouTube Channel</li>
            <li className="hover:text-white cursor-pointer transition-colors">Customer Community</li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Make Money with Us</h4>
          <ul className="space-y-2 text-gray-400">
            <li className="hover:text-white cursor-pointer transition-colors">Sell on ApexMart</li>
            <li className="hover:text-white cursor-pointer transition-colors">Protect & Build Your Brand</li>
            <li className="hover:text-white cursor-pointer transition-colors">Become an Affiliate</li>
            <li className="hover:text-white cursor-pointer transition-colors">Fulfillment by ApexMart (FBA)</li>
            <li className="hover:text-white cursor-pointer transition-colors">Advertise Your Products</li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-sm mb-3 uppercase tracking-wider">Let Us Help You</h4>
          <ul className="space-y-2 text-gray-400">
            <li className="hover:text-white cursor-pointer transition-colors">Your Account</li>
            <li className="hover:text-white cursor-pointer transition-colors">Returns & Replacement Centre</li>
            <li className="hover:text-white cursor-pointer transition-colors">100% Purchase Protection</li>
            <li className="hover:text-white cursor-pointer transition-colors">ApexMart Mobile App</li>
            <li className="hover:text-white cursor-pointer transition-colors">Help & Customer Support</li>
          </ul>
        </div>
      </div>

      {/* Bottom Copyright */}
      <div className="border-t border-gray-800 py-6 text-center text-xs text-gray-400">
        <p>© 2026 ApexMart, Inc. or its affiliates. All rights reserved. Conditions of Use & Sale | Privacy Notice | Interest-Based Ads</p>
      </div>
    </footer>
  );
};
