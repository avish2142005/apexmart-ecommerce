import React, { useState, useEffect } from 'react';
import { 
  Star, Truck, ShieldCheck, RotateCcw, ShoppingCart, 
  Check, Heart, Share2, ArrowLeft, ThumbsUp, AlertCircle 
} from 'lucide-react';
import { Product, Review } from '../types';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

interface ProductDetailsPageProps {
  product: Product;
  onNavigate: (page: string, params?: any) => void;
  onSelectProduct: (product: Product) => void;
}

export const ProductDetailsPage: React.FC<ProductDetailsPageProps> = ({ 
  product, 
  onNavigate,
  onSelectProduct 
}) => {
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [selectedImage, setSelectedImage] = useState(product.image_url);
  const [quantity, setQuantity] = useState(1);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [reviewsData, setReviewsData] = useState<{
    reviews: Review[];
    average_rating: number;
    total_reviews: number;
    rating_breakdown: any;
  }>({ reviews: [], average_rating: product.rating, total_reviews: product.rating_count, rating_breakdown: {} });
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewTitle, setReviewTitle] = useState('');
  const [reviewComment, setReviewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  useEffect(() => {
    setSelectedImage(product.image_url);
    const loadDetails = async () => {
      try {
        const [recRes, revRes] = await Promise.all([
          api.get(`/catalog/products/${product.id}/recommendations`),
          api.get(`/reviews/product/${product.id}`)
        ]);
        setRecommendations(recRes.data);
        setReviewsData(revRes.data);
      } catch (e) {
        console.error(e);
      }
    };
    loadDetails();
  }, [product]);

  const handleBuyNow = async () => {
    await addToCart(product.id, quantity);
    onNavigate('checkout');
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingReview(true);
    try {
      await api.post('/reviews/', {
        product_id: product.id,
        user_id: user?.id || 2,
        user_name: user?.full_name || 'Verified Customer',
        rating: reviewRating,
        title: reviewTitle,
        comment: reviewComment
      });
      // Refresh reviews
      const revRes = await api.get(`/reviews/product/${product.id}`);
      setReviewsData(revRes.data);
      setShowReviewForm(false);
      setReviewTitle('');
      setReviewComment('');
    } catch (err: any) {
      alert(err.message || 'Error submitting review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleVoteHelpful = async (reviewId: number) => {
    try {
      await api.post(`/reviews/${reviewId}/vote`);
      // Local update
      setReviewsData(prev => ({
        ...prev,
        reviews: prev.reviews.map(r => r.id === reviewId ? { ...r, helpful_votes: r.helpful_votes + 1 } : r)
      }));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-8">
      {/* Back button & Breadcrumbs */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <button 
          onClick={() => onNavigate('home')} 
          className="hover:text-amber-600 flex items-center gap-1 font-medium"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Catalog
        </button>
        <span>/</span>
        <span>{product.category}</span>
        <span>/</span>
        <span className="text-gray-800 font-semibold truncate max-w-xs">{product.name}</span>
      </div>

      {/* Main Product Showcase Box */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left: Images Column (5 cols) */}
        <div className="md:col-span-5 space-y-4">
          <div className="aspect-square bg-gray-50 rounded-lg overflow-hidden border border-gray-100 flex items-center justify-center p-4">
            <img 
              src={selectedImage} 
              alt={product.name} 
              className="object-contain h-full w-full max-h-[420px]"
            />
          </div>

          {/* Thumbnails */}
          {product.images && product.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {product.images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(img)}
                  className={`w-16 h-16 rounded border p-1 shrink-0 ${
                    selectedImage === img ? 'border-amber-500 ring-2 ring-amber-200' : 'border-gray-200'
                  }`}
                >
                  <img src={img} alt="" className="w-full h-full object-contain" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Middle: Details & Specs (4 cols) */}
        <div className="md:col-span-4 space-y-4">
          <div>
            <span className="text-xs uppercase tracking-wider font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
              {product.brand}
            </span>
            <h1 className="text-xl md:text-2xl font-bold text-gray-900 mt-1 leading-snug">
              {product.name}
            </h1>
          </div>

          {/* Rating Summary */}
          <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
            <div className="flex items-center text-amber-500">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(product.rating) ? 'fill-current' : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm font-bold text-gray-800">{product.rating}</span>
            <span className="text-xs text-blue-600 hover:underline cursor-pointer">
              {reviewsData.total_reviews} ratings & reviews
            </span>
          </div>

          {/* Pricing */}
          <div className="border-b border-gray-100 pb-4">
            <div className="flex items-baseline gap-2">
              <span className="text-red-600 font-bold text-lg">-{product.discount_pct}%</span>
              <span className="text-3xl font-extrabold text-gray-900">
                ₹{product.discounted_price.toLocaleString('en-IN')}
              </span>
            </div>
            {product.discount_pct > 0 && (
              <p className="text-xs text-gray-400 mt-0.5">
                M.R.P.: <span className="line-through">₹{product.price.toLocaleString('en-IN')}</span>
              </p>
            )}
            <p className="text-xs text-gray-500 mt-1">Inclusive of all applicable GST taxes.</p>
          </div>

          {/* Key Specifications */}
          {product.specs && Object.keys(product.specs).length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">Specifications</h3>
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-100 grid grid-cols-2 gap-2 text-xs">
                {Object.entries(product.specs).map(([k, v]) => (
                  <div key={k}>
                    <span className="text-gray-500 block">{k}</span>
                    <span className="font-semibold text-gray-800">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          <div>
            <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Description</h3>
            <p className="text-xs text-gray-600 leading-relaxed">{product.description}</p>
          </div>
        </div>

        {/* Right: Buy Box (3 cols) */}
        <div className="md:col-span-3">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-4 shadow-sm sticky top-24">
            <div>
              <span className="text-2xl font-bold text-gray-900">
                ₹{product.discounted_price.toLocaleString('en-IN')}
              </span>
              <p className="text-xs text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                <Truck className="w-4 h-4" /> FREE Next-Day Delivery
              </p>
            </div>

            {/* In stock badge */}
            <div>
              {product.stock > 10 ? (
                <span className="text-emerald-700 font-bold text-sm">In Stock.</span>
              ) : product.stock > 0 ? (
                <span className="text-orange-600 font-bold text-sm">Only {product.stock} left in stock!</span>
              ) : (
                <span className="text-red-600 font-bold text-sm">Currently unavailable.</span>
              )}
              <p className="text-[11px] text-gray-500 mt-0.5">Dispatches from Central Hub BLR-01</p>
            </div>

            {/* Quantity Selector */}
            {product.in_stock && (
              <div className="flex items-center justify-between text-xs font-semibold">
                <span>Quantity:</span>
                <select
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  className="bg-white border border-gray-300 rounded px-2.5 py-1 text-xs focus:outline-none"
                >
                  {[...Array(Math.min(10, product.stock))].map((_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-2">
              <button
                onClick={() => addToCart(product.id, quantity)}
                disabled={!product.in_stock}
                className="w-full bg-amber-400 hover:bg-amber-500 disabled:bg-gray-300 text-gray-900 font-bold text-xs py-2.5 rounded-lg shadow transition-colors flex items-center justify-center gap-2"
              >
                <ShoppingCart className="w-4 h-4" /> Add to Cart
              </button>
              <button
                onClick={handleBuyNow}
                disabled={!product.in_stock}
                className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 text-white font-bold text-xs py-2.5 rounded-lg shadow transition-colors"
              >
                Buy Now
              </button>
            </div>

            {/* Security info */}
            <div className="text-[11px] text-gray-500 space-y-1.5 pt-2 border-t border-gray-200">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-gray-400" />
                <span>Secure distributed transaction</span>
              </div>
              <div className="flex items-center gap-1.5">
                <RotateCcw className="w-4 h-4 text-gray-400" />
                <span>10-Day Return & Replacement</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Reviews Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-100 pb-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Customer Reviews & Ratings</h2>
            <p className="text-xs text-gray-500">Verified buyer ratings and authentic feedback</p>
          </div>
          <button
            onClick={() => setShowReviewForm(!showReviewForm)}
            className="bg-gray-900 hover:bg-gray-800 text-white text-xs font-semibold px-4 py-2 rounded-md transition-colors"
          >
            {showReviewForm ? 'Cancel Review' : 'Write a Customer Review'}
          </button>
        </div>

        {/* Write Review Form */}
        {showReviewForm && (
          <form onSubmit={handleReviewSubmit} className="bg-amber-50/50 border border-amber-200 rounded-lg p-5 space-y-3">
            <h3 className="font-bold text-sm text-gray-800">Submit Your Feedback</h3>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Overall Rating</label>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    onClick={() => setReviewRating(star)}
                    className={`w-6 h-6 cursor-pointer ${
                      star <= reviewRating ? 'fill-amber-400 text-amber-400' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Review Headline</label>
              <input
                type="text"
                required
                placeholder="What's most important to know?"
                value={reviewTitle}
                onChange={(e) => setReviewTitle(e.target.value)}
                className="w-full text-xs p-2.5 rounded border border-gray-300 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Detailed Review</label>
              <textarea
                rows={3}
                required
                placeholder="Write your review here..."
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                className="w-full text-xs p-2.5 rounded border border-gray-300 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={submittingReview}
              className="bg-amber-500 hover:bg-amber-600 text-black font-bold text-xs px-5 py-2 rounded shadow transition-colors"
            >
              {submittingReview ? 'Submitting...' : 'Submit Review'}
            </button>
          </form>
        )}

        {/* Reviews List */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Breakdown summary (4 cols) */}
          <div className="md:col-span-4 space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-gray-900">{reviewsData.average_rating}</span>
              <span className="text-sm text-gray-500">out of 5</span>
            </div>
            <div className="flex items-center text-amber-500">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(reviewsData.average_rating) ? 'fill-current' : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <p className="text-xs text-gray-500">{reviewsData.total_reviews} global customer ratings</p>
          </div>

          {/* Individual Reviews (8 cols) */}
          <div className="md:col-span-8 space-y-4">
            {reviewsData.reviews && reviewsData.reviews.length > 0 ? (
              reviewsData.reviews.map((rev) => (
                <div key={rev.id} className="border-b border-gray-100 pb-4 last:border-0 space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-gray-800">{rev.user_name}</span>
                    <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-1.5 py-0.5 rounded">
                      Verified Purchase
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center text-amber-500">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${
                            i < rev.rating ? 'fill-current' : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-bold text-gray-900">{rev.title}</span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{rev.comment}</p>
                  <div className="flex items-center gap-3 pt-1">
                    <button
                      onClick={() => handleVoteHelpful(rev.id)}
                      className="text-[11px] text-gray-500 hover:text-gray-800 flex items-center gap-1 border border-gray-200 px-2 py-0.5 rounded"
                    >
                      <ThumbsUp className="w-3 h-3" /> Helpful ({rev.helpful_votes})
                    </button>
                    <span className="text-[11px] text-gray-400">
                      {new Date(rev.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500">No customer reviews yet. Be the first to review this product!</p>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Products Carousel */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-gray-900">Customers who viewed this also bought</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {recommendations.slice(0, 4).map((p) => (
              <div 
                key={p.id} 
                onClick={() => onSelectProduct(p)} 
                className="bg-white p-3 rounded-lg border border-gray-200 hover:shadow-md cursor-pointer transition-all flex flex-col justify-between"
              >
                <div className="aspect-square bg-gray-50 rounded mb-2 overflow-hidden flex items-center justify-center p-2">
                  <img src={p.image_url} alt="" className="object-contain h-full w-full" />
                </div>
                <h4 className="font-medium text-xs text-gray-800 line-clamp-2">{p.name}</h4>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="font-bold text-sm text-gray-900">₹{p.discounted_price.toLocaleString('en-IN')}</span>
                  {p.discount_pct > 0 && (
                    <span className="text-[10px] text-gray-400 line-through">₹{p.price.toLocaleString('en-IN')}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
