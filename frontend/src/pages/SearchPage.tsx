import React, { useState, useEffect } from 'react';
import { Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { Product } from '../types';
import { ProductCard } from '../components/ProductCard';
import api from '../api/client';

interface SearchPageProps {
  initialQuery?: string;
  initialCategory?: string;
  onSelectProduct: (product: Product) => void;
}

export const SearchPage: React.FC<SearchPageProps> = ({ 
  initialQuery = '', 
  initialCategory = 'All', 
  onSelectProduct 
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState(initialCategory);
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [sortBy, setSortBy] = useState('relevance');
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [categoriesList, setCategoriesList] = useState<any[]>([]);

  useEffect(() => {
    setQuery(initialQuery);
    setCategory(initialCategory);
    setPage(1);
  }, [initialQuery, initialCategory]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await api.get('/catalog/categories');
        setCategoriesList(res.data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchCategories();
  }, []);

  const executeSearch = async () => {
    setLoading(true);
    try {
      const params: any = {
        q: query,
        page,
        limit: 16,
        sort_by: sortBy
      };
      if (category && category !== 'All') params.category = category;
      if (minPrice) params.min_price = minPrice;
      if (maxPrice) params.max_price = maxPrice;

      const res = await api.get('/search/query', { params });
      setProducts(res.data.results);
      setTotal(res.data.total);
      setTotalPages(res.data.total_pages || 1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [query, category, minPrice, maxPrice, sortBy, page]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Top Search Controls Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {query ? `Search results for "${query}"` : category !== 'All' ? `${category} Catalog` : 'Complete Product Catalog'}
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">Showing {products.length} of {total} products</p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-gray-500 font-medium">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-gray-50 border border-gray-300 rounded px-3 py-1.5 font-medium text-gray-800 focus:outline-none"
          >
            <option value="relevance">Featured & Relevant</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="rating">Customer Rating</option>
            <option value="newest">Newest Arrivals</option>
          </select>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Filter Sidebar (3 cols) */}
        <div className="md:col-span-3 space-y-6 bg-white p-5 rounded-xl border border-gray-200 shadow-sm h-fit">
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <h3 className="font-bold text-sm text-gray-800 flex items-center gap-2">
              <Filter className="w-4 h-4 text-amber-500" /> Filters
            </h3>
            {(category !== 'All' || minPrice || maxPrice) && (
              <button
                onClick={() => {
                  setCategory('All');
                  setMinPrice(undefined);
                  setMaxPrice(undefined);
                }}
                className="text-xs text-red-600 hover:underline"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Category Filter */}
          <div>
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Category</h4>
            <div className="space-y-1 max-h-56 overflow-y-auto text-xs pr-1">
              <div
                onClick={() => setCategory('All')}
                className={`px-2 py-1.5 rounded cursor-pointer transition-colors ${
                  category === 'All' ? 'bg-amber-100 text-amber-900 font-bold' : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                All Categories
              </div>
              {categoriesList.map((cat, idx) => (
                <div
                  key={idx}
                  onClick={() => setCategory(cat.name)}
                  className={`px-2 py-1.5 rounded cursor-pointer transition-colors flex justify-between items-center ${
                    category === cat.name ? 'bg-amber-100 text-amber-900 font-bold' : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <span className="truncate">{cat.name}</span>
                  <span className="text-[10px] text-gray-400 font-mono">({cat.count})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Price Range Filter */}
          <div className="pt-2 border-t border-gray-100">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Price Range (₹)</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <input
                type="number"
                placeholder="Min ₹"
                value={minPrice || ''}
                onChange={(e) => setMinPrice(e.target.value ? Number(e.target.value) : undefined)}
                className="p-2 border border-gray-300 rounded focus:outline-none"
              />
              <input
                type="number"
                placeholder="Max ₹"
                value={maxPrice || ''}
                onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : undefined)}
                className="p-2 border border-gray-300 rounded focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Right Product Grid (9 cols) */}
        <div className="md:col-span-9 space-y-6">
          {loading ? (
            <div className="bg-white p-12 rounded-xl border border-gray-200 text-center text-gray-500">
              Loading matching catalog items...
            </div>
          ) : products.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((p) => (
                  <ProductCard key={p.id} product={p} onSelect={onSelectProduct} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-4">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-2 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50 text-xs font-semibold"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs font-semibold text-gray-700 px-3">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="p-2 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50 text-xs font-semibold"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white p-12 rounded-xl border border-gray-200 text-center space-y-3">
              <Search className="w-12 h-12 text-gray-300 mx-auto" />
              <h3 className="text-base font-bold text-gray-800">No products found</h3>
              <p className="text-xs text-gray-500">Try adjusting your keyword, category, or price range filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
