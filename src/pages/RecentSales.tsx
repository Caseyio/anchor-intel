// ✅ File: src/pages/RecentSales.tsx
import { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import ProductSearchBox from '../components/ProductSearchBox';
import ProductSuggestions from '../components/ProductSuggestions';
import ReturnCart from '../components/ReturnCart';
import { ProductOut } from '../schemas/product';
import type { ReturnItemUI } from '@/schemas/return';

const RecentSales = () => {
  const [mode, setMode] = useState<'sale' | 'manual'>('sale');
  const [saleId, setSaleId] = useState('');
  const [saleItems, setSaleItems] = useState<ReturnItemUI[]>([]);
  const [products, setProducts] = useState<ProductOut[]>([]);
  const [search, setSearch] = useState('');
  const [returnItems, setReturnItems] = useState<ReturnItemUI[]>([]);
  const searchRef = useRef<HTMLInputElement>(null);

  const navigate = useNavigate();

  useEffect(() => {
    API.get('/products')
      .then((res) => setProducts(res.data))
      .catch((err) => console.error('❌ Failed to fetch products:', err));
  }, []);

  const handleLoadSaleItems = async () => {
    if (!saleId) {
      alert('Please enter a valid Sale ID.');
      return;
    }

    setSaleItems([]);

    try {
      const [saleRes, productRes] = await Promise.all([
        API.get(`/sales/sales/${saleId}`),
        products.length === 0 ? API.get('/products') : Promise.resolve({ data: products }),
      ]);

      const allProducts: ProductOut[] = productRes.data;

      const enriched: ReturnItemUI[] = saleRes.data.items.map((item: any) => {
        const full = allProducts.find((p: ProductOut) => p.id === item.product_id);
        return {
          id: full?.id ?? item.product_id,
          product_id: item.product_id,
          name: full?.name || 'Unnamed Product',
          sku: full?.sku || 'N/A',
          price: full?.price ?? item.price ?? 0,
          quantity: item.quantity ?? 1,
          reason: '',
          notes: '',
          restock: true,
        };
      });

      setProducts(allProducts);
      setSaleItems(enriched);
    } catch (err) {
      console.error('❌ Failed to load sale:', err);
      alert('Could not find sale.');
      setSaleItems([]);
    }
  };

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleBack();
    };
    const listener = handleKey as unknown as EventListener;
    window.addEventListener('keydown', listener);
    return () => window.removeEventListener('keydown', listener);
  }, []);

  const handleManualSelect = (product: ProductOut) => {
    const exists = returnItems.find((item) => item.product_id === product.id);
    if (!exists) {
      setReturnItems([
        ...returnItems,
        {
          id: product.id,
          product_id: product.id,
          name: product.name,
          sku: product.sku,
          quantity: 1,
          price: product.price,
          reason: '',
          notes: '',
          restock: true
        },
      ]);
    }
  };

  const handleSubmitReturn = async (items: ReturnItemUI[]) => {
    if (items.length === 0 || (mode === 'sale' && !saleId)) {
      alert('No items or missing sale ID.');
      return;
    }

    const payload = {
      sale_id: parseInt(saleId) || undefined,
      returns: items.map(({ product_id, quantity, reason, notes, restock }) => ({
        product_id,
        quantity,
        reason: reason || 'Unspecified',
        notes: reason === 'Other' ? notes : '',
        restock: restock !== false
      })),
    };

    try {
      await API.post('/returns', payload);
      alert('✅ Return processed successfully.');
      setSaleItems([]);
      setReturnItems([]);
      setSearch('');
      setSaleId('');
    } catch (err) {
      console.error('❌ Return failed:', err);
      alert('Error processing return.');
    }
  };

  const handleBack = () => {
    setSaleId('');
    setReturnItems([]);
    setSaleItems([]);
    setSearch('');
    navigate('/pos');
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Return Product</h1>
        <button
          onClick={handleBack}
          className="text-sm bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
        >
          ← Back to Checkout
        </button>
      </div>

      <div className="mb-4 flex gap-4">
        <button
          onClick={() => setMode('sale')}
          className={`px-4 py-2 rounded ${mode === 'sale' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
        >
          Return by Sale ID
        </button>
        <button
          onClick={() => setMode('manual')}
          className={`px-4 py-2 rounded ${mode === 'manual' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
        >
          Manual Return (Search)
        </button>
      </div>

      {mode === 'sale' ? (
        <div>
          <div className="mb-4 flex items-center gap-2">
            <label className="block font-semibold">Sale ID</label>
            <input
              type="number"
              value={saleId}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setSaleId(e.target.value)}
              className="border p-2 rounded w-32"
            />
            <button
              onClick={handleLoadSaleItems}
              className="bg-blue-600 text-white px-4 py-2 rounded"
            >
              Load Sale Items
            </button>
          </div>

          {saleItems.length > 0 && (
            <ReturnCart
              items={saleItems}
              source="sale"
              saleId={parseInt(saleId) || undefined}
              clearItems={() => setSaleItems([])}
              onSubmit={handleSubmitReturn}
            />
          )}
        </div>
      ) : (
        <div>
          <ProductSearchBox search={search} setSearch={setSearch} searchRef={searchRef} />
          {search.length > 0 && (
            <ProductSuggestions
              products={products.filter((p) =>
                p.name.toLowerCase().includes(search.toLowerCase()) ||
                p.sku.toLowerCase().includes(search.toLowerCase())
              )}
              onSelect={handleManualSelect}
              search={search}
              setSearch={setSearch}
              searchRef={searchRef}
            />
          )}

          {returnItems.length > 0 && (
            <ReturnCart
              items={returnItems}
              source="manual"
              clearItems={() => setReturnItems([])}
              onSubmit={handleSubmitReturn}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default RecentSales;