import { useEffect, useState } from 'react';
import API from '../services/api';
import type { ReturnItemUI } from '@/schemas/return';

const reasons = ['Damaged', 'Expired', 'Customer Changed Mind', 'Other'];

type Props = {
  items: ReturnItemUI[];
  source?: 'manual' | 'sale';
  saleId?: number | null;
  clearItems: () => void;
  onSuccess?: () => void;
  onSubmit?: (items: ReturnItemUI[]) => void;
};

const ReturnCart: React.FC<Props> = ({
  items,
  source = 'manual',
  saleId = null,
  clearItems,
  onSuccess,
  onSubmit,
}) => {
  const [returnList, setReturnList] = useState<ReturnItemUI[]>([]);

  useEffect(() => {
    const enriched = items.map((item) => ({
      ...item,
      quantity: item.quantity ?? 1,
      reason: item.reason ?? '',
      notes: item.notes ?? '',
      restock: item.restock !== false,
    }));
    setReturnList(enriched);
  }, [items]);

  const handleQtyChange = (index: number, qty: number) => {
    const updated = [...returnList];
    updated[index].quantity = qty;
    setReturnList(updated);
  };

  const handleReasonChange = (index: number, reason: string) => {
    const updated = [...returnList];
    updated[index].reason = reason;
    setReturnList(updated);
  };

  const handleNotesChange = (index: number, notes: string) => {
    const updated = [...returnList];
    updated[index].notes = notes;
    setReturnList(updated);
  };

  const handleRestockToggle = (index: number) => {
    const updated = [...returnList];
    updated[index].restock = !updated[index].restock;
    setReturnList(updated);
  };

  const handleRemove = (index: number) => {
    const updated = [...returnList];
    updated.splice(index, 1);
    setReturnList(updated);
  };

  const handleSubmitReturn = async () => {
    if (returnList.length === 0) {
      alert('No items to return.');
      return;
    }

    if (source === 'sale' && !saleId) {
      alert('Missing Sale ID.');
      return;
    }

    const payload = {
      sale_id: saleId || 0,
      returns: returnList.map((item) => ({
        product_id: item.product_id || item.id,
        quantity: item.quantity,
        reason: item.reason || 'Unspecified',
        notes: item.reason === 'Other' ? item.notes : '',
        restock: item.restock !== false,
      })),
    };

    try {
      await API.post('/returns', payload);
      alert('✅ Return processed successfully.');
      clearItems();
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error('❌ Failed to submit return:', err);
      alert('Error processing return.');
    }
  };

  const subtotal = returnList.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  const tax = subtotal * 0.06;
  const total = subtotal + tax;

  return (
    <div className="mt-4">
      {returnList.map((item, idx) => (
        <div key={idx} className="border p-2 my-2 rounded">
          <p className="font-semibold">{item.name}</p>
          <p className="text-sm text-gray-500">SKU: {item.sku}</p>
          <p className="text-sm">Unit Price: ${item.price.toFixed(2)}</p>

          <div className="mt-2">
            <label className="block text-sm mb-1">Qty</label>
            <input
              type="number"
              min="1"
              value={item.quantity}
              onChange={(e) => handleQtyChange(idx, parseInt(e.target.value))}
              className="p-1 border rounded"
            />
          </div>

          <div className="mt-2">
            <label className="block text-sm mb-1">Reason</label>
            <select
              value={item.reason}
              onChange={(e) => handleReasonChange(idx, e.target.value)}
              className="border p-2 rounded"
            >
              <option value="">-- Select --</option>
              {reasons.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {item.reason === 'Other' && (
            <div className="mt-2">
              <label className="block text-sm mb-1">Notes</label>
              <input
                type="text"
                value={item.notes}
                onChange={(e) => handleNotesChange(idx, e.target.value)}
                placeholder="Enter notes"
                className="border p-2 rounded"
              />
            </div>
          )}

          <div className="flex items-center mt-2">
            <input
              type="checkbox"
              checked={item.restock}
              onChange={() => handleRestockToggle(idx)}
              className="mr-2"
            />
            <label>Restock item</label>
            <button onClick={() => handleRemove(idx)} className="text-red-600 ml-4">
              ❌ Remove
            </button>
          </div>
        </div>
      ))}

      {returnList.length > 0 && (
        <div className="mt-4">
          <p>Subtotal: ${subtotal.toFixed(2)}</p>
          <p>Tax (6%): ${tax.toFixed(2)}</p>
          <p>Total: ${total.toFixed(2)}</p>

          <button
            onClick={onSubmit ? () => onSubmit(returnList) : handleSubmitReturn}
            className="mt-3 bg-red-600 text-white px-4 py-2 rounded"
          >
            Submit Return
          </button>
        </div>
      )}
    </div>
  );
};

export default ReturnCart;
