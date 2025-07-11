import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSaleFromSession } from '../utils/storage';
import { format } from 'date-fns';

type SaleItem = {
  name: string;
  sku?: string;
  quantity: number;
  price: number;
};

type Sale = {
  id?: number;
  sale_id?: number;
  items: SaleItem[];
  payment_type?: string;
  created_at?: string;
  sale_timestamp?: string;
  timestamp?: string;
};

const CustomerReceipt = () => {
  const [sale, setSale] = useState<Sale | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const sessionSale = getSaleFromSession();
    if (sessionSale) {
      setSale(sessionSale as Sale);
    } else {
      navigate('/pos');
    }
  }, [navigate]);

  if (!sale) return null;

  const subtotal = sale.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  const taxRate = 0.06;
  const tax = subtotal * taxRate;
  const total = subtotal + tax;

  const handlePrint = () => window.print();

  const parsedDate = sale.created_at || sale.sale_timestamp || sale.timestamp;
  const formattedDate = parsedDate
    ? format(new Date(parsedDate), 'PPPpp')
    : 'Unknown date';

  return (
    <div className="max-w-xs mx-auto p-4 bg-white text-xs font-mono print:text-xs print:bg-white print:shadow-none">
      {/* Store Info */}
      <div className="text-center mb-2">
        <p><strong>Anchor Beverage Co.</strong></p>
        <p>123 Main Street</p>
        <p>Annapolis, MD 21401</p>
        <p>(410) 555-1234</p>
      </div>

      {/* Sale Info */}
      <p className="text-center mb-2">
        Sale #{sale.id || '—'} &bull; {formattedDate}
      </p>
      <hr className="mb-2" />

      {/* Line Items */}
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

      {/* Payment Confirmation */}
      <p className="text-center mt-3 text-green-600 font-semibold">
        Payment Accepted{sale.payment_type ? ` via ${sale.payment_type}` : ''}
      </p>

      {/* Footer */}
      <div className="text-center mt-2 text-xs">
        <p>Thank you for shopping local!</p>
        <p>All sales final unless otherwise stated. Must be 21+ to purchase alcohol.</p>
      </div>

      {/* Action Buttons (not shown on print) */}
      <div className="flex gap-2 mt-4 print:hidden">
        <button
          onClick={() => navigate('/pos')}
          className="w-full bg-gray-200 py-2 rounded"
        >
          ⬅ Back
        </button>
        <button
          onClick={handlePrint}
          className="w-full bg-blue-500 text-white py-2 rounded"
        >
          🖨️ Print
        </button>
      </div>
    </div>
  );
};

export default CustomerReceipt;
