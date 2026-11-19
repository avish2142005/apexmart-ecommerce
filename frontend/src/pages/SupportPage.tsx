import React, { useState, useEffect } from 'react';
import { 
  HelpCircle, MessageSquare, Plus, CheckCircle, Clock, 
  Send, User, ShieldCheck, AlertCircle 
} from 'lucide-react';
import { SupportTicket } from '../types';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

interface SupportPageProps {
  initialOrderNumber?: string;
  onNavigate: (page: string, params?: any) => void;
}

export const SupportPage: React.FC<SupportPageProps> = ({ initialOrderNumber = '' }) => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [loading, setLoading] = useState(true);

  // New ticket state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [subject, setSubject] = useState('');
  const [category, setCategory] = useState('Order Issue');
  const [orderNumber, setOrderNumber] = useState(initialOrderNumber);
  const [message, setMessage] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [submitting, setSubmitting] = useState(false);

  // Reply state
  const [replyText, setReplyText] = useState('');
  const [sendingReply, setSendingReply] = useState(false);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const res = await api.get('/support/tickets', { params: { user_id: user?.id || 2 } });
      setTickets(res.data);
      if (res.data.length > 0 && !selectedTicket) {
        setSelectedTicket(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [user]);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.post('/support/tickets', {
        user_id: user?.id || 2,
        user_email: user?.email || 'john.doe@example.com',
        order_number: orderNumber || undefined,
        subject,
        category,
        message,
        priority
      });
      setShowCreateModal(false);
      setSubject('');
      setMessage('');
      fetchTickets();
      setSelectedTicket(res.data);
    } catch (err: any) {
      alert(err.message || 'Error submitting support ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTicket || !replyText.trim()) return;
    setSendingReply(true);
    try {
      const res = await api.post(`/support/tickets/${selectedTicket.ticket_id}/reply`, {
        sender_name: user?.full_name || 'Customer',
        sender_role: 'customer',
        message: replyText
      });
      setSelectedTicket(res.data);
      setReplyText('');
      // Update tickets list
      setTickets(prev => prev.map(t => t.ticket_id === res.data.ticket_id ? res.data : t));
    } catch (err: any) {
      alert(err.message || 'Error sending reply');
    } finally {
      setSendingReply(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customer Support Ticket Center</h1>
          <p className="text-xs text-gray-500 mt-0.5">Direct resolution for order complaints, refunds, and technical inquiries</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-amazon-dark hover:bg-black text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow transition-colors flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4 text-amber-400" /> Create New Support Ticket
        </button>
      </div>

      {/* Main Ticket Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Ticket List (4 cols) */}
        <div className="md:col-span-4 space-y-3 bg-white p-4 rounded-xl border border-gray-200 shadow-sm h-fit max-h-[650px] overflow-y-auto">
          <h3 className="font-bold text-xs text-gray-700 uppercase tracking-wider mb-2">Your Open Tickets</h3>
          {loading ? (
            <p className="text-xs text-gray-400 py-4 text-center">Loading tickets...</p>
          ) : tickets.length > 0 ? (
            tickets.map((t) => (
              <div
                key={t.ticket_id}
                onClick={() => setSelectedTicket(t)}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  selectedTicket?.ticket_id === t.ticket_id 
                    ? 'border-amber-500 bg-amber-50/50 ring-1 ring-amber-400' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-mono font-bold text-blue-600">{t.ticket_id}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    t.status === 'RESOLVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {t.status}
                  </span>
                </div>
                <h4 className="font-semibold text-xs text-gray-900 truncate">{t.subject}</h4>
                <p className="text-[11px] text-gray-400 mt-1">{t.category} • {new Date(t.created_at).toLocaleDateString()}</p>
              </div>
            ))
          ) : (
            <p className="text-xs text-gray-500 py-8 text-center">No support tickets found.</p>
          )}
        </div>

        {/* Ticket Detail Thread (8 cols) */}
        <div className="md:col-span-8 bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4 flex flex-col justify-between min-h-[500px]">
          {selectedTicket ? (
            <>
              {/* Ticket Top Header */}
              <div className="pb-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                      {selectedTicket.ticket_id}
                    </span>
                    <span className="text-xs text-gray-400">|</span>
                    <span className="text-xs text-gray-500">{selectedTicket.category}</span>
                    {selectedTicket.order_number && (
                      <span className="text-xs font-mono text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                        Order: {selectedTicket.order_number}
                      </span>
                    )}
                  </div>
                  <h2 className="text-lg font-bold text-gray-900 mt-1">{selectedTicket.subject}</h2>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                    Priority: {selectedTicket.priority}
                  </span>
                </div>
              </div>

              {/* Chat Thread */}
              <div className="space-y-4 flex-1 overflow-y-auto max-h-[380px] pr-2">
                {/* Initial customer message */}
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-gray-800">{user?.full_name || 'Customer'} (Original Inquiry)</span>
                    <span className="text-gray-400 text-[10px]">{new Date(selectedTicket.created_at).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-xs text-gray-700 leading-relaxed">{selectedTicket.message}</p>
                </div>

                {/* Follow-up responses */}
                {selectedTicket.responses && selectedTicket.responses.map((r, i) => (
                  <div 
                    key={i} 
                    className={`p-4 rounded-lg text-xs space-y-1 ${
                      r.sender_role === 'customer' 
                        ? 'bg-amber-50/70 border border-amber-200 ml-6' 
                        : 'bg-blue-50/70 border border-blue-200 mr-6'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <span className={r.sender_role === 'customer' ? 'text-amber-900' : 'text-blue-900'}>
                        {r.sender_name} ({r.sender_role})
                      </span>
                      <span className="text-[10px] text-gray-400">{new Date(r.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed">{r.message}</p>
                  </div>
                ))}
              </div>

              {/* Reply Form */}
              <form onSubmit={handleSendReply} className="pt-3 border-t border-gray-100 flex gap-2">
                <input
                  type="text"
                  placeholder="Type your response to support agent..."
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  className="flex-1 text-xs p-2.5 border border-gray-300 rounded focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={sendingReply || !replyText.trim()}
                  className="bg-amazon-dark hover:bg-black disabled:bg-gray-300 text-white font-bold text-xs px-4 py-2.5 rounded transition-colors flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" /> Send
                </button>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-xs">
              Select a ticket on the left to view response thread.
            </div>
          )}
        </div>
      </div>

      {/* Create Ticket Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 space-y-4">
            <h3 className="font-bold text-base text-gray-900">Create New Support Ticket</h3>
            <form onSubmit={handleCreateTicket} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Issue Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:outline-none"
                >
                  <option value="Order Issue">Order Issue (Delays, Missing)</option>
                  <option value="Payment">Payment & Billing</option>
                  <option value="Refund">Refund Status</option>
                  <option value="Return">Product Return / Replacement</option>
                  <option value="Technical">Website / Technical Error</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Related Order Number (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. ORD-20261119-XXXXXX"
                  value={orderNumber}
                  onChange={(e) => setOrderNumber(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Subject</label>
                <input
                  type="text"
                  required
                  placeholder="Brief summary of the issue"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Detailed Explanation</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Describe what occurred, any error messages, etc."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-amber-400 hover:bg-amber-500 font-bold text-gray-900 px-5 py-2 rounded shadow"
                >
                  {submitting ? 'Submitting...' : 'Create Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
