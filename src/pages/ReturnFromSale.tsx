import { useEffect, useState, useRef, ChangeEvent, KeyboardEvent } from 'react';
import API from '../services/api';
import { useNavigate } from 'react-router-dom';

interface Product {
  id: number;
  name: string;
  sku: string;
  price: string | number;
}

interface ReturnItem {
  product_id: number;
  name: string;
  sku: string;
  quantity: number;
  price: number;
  restock: boolean;
}

const reasons = ['Damaged', 'Expired', 'Customer Changed Mind', 'Other'];

const ReturnFromSale = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [returnItems, setReturnItems] = useState<ReturnItem[]>([]);
  const [saleId, setSaleId] = useState('');
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const loadButtonRef = useRef<HTMLButtonElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);

  const simulateButtonPress = (ref: React.RefObject<HTMLButtonElement | null>) => {
    if (ref.current) {
      ref.current.classList.add('scale-95');
      setTimeout(() => {
        ref.current?.classList.remove('scale-95');
        ref.current?.click();
      }, 100);
    }
  };

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await API.get('/products/products');
        setProducts(res.data);
      } catch (err) {
        console.error('❌ Failed to fetch products:', err);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key;

      if (key === 'Escape') {
        if (returnItems.length > 0) {
          const updated = [...returnItems];
          updated.pop();
          setReturnItems(updated);
        } else {
          navigate('/pos');
        }
        setError('');
        setMessage('');
      }

      if ((key === ' ' || key === 'Enter') && saleId && returnItems.length > 0 && reason) {
        e.preventDefault();
        simulateButtonPress(submitButtonRef);
      }
    };

    const listener = handleKeyDown as unknown as EventListener;
    window.addEventListener('keydown', listener);
    return () => window.removeEventListener('keydown', listener);
  }, [returnItems, reason, saleId, navigate]);

  const handleFetchSale = async () => {
    if (!saleId) return;

    try {
      const res = await API.get(`/sales/sales/${saleId}`);
      const items = res.data.items || [];

      const enrichedItems: ReturnItem[] = items.map((item: any) => {
        const product = products.find((p) => p.id === item.product_id);
        return {
          product_id: item.product_id,
          name: product?.name || `Product #${item.product_id}`,
          sku: product?.sku || '',
          quantity: item.quantity,
          price: item.price,
          restock: true,
        };
      });

      if (enrichedItems.length === 0) {
        alert('❌ No returnable items found for this sale.');
      }

      setReturnItems(enrichedItems);
    } catch (err) {
      console.error('❌ Failed to fetch sale:', err);
      alert('❌ Sale not found.');
      setReturnItems([]);
    }
  };

  const handleQuantityChange = (index: number, newQuantity: number) => {
    const updated = [...returnItems];
    updated[index].quantity = newQuantity;
    setReturnItems(updated);
  };

  const handleRestockToggle = (index: number, checked: boolean) => {
    const updated = [...returnItems];
    updated[index].restock = checked;
    setReturnItems(updated);
  };

  const handleDeleteItem = (index: number) => {
    const updated = [...returnItems];
    updated.splice(index, 1);
    setReturnItems(updated);
  };

  const handleSubmit = async () => {
    setError('');
    setMessage('');

    if (!saleId || returnItems.length === 0 || !reason) {
      setError('⚠️ Please fill all required fields before submitting.');
      return;
    }

    const payload = {
      sale_id: parseInt(saleId),
      returns: returnItems.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        restock: item.restock,
        reason,
        notes: reason === 'Other' ? notes : '',
      })),
    };

    try {
      await API.post('/returns/', payload);
      setMessage('✅ Return processed');
      setTimeout(() => navigate('/pos'), 4000);
      setReturnItems([]);
      setSaleId('');
      setReason('');
      setNotes('');
    } catch (err: any) {
      console.error('❌ Return failed:', err);
      const detail = err?.response?.data?.detail;
      setError(detail ? `❌ ${detail}` : '❌ Failed to process return. Please try again.');
    }
  };

  const taxRate = 0.06;
  const subtotal = returnItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * taxRate;
  const total = subtotal + tax;

  return (
    <div className="p-4 max-w-2xl mx-auto font-mono">
      <button
        onClick={() => navigate('/pos')}
        className="mb-2 text-sm text-blue-700 hover:underline"
      >
        ← Back to Checkout
      </button>

      <div className="mb-4 flex gap-2">
        <button
          onClick={() => navigate('/return-manual')}
          className="bg-gray-300 px-3 py-1 rounded hover:bg-gray-400"
        >
          Manual Return (Search)
        </button>
      </div>

      <h1 className="text-2xl font-bold mb-4">Return by Sale ID</h1>

      <div className="mb-4">
        <label className="block font-semibold">Sale ID</label>
        <input
          type="number"
          value={saleId}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setSaleId(e.target.value)}
          className="border p-2 rounded w-full"
          placeholder="Enter Sale Number"
        />
        <button
          ref={loadButtonRef}
          onClick={handleFetchSale}
          className="mt-2 bg-blue-600 text-white px-4 py-1 rounded active:scale-95 transition-transform"
        >
          Load Sale Items
        </button>
      </div>

      {returnItems.length > 0 && (
        <div className="bg-gray-50 p-3 border rounded mb-4">
          <h2 className="font-semibold mb-2">Items to Return:</h2>
          {returnItems.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between mb-3">
              <div>
                <p className="text-sm">
                  {item.name} ({item.sku || `ID#${item.product_id}`})
                </p>
                <div className="flex gap-2 items-center mt-1">
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) =>
                      handleQuantityChange(idx, parseInt(e.target.value) || 1)
                    }
                    className="border p-1 w-20"
                  />
                  <label className="text-sm">
                    <input
                      type="checkbox"
                      checked={item.restock}
                      onChange={(e) => handleRestockToggle(idx, e.target.checked)}
                      className="mr-1"
                    />
                    Restock
                  </label>
                </div>
              </div>
              <div className="text-right">
                <p>${(item.price * item.quantity).toFixed(2)}</p>
                <button
                  onClick={() => handleDeleteItem(idx)}
                  className="text-red-500 text-xs mt-1"
                >
                  ✖ Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {returnItems.length > 0 && (
        <>
          <div className="mb-4 text-right font-semibold">
            <p>Subtotal: ${subtotal.toFixed(2)}</p>
            <p>Tax (6%): ${tax.toFixed(2)}</p>
            <p className="text-lg font-bold">Total: ${total.toFixed(2)}</p>
          </div>

          <div className="mb-4">
            <label className="block font-semibold">Reason</label>
            <select
              value={reason}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => setReason(e.target.value)}
              className="border p-2 rounded w-full"
            >
              <option value="">-- Select --</option>
              {reasons.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {reason === 'Other' && (
            <div className="mb-4">
              <label className="block font-semibold">Notes</label>
              <textarea
                value={notes}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setNotes(e.target.value)}
                className="border p-2 rounded w-full"
                placeholder="Explain reason"
              />
            </div>
          )}

          {error && <p className="text-red-600 font-semibold mb-2">{error}</p>}

          <button
            ref={submitButtonRef}
            onClick={handleSubmit}
            className="bg-red-600 text-white px-4 py-2 rounded w-full active:scale-95 transition-transform"
          >
            Submit Return
          </button>
        </>
      )}

      {message && (
        <p className="mt-4 text-center font-semibold text-green-600">{message}</p>
      )}
    </div>
  );
};

export default ReturnFromSale;