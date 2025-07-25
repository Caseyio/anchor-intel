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

const ReturnManual = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState('');
  const [returnItems, setReturnItems] = useState<ReturnItem[]>([]);
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);
  const navigate = useNavigate();

  const simulateButtonPress = (ref: HTMLButtonElement | null) => {
    if (ref) {
      ref.classList.add('scale-95');
      setTimeout(() => {
        ref.classList.remove('scale-95');
        ref.click();
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
    searchRef.current?.focus();

    const handleKeyDown = (event: globalThis.KeyboardEvent): void => {
      if (event.key === 'Escape') {
        if (returnItems.length > 0) {
          const updated = [...returnItems];
          updated.pop();
          setReturnItems(updated);
        } else {
          navigate('/pos');
        }
        setError('');
        setMessage('');
      } else if ((event.key === ' ' || event.key === 'Enter') && returnItems.length > 0 && reason) {
        event.preventDefault();
        simulateButtonPress(submitButtonRef.current);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [returnItems, reason, navigate]);

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

    if (returnItems.length === 0 || !reason) {
      setError('⚠️ Please fill all required fields before submitting.');
      return;
    }

    const payload = {
      returns: returnItems.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        restock: item.restock,
        reason,
        notes: reason === 'Other' ? notes : '',
      })),
    };

    try {
      await API.post('/returns', payload);
      setMessage('✅ Return processed');
      setTimeout(() => navigate('/pos'), 4000);
      setReturnItems([]);
      setReason('');
      setNotes('');
      setSearch('');
    } catch (err: any) {
      console.error('❌ Return failed:', err);
      const detail = err?.response?.data?.detail;
      setError(detail ? `❌ ${detail}` : '❌ Failed to process return. Please try again.');
    }
  };

  const filtered = search
    ? products.filter((p) =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.sku.toLowerCase().includes(search.toLowerCase())
      )
    : [];

  const taxRate = 0.06;
  const subtotal = returnItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * taxRate;
  const total = subtotal + tax;

  return (
    <div className="p-4 max-w-2xl mx-auto font-mono">
      <h1 className="text-2xl font-bold mb-4">Return Product</h1>

      <input
        type="text"
        ref={searchRef}
        placeholder="Scan or search product..."
        value={search}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
        className="border p-2 rounded w-full mb-2"
      />

      {filtered.length > 0 && (
        <div className="bg-white shadow border rounded mb-4">
          {filtered.slice(0, 5).map((product) => (
            <div
              key={product.id}
              onClick={() => {
                const exists = returnItems.find((item) => item.product_id === product.id);
                if (!exists) {
                  const newItem: ReturnItem = {
                    product_id: product.id,
                    name: product.name,
                    sku: product.sku,
                    quantity: 1,
                    price: parseFloat(product.price as string),
                    restock: true,
                  };
                  setReturnItems((prev) => [...prev, newItem]);
                }
                setSearch('');
                searchRef.current?.focus();
              }}
              className="p-2 hover:bg-gray-100 cursor-pointer flex justify-between"
            >
              <span>{product.name}</span>
              <span>${parseFloat(product.price as string).toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}

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
                    onChange={(e: ChangeEvent<HTMLInputElement>) =>
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
              <option value="">Select reason</option>
              {reasons.map((r) => (
                <option key={r} value={r}>{r}</option>
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
          {message && <p className="text-green-600 font-semibold mb-2">{message}</p>}

          <button
            ref={submitButtonRef}
            onClick={handleSubmit}
            className="bg-red-600 text-white px-4 py-2 rounded w-full transition-transform active:scale-95"
          >
            Process Return
          </button>

          <button
            onClick={() => navigate('/pos')}
            className="mt-2 bg-gray-300 text-black px-4 py-2 rounded w-full"
          >
            ⬅ Return to Checkout
          </button>
        </>
      )}
    </div>
  );
};

export default ReturnManual;