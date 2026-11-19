import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';
import { HomePage } from './pages/HomePage';
import { SearchPage } from './pages/SearchPage';
import { ProductDetailsPage } from './pages/ProductDetailsPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderConfirmationPage } from './pages/OrderConfirmationPage';
import { OrdersPage } from './pages/OrdersPage';
import { OrderTrackingPage } from './pages/OrderTrackingPage';
import { SupportPage } from './pages/SupportPage';
import { ProfilePage } from './pages/ProfilePage';
import { Product, SagaCheckoutResult } from './types';

const AppContent: React.FC = () => {
  const { isAuthModalOpen, authModalMode, closeAuthModal } = useAuth();
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [searchParams, setSearchParams] = useState<{ q?: string; category?: string }>({});
  const [trackingNumber, setTrackingNumber] = useState<string>('');
  const [orderNumberForSupport, setOrderNumberForSupport] = useState<string>('');
  const [checkoutCoupon, setCheckoutCoupon] = useState<string>('');
  const [orderResult, setOrderResult] = useState<SagaCheckoutResult | undefined>();

  const navigate = (page: string, params?: any) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (page === 'search') {
      setSearchParams({ q: params?.q || '', category: params?.category || 'All' });
    } else if (page === 'track') {
      setTrackingNumber(params?.trackingNumber || '');
    } else if (page === 'support') {
      setOrderNumberForSupport(params?.orderNumber || '');
    } else if (page === 'checkout') {
      setCheckoutCoupon(params?.coupon_code || '');
    } else if (page === 'order-confirmation') {
      setOrderResult(params?.result);
    }
    setCurrentPage(page);
  };

  const handleSelectProduct = (product: Product) => {
    setSelectedProduct(product);
    navigate('product-detail');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#eaeded]">
      <Navbar onNavigate={navigate} currentPage={currentPage} />

      <main className="flex-1">
        {currentPage === 'home' && (
          <HomePage onNavigate={navigate} onSelectProduct={handleSelectProduct} />
        )}

        {currentPage === 'search' && (
          <SearchPage 
            initialQuery={searchParams.q} 
            initialCategory={searchParams.category} 
            onSelectProduct={handleSelectProduct} 
          />
        )}

        {currentPage === 'product-detail' && selectedProduct && (
          <ProductDetailsPage
            product={selectedProduct}
            onNavigate={navigate}
            onSelectProduct={handleSelectProduct}
          />
        )}

        {currentPage === 'cart' && (
          <CartPage onNavigate={navigate} />
        )}

        {currentPage === 'checkout' && (
          <CheckoutPage onNavigate={navigate} initialCoupon={checkoutCoupon} />
        )}

        {currentPage === 'order-confirmation' && (
          <OrderConfirmationPage result={orderResult} onNavigate={navigate} />
        )}

        {currentPage === 'orders' && (
          <OrdersPage onNavigate={navigate} />
        )}

        {currentPage === 'track' && (
          <OrderTrackingPage trackingQuery={trackingNumber} onNavigate={navigate} />
        )}

        {currentPage === 'support' && (
          <SupportPage initialOrderNumber={orderNumberForSupport} onNavigate={navigate} />
        )}

        {currentPage === 'profile' && (
          <ProfilePage onNavigate={navigate} />
        )}
      </main>

      <Footer />

      {/* Global Sign In / Sign Up Modal with Live Criteria */}
      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={closeAuthModal} 
        initialMode={authModalMode} 
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <CartProvider>
        <AppContent />
      </CartProvider>
    </AuthProvider>
  );
};

export default App;
