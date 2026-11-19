import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Tag, ChevronRight, 
  ArrowRight, Clock, Flame, Truck, ShieldCheck, RotateCcw, Headphones,
  Percent, Gift
} from 'lucide-react';
import { Product } from '../types';
import { ProductCard } from '../components/ProductCard';
import api from '../api/client';

interface HomePageProps {
  onNavigate: (page: string, params?: any) => void;
  onSelectProduct: (product: Product) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate, onSelectProduct }) => {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [deals, setDeals] = useState<Product[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [featRes, catRes] = await Promise.all([
          api.get('/catalog/featured'),
          api.get('/catalog/categories')
        ]);
        setFeaturedProducts(featRes.data.featured || []);
        setDeals(featRes.data.deals_of_the_day || []);
        setCategories(catRes.data || []);
      } catch (err) {
        console.error('Error loading homepage data', err);
      } finally {
        setLoading(false);
      }
    };
    loadHomeData();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      {/* Hero Banner Section */}
      <div className="relative bg-gradient-to-r from-amazon-dark via-[#1e293b] to-amazon-light text-white overflow-hidden shadow-xl">
        <div className="max-w-7xl mx-auto px-4 py-12 md:py-16 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="space-y-4 z-10">
            <div className="inline-flex items-center gap-2 bg-amber-400/20 text-amber-300 border border-amber-400/40 px-3 py-1 rounded-full text-xs font-semibold">
              <Sparkles className="w-4 h-4" />
              <span>Mega Festival Sale is Live</span>
            </div>
            <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight">
              Top Brands. Unmatched Deals. Delivered Fast.
            </h1>
            <p className="text-gray-300 text-sm md:text-base leading-relaxed max-w-lg">
              Explore 100+ premium products across Electronics, Fashion, Home Appliances, and more. Enjoy free delivery on eligible orders and instant checkout savings.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <button
                onClick={() => onNavigate('search', { category: 'All' })}
                className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold px-6 py-2.5 rounded-md text-sm shadow transition-colors flex items-center gap-2"
              >
                Shop All Products <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onNavigate('search', { category: 'Smartphones' })}
                className="bg-gray-800/80 hover:bg-gray-800 text-white border border-gray-600 font-medium px-5 py-2.5 rounded-md text-sm transition-colors flex items-center gap-2"
              >
                Explore Smartphones
              </button>
            </div>
          </div>

          <div className="relative flex justify-center">
            <div className="relative w-full max-w-md aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl border border-gray-700/50">
              <img
                src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80"
                alt="MacBook Pro and Tech Showcase"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-6">
                <div>
                  <span className="bg-red-600 text-white font-bold text-xs px-2 py-0.5 rounded">Mega Deal</span>
                  <p className="font-bold text-lg text-white mt-1">Apple M3 Max Series</p>
                  <p className="text-xs text-gray-300">Save up to ₹25,000 with coupon SUPER50</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 space-y-8">
        {/* Active Promotional Coupons Ribbon */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm font-bold text-gray-800">
            <Tag className="w-5 h-5 text-amber-500" />
            <span>Active Promotion Coupons:</span>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="bg-amber-50 border border-amber-300 text-amber-900 font-mono font-bold px-2.5 py-1 rounded">
              SAVE10 (10% OFF)
            </span>
            <span className="bg-emerald-50 border border-emerald-300 text-emerald-900 font-mono font-bold px-2.5 py-1 rounded">
              SUPER50 (50% OFF up to ₹1,500)
            </span>
            <span className="bg-blue-50 border border-blue-300 text-blue-900 font-mono font-bold px-2.5 py-1 rounded">
              FREESHIP (Free Delivery)
            </span>
            <span className="bg-purple-50 border border-purple-300 text-purple-900 font-mono font-bold px-2.5 py-1 rounded">
              FESTIVE25 (25% OFF)
            </span>
          </div>
        </div>

        {/* Categories Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Shop by Popular Categories</h2>
            <button
              onClick={() => onNavigate('search', { category: 'All' })}
              className="text-xs font-semibold text-blue-600 hover:underline"
            >
              See all categories →
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
            {categories.slice(0, 12).map((cat) => (
              <div
                key={cat.id}
                onClick={() => onNavigate('search', { category: cat.name })}
                className="bg-white p-3.5 rounded-xl border border-gray-200 hover:border-amber-400 hover:shadow-md cursor-pointer transition-all group text-center"
              >
                <div className="w-12 h-12 bg-gray-50 rounded-full mx-auto flex items-center justify-center text-gray-600 group-hover:bg-amber-50 group-hover:text-amber-600 transition-colors mb-2">
                  <Tag className="w-5 h-5" />
                </div>
                <p className="font-semibold text-xs text-gray-800 group-hover:text-amber-700 truncate">
                  {cat.name}
                </p>
                <span className="text-[10px] text-gray-400">
                  {cat.product_count} products
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Deals of the Day */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-gray-100">
            <div className="flex items-center gap-2.5">
              <div className="bg-red-500 text-white p-1.5 rounded-md">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-xl font-extrabold text-gray-900">Deals of the Day</h2>
                <p className="text-xs text-gray-500">Unbeatable discounts up to 50% on top electronics</p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-semibold bg-red-50 text-red-700 px-3 py-1.5 rounded-full border border-red-200">
              <Clock className="w-4 h-4" />
              <span>Ends in: 08h : 42m : 19s</span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {deals.slice(0, 4).map((p) => (
              <ProductCard key={p.id} product={p} onSelect={onSelectProduct} />
            ))}
          </div>
        </div>

        {/* Consumer Value & Perks Highlight Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Truck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-900">Free Express Delivery</h4>
              <p className="text-xs text-gray-500 mt-1">Free standard delivery on orders above ₹499 across all locations.</p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <RotateCcw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-900">10-Day Easy Returns</h4>
              <p className="text-xs text-gray-500 mt-1">Hassle-free pickups and instant refunds back to your source account.</p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-900">100% Genuine Products</h4>
              <p className="text-xs text-gray-500 mt-1">Sourced directly from authorized manufacturers and verified brands.</p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
              <Headphones className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-900">24/7 Customer Care</h4>
              <p className="text-xs text-gray-500 mt-1">Dedicated help desk for order tracking, returns, and product queries.</p>
            </div>
          </div>
        </div>

        {/* Featured Flagship Products */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Featured Flagship Devices</h2>
            <button
              onClick={() => onNavigate('search', { category: 'All' })}
              className="text-xs font-semibold text-blue-600 hover:underline"
            >
              Browse complete catalog →
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {featuredProducts.slice(0, 8).map((p) => (
              <ProductCard key={p.id} product={p} onSelect={onSelectProduct} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
