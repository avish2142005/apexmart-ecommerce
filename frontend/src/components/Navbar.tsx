import React, { useState, useEffect, useRef } from 'react';
import {
  ShoppingCart, Search, MapPin, 
  Menu, ChevronDown, Sparkles, User, LogIn
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import api from '../api/client';

interface NavbarProps {
  onNavigate: (page: string, params?: any) => void;
  currentPage: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate, currentPage }) => {
  const { user, logout, openAuthModal } = useAuth();
  const { cart } = useCart();
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchTerm.trim().length > 1) {
      const timer = setTimeout(async () => {
        try {
          const res = await api.get('/search/suggestions', { params: { q: searchTerm } });
          setSuggestions(res.data);
          setShowSuggestions(true);
        } catch (e) {
          console.error(e);
        }
      }, 200);
      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchTerm]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    onNavigate('search', { q: searchTerm, category: selectedCategory });
  };

  const handleSelectSuggestion = (text: string) => {
    setSearchTerm(text);
    setShowSuggestions(false);
    onNavigate('search', { q: text, category: selectedCategory });
  };

  return (
    <header className="sticky top-0 z-40 shadow-md">
      {/* Top Bar */}
      <div className="bg-amazon-dark text-white px-4 py-2.5 flex items-center justify-between gap-4">
        {/* Logo */}
        <div
          onClick={() => onNavigate('home')}
          className="flex items-center gap-1.5 cursor-pointer select-none group"
        >
          <div className="bg-gradient-to-tr from-amber-500 to-orange-400 text-black font-black text-xl px-2.5 py-0.5 rounded tracking-tighter">
            APEX
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-bold text-lg tracking-tight text-white group-hover:text-amber-400 transition-colors">mart</span>
            <span className="text-[10px] text-amber-400 font-bold tracking-wider">.in</span>
          </div>
        </div>

        {/* Deliver To */}
        <div
          onClick={() => onNavigate('profile')}
          className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded hover:outline outline-1 outline-white cursor-pointer transition-all"
        >
          <MapPin className="w-5 h-5 text-gray-300" />
          <div className="text-xs">
            <p className="text-gray-400 leading-none">Deliver to</p>
            <p className="font-bold text-gray-100 truncate max-w-[130px]">
              {user?.address?.city || 'Bengaluru 560103'}
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-3xl relative" ref={searchRef}>
          <form onSubmit={handleSearchSubmit} className="flex">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-gray-200 text-gray-800 text-xs px-3 rounded-l-md border-r border-gray-300 focus:outline-none cursor-pointer"
            >
              <option value="All">All Categories</option>
              <option value="Smartphones">Smartphones</option>
              <option value="Laptops">Laptops</option>
              <option value="Audio & Headphones">Audio</option>
              <option value="Smart Watches">Wearables</option>
              <option value="Cameras & Photography">Cameras</option>
              <option value="Home Appliances">Appliances</option>
              <option value="Furniture">Furniture</option>
              <option value="Men's Fashion">Men's Fashion</option>
              <option value="Women's Fashion">Women's Fashion</option>
            </select>
            <input
              type="text"
              placeholder="Search 100+ industrial products, electronics, brands..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              className="w-full px-4 py-2 text-sm text-gray-900 focus:outline-none"
            />
            <button
              type="submit"
              className="bg-amber-400 hover:bg-amber-500 text-gray-900 px-5 rounded-r-md flex items-center justify-center transition-colors"
            >
              <Search className="w-5 h-5" />
            </button>
          </form>

          {/* Autocomplete Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-white text-gray-800 rounded-md shadow-2xl border border-gray-200 overflow-hidden z-50">
              {suggestions.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSelectSuggestion(item.text)}
                  className="px-4 py-2.5 hover:bg-gray-100 cursor-pointer flex items-center justify-between text-sm border-b border-gray-50 last:border-0"
                >
                  <div className="flex items-center gap-2">
                    <Search className="w-3.5 h-3.5 text-gray-400" />
                    <span>{item.text}</span>
                  </div>
                  <span className="text-[11px] uppercase tracking-wider text-gray-400 font-mono bg-gray-100 px-2 py-0.5 rounded">
                    {item.type}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Customer Actions */}
        <div className="flex items-center gap-3">
          {/* Returns & Orders */}
          <div
            onClick={() => onNavigate('orders')}
            className="hidden sm:flex flex-col text-left px-2 py-1 rounded hover:outline outline-1 outline-white cursor-pointer"
          >
            <span className="text-gray-400 text-xs leading-none">Returns</span>
            <span className="font-bold text-xs text-gray-100">& Orders</span>
          </div>

          {/* User Account Menu */}
          <div className="relative">
            <button
              onClick={() => {
                if (!user) {
                  openAuthModal('signin');
                } else {
                  setUserDropdownOpen(!userDropdownOpen);
                }
              }}
              className="flex items-center gap-1 text-left px-2 py-1 rounded hover:outline outline-1 outline-white cursor-pointer"
            >
              <div className="text-xs">
                <p className="text-gray-400 leading-none">
                  Hello, {user ? user.full_name.split(' ')[0] : 'Sign In'}
                </p>
                <p className="font-bold text-gray-100 flex items-center gap-0.5">
                  Account & Lists <ChevronDown className="w-3 h-3 text-gray-400" />
                </p>
              </div>
            </button>

            {userDropdownOpen && (
              <div
                className="absolute right-0 top-full mt-2 w-64 bg-white text-gray-900 rounded-xl shadow-2xl border border-gray-200 py-3 z-50"
                onMouseLeave={() => setUserDropdownOpen(false)}
              >
                {user ? (
                  <>
                    <div className="px-4 pb-3 border-b border-gray-100">
                      <p className="text-[11px] text-gray-500 font-medium">Signed in as</p>
                      <p className="font-bold text-sm text-gray-900 truncate">{user.full_name}</p>
                      <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    </div>

                    <div className="py-2 text-xs">
                      <button
                        onClick={() => { onNavigate('orders'); setUserDropdownOpen(false); }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 text-gray-700 font-medium"
                      >
                        Your Orders & Tracking
                      </button>
                      <button
                        onClick={() => { onNavigate('profile'); setUserDropdownOpen(false); }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 text-gray-700 font-medium"
                      >
                        Your Account & Addresses
                      </button>
                      <button
                        onClick={() => { onNavigate('support'); setUserDropdownOpen(false); }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 text-gray-700 font-medium"
                      >
                        Customer Service & Help
                      </button>
                    </div>

                    <div className="border-t border-gray-100 pt-2 px-2">
                      <button
                        onClick={() => { openAuthModal('signin'); setUserDropdownOpen(false); }}
                        className="w-full text-left px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-50 rounded font-medium"
                      >
                        Switch Account / Sign In
                      </button>
                      <button
                        onClick={() => { logout(); setUserDropdownOpen(false); }}
                        className="w-full text-left px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded font-bold"
                      >
                        Sign Out
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="p-4 text-center space-y-3">
                    <button
                      onClick={() => { openAuthModal('signin'); setUserDropdownOpen(false); }}
                      className="w-full bg-amber-400 hover:bg-amber-500 text-gray-900 font-bold py-2 rounded-lg text-xs shadow-sm transition-colors"
                    >
                      Sign In
                    </button>
                    <p className="text-xs text-gray-500">
                      New customer?{' '}
                      <button
                        onClick={() => { openAuthModal('signup'); setUserDropdownOpen(false); }}
                        className="text-blue-600 font-bold hover:underline"
                      >
                        Start here.
                      </button>
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Cart Icon */}
          <div
            onClick={() => onNavigate('cart')}
            className="flex items-center gap-1.5 px-3 py-1 rounded hover:outline outline-1 outline-white cursor-pointer relative"
          >
            <div className="relative">
              <ShoppingCart className="w-7 h-7 text-white" />
              <span className="absolute -top-1.5 -right-2 bg-amber-400 text-black font-black text-xs px-1.5 py-0.2 rounded-full min-w-[20px] text-center border-2 border-amazon-dark">
                {cart.item_count}
              </span>
            </div>
            <span className="hidden sm:inline font-bold text-sm text-white pt-2">Cart</span>
          </div>
        </div>
      </div>

      {/* Sub-Navbar Navigation Strip */}
      <div className="bg-amazon-light text-gray-200 px-4 py-1.5 text-xs flex items-center justify-between overflow-x-auto whitespace-nowrap">
        <div className="flex items-center gap-4">
          <button
            onClick={() => onNavigate('search', { category: 'All' })}
            className="flex items-center gap-1 font-bold text-white hover:text-amber-400"
          >
            <Menu className="w-4 h-4" /> All Products
          </button>
          <button onClick={() => onNavigate('search', { category: 'Smartphones' })} className="hover:text-amber-400">Smartphones</button>
          <button onClick={() => onNavigate('search', { category: 'Laptops' })} className="hover:text-amber-400">Laptops & PCs</button>
          <button onClick={() => onNavigate('search', { category: 'Audio & Headphones' })} className="hover:text-amber-400">Audio Gear</button>
          <button onClick={() => onNavigate('search', { category: 'Cameras & Photography' })} className="hover:text-amber-400">Cameras</button>
          <button onClick={() => onNavigate('search', { category: 'Smart Watches' })} className="hover:text-amber-400">Wearables</button>
          <button onClick={() => onNavigate('search', { category: 'Home Appliances' })} className="hover:text-amber-400">Home & Kitchen</button>
          <button onClick={() => onNavigate('search', { category: "Men's Fashion" })} className="hover:text-amber-400">Fashion</button>
          <button onClick={() => onNavigate('search', { category: 'Sports & Fitness' })} className="hover:text-amber-400">Fitness</button>
        </div>

        <div className="flex items-center gap-4 text-amber-300 font-semibold pl-4">
          <span className="flex items-center gap-1 cursor-pointer" onClick={() => onNavigate('home')}>
            <Sparkles className="w-3.5 h-3.5" /> Festive Tech Fest Deals: Up to 50% Off
          </span>
        </div>
      </div>
    </header>
  );
};
