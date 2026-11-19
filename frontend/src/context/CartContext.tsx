import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';
import { CartItem, CartData } from '../types';
import { useAuth } from './AuthContext';

interface CartContextType {
  cart: CartData;
  loading: boolean;
  addToCart: (productId: number, quantity?: number) => Promise<void>;
  updateQuantity: (productId: number, quantity: number) => Promise<void>;
  removeFromCart: (productId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [cart, setCart] = useState<CartData>({ items: [], item_count: 0, subtotal: 0.0 });
  const [loading, setLoading] = useState<boolean>(false);

  const getSessionId = () => {
    let sid = localStorage.getItem('cart_session_id');
    if (!sid) {
      sid = 'session-' + Math.random().toString(36).substring(2, 9);
      localStorage.setItem('cart_session_id', sid);
    }
    return sid;
  };

  const refreshCart = async () => {
    try {
      const params = user ? { user_id: user.id } : { session_id: getSessionId() };
      const res = await api.get('/cart/', { params });
      setCart(res.data);
    } catch (err) {
      console.error('Failed to load cart', err);
    }
  };

  useEffect(() => {
    refreshCart();
  }, [user]);

  const addToCart = async (productId: number, quantity: number = 1) => {
    setLoading(true);
    try {
      const payload = {
        product_id: productId,
        quantity,
        user_id: user?.id,
        session_id: getSessionId()
      };
      const res = await api.post('/cart/add', payload);
      setCart(res.data);
    } catch (err: any) {
      alert(err.message || "Failed to add to cart");
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId: number, quantity: number) => {
    setLoading(true);
    try {
      const payload = {
        product_id: productId,
        quantity,
        user_id: user?.id,
        session_id: getSessionId()
      };
      const res = await api.put('/cart/update', payload);
      setCart(res.data);
    } catch (err: any) {
      alert(err.message || "Failed to update quantity");
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (productId: number) => {
    setLoading(true);
    try {
      const params = user ? { user_id: user.id } : { session_id: getSessionId() };
      const res = await api.delete(`/cart/remove/${productId}`, { params });
      setCart(res.data);
    } catch (err: any) {
      alert(err.message || "Failed to remove item");
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    setLoading(true);
    try {
      const params = user ? { user_id: user.id } : { session_id: getSessionId() };
      await api.delete('/cart/clear', { params });
      setCart({ items: [], item_count: 0, subtotal: 0.0 });
    } catch (err: any) {
      console.error('Failed to clear cart', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <CartContext.Provider value={{ cart, loading, addToCart, updateQuantity, removeFromCart, clearCart, refreshCart }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) throw new Error('useCart must be used within a CartProvider');
  return context;
};
