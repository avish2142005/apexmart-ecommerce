import React from 'react';
import { Star, ShoppingCart, Truck, ShieldCheck } from 'lucide-react';
import { Product } from '../types';
import { useCart } from '../context/CartContext';

interface ProductCardProps {
  product: Product;
  onSelect: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onSelect }) => {
  const { addToCart } = useCart();

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-200 flex flex-col justify-between overflow-hidden group">
      <div className="p-4 cursor-pointer" onClick={() => onSelect(product)}>
        {/* Image Container with Badges */}
        <div className="relative aspect-square w-full mb-3 bg-gray-50 rounded-md overflow-hidden flex items-center justify-center p-2">
          <img
            src={product.image_url}
            alt={product.name}
            className="object-contain h-full w-full group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          {product.discount_pct > 0 && (
            <span className="absolute top-2 left-2 bg-red-600 text-white text-[11px] font-black px-2 py-0.5 rounded shadow">
              {product.discount_pct}% OFF
            </span>
          )}
          {product.is_featured && (
            <span className="absolute top-2 right-2 bg-amber-500 text-black text-[10px] font-bold px-1.5 py-0.5 rounded shadow flex items-center gap-0.5">
              Top Choice
            </span>
          )}
        </div>

        {/* Brand & Category */}
        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span className="font-semibold text-gray-600 uppercase tracking-wider">{product.brand}</span>
          <span className="text-gray-400">{product.category}</span>
        </div>

        {/* Product Title */}
        <h3 className="font-medium text-gray-900 text-sm line-clamp-2 hover:text-amber-600 transition-colors mb-1.5 min-h-[40px]">
          {product.name}
        </h3>

        {/* Rating */}
        <div className="flex items-center gap-1.5 mb-2">
          <div className="flex items-center text-amber-500">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-3.5 h-3.5 ${
                  i < Math.floor(product.rating) ? 'fill-current' : 'text-gray-300'
                }`}
              />
            ))}
          </div>
          <span className="text-xs font-bold text-gray-700">{product.rating}</span>
          <span className="text-[11px] text-gray-400">({product.rating_count})</span>
        </div>

        {/* Price Section */}
        <div className="mb-2">
          <div className="flex items-baseline gap-2">
            <span className="text-xs font-semibold text-gray-500">₹</span>
            <span className="text-xl font-bold text-gray-900">
              {product.discounted_price.toLocaleString('en-IN')}
            </span>
            {product.discount_pct > 0 && (
              <span className="text-xs text-gray-400 line-through">
                ₹{product.price.toLocaleString('en-IN')}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1 text-[11px] text-emerald-600 font-medium mt-0.5">
            <Truck className="w-3.5 h-3.5" />
            <span>FREE Next-Day Delivery</span>
          </div>
        </div>

        {/* Stock Status Indicator */}
        <div className="text-[11px] mb-3">
          {product.stock > 10 ? (
            <span className="text-emerald-600 font-medium">In Stock</span>
          ) : product.stock > 0 ? (
            <span className="text-orange-600 font-semibold">Only {product.stock} left in stock!</span>
          ) : (
            <span className="text-red-500 font-semibold">Temporarily Out of Stock</span>
          )}
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className="px-4 pb-4 pt-1 border-t border-gray-100 bg-gray-50/50">
        <button
          onClick={(e) => {
            e.stopPropagation();
            addToCart(product.id, 1);
          }}
          disabled={!product.in_stock}
          className="w-full bg-amber-400 hover:bg-amber-500 disabled:bg-gray-300 disabled:cursor-not-allowed text-gray-900 font-semibold text-xs py-2 px-3 rounded-md shadow-sm flex items-center justify-center gap-1.5 transition-colors"
        >
          <ShoppingCart className="w-3.5 h-3.5" />
          {product.in_stock ? 'Add to Cart' : 'Out of Stock'}
        </button>
      </div>
    </div>
  );
};
