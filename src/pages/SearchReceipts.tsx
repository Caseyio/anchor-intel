import { useState, useEffect, useRef, KeyboardEvent, ChangeEvent } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import API from '../services/api';

interface SaleItem {
  name?: string;
  sku?: string;
  price: number;
  quantity: number;
}

interface Sale {
  id: number;
  timestamp: string;
  items: SaleItem[];
  payment_type?: string;
}

const SearchReceipts = () => {
  const [saleId, setSaleId] = useState('');
  const [sale, setSale] = useState<Sale | null>(null);
  const [error, setError] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const fetchSale = async () => {
    if (!saleId) return;
    try {
      const res = await API.get(`/sales/sales/${saleId}`);
      setSale(res.data);
      setError(null);
    } catch (err) {
      setSale(null);
      setError('❌ Sale not found.');
    }
  };

  const handlePrint = () => window.print();

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === ' ') {
      e.preventDefault();
      if (sale) {
        handlePrint();
      } else if (saleId.trim()) {
        fetchSale();
      }
    } else if (e.key === 'Escape') {
      if (sale) {
        setSale(null);
        setTimeout(() => searchRef.current?.focus(), 100);
      } else if (saleId) {
        setSaleId('');
        searchRef.current?.focus();
      } else {
        navigate('/pos');
      }
    }
  };

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown as any);
    return () => document.removeEventListener('keydown', handleKeyDown as any);
  }, [saleId, sale]);

  const subtotal = sale?.items?.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  ) || 0;
  const tax = subtotal * 0.06;
  const total = subtotal + tax;
  const formattedDate = sale?.timestamp
    ? format(new Date(sale.timestamp), 'PPPpp')
    : 'Unknown date';

  return (
    <div className="max-w-md mx-auto p-4 font-mono text-sm">
      <h1 className="text-xl font-bold mb-2">🔍 Search Past Receipt</h1>

      <div className="flex items-center gap-2 mb-4">
        <input
          ref={searchRef}
          type="number"
          value={saleId}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setSaleId(e.target.value)
          }
          className="border px-2 py-1 text-sm w-24"
          placeholder="Sale ID"
        />
        <button
          onClick={fetchSale}
          className="bg-gray-200 px-3 py-1 rounded"
        >
          Search
        </button>
        <button
          onClick={() => navigate('/receipt/search-product')}
          className="bg-gray-100 px-3 py-1 rounded"
        >
          Lookup by Product
        </button>
      </div>

      {error && (
        <div className="text-red-600 text-sm mb-4">
          {error}
        </div>
      )}

      {sale && (
        <div className="bg-white p-4 text-xs print:text-xs print:bg-white print:shadow-none">
          {/* Store Info */}
          <div className="text-center mb-2">
            <p><strong>Anchor Beverage Co.</strong></p>
            <p>123 Main Street</p>
            <p>Annapolis, MD 21401</p>
            <p>(410) 555-1234</p>
          </div>

          {/* Sale Info */}
          <p className="text-center mb-2">
            <span className="font-normal">Sale #{sale.id}</span> · {formattedDate}
          </p>
          <hr className="mb-2" />

          {/* Items */}
          {sale.items.map((item, idx) => (
            <div key={idx} className="flex justify-between py-1">
              <div>
                {item.quantity} × {item.name || 'Unnamed Item'}
                <br />
                <span className="text-[10px] text-gray-600">
                  SKU: {item.sku || 'N/A'}
                </span>
              </div>
              <div>${(item.price * item.quantity).toFixed(2)}</div>
            </div>
          ))}
          <hr className="my-2" />

          {/* Totals */}
          <div className="flex justify-between">
            <span>Subtotal:</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span>Tax (6%):</span>
            <span>${tax.toFixed(2)}</span>
          </div>
          <div className="flex justify-between font-bold text-sm mt-1">
            <span>Total:</span>
            <span>${total.toFixed(2)}</span>
          </div>

          {/* Payment Info */}
          <p className="text-center mt-3">
            Payment: {sale.payment_type?.toUpperCase() || 'NOT RECORDED'}
          </p>

          {/* Footer */}
          <div className="text-center mt-2 text-xs">
            <p>Thank you for supporting local businesses!</p>
            <p>All sales final unless otherwise stated. Must be 21+ to purchase alcohol.</p>
          </div>

          {/* Buttons */}
          <div className="flex gap-2 mt-4 print:hidden">
            <button
              onClick={() => setSale(null)}
              className="bg-gray-200 py-2 px-4 rounded"
            >
              ← Back
            </button>
            <button
              onClick={handlePrint}
              className="bg-blue-500 text-white py-2 px-4 rounded"
            >
              🖨️ Print
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchReceipts;
