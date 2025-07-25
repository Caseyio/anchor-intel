import React, {
  useState,
  useEffect,
  useRef,
  KeyboardEvent,
  ChangeEvent,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { motion } from 'framer-motion';
import { fade, pop } from '@/components/modalVariants';
import API from '@/services/api'; // ✅ your centralized Axios instance

interface Product {
  id: number;
  name: string;
  sku: string;
}

interface Sale {
  id: number;
  timestamp: string;
}

const SearchReceiptsByProduct: React.FC = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [sales, setSales] = useState<Sale[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [showSearchButton, setShowSearchButton] = useState(false);
  const [receiptMode, setReceiptMode] = useState(false);
  const [canRefocus, setCanRefocus] = useState(true);

  const inputRef = useRef<HTMLInputElement>(null);
  const searchButtonRef = useRef<HTMLButtonElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (canRefocus) inputRef.current?.focus();
  }, [canRefocus]);

  const handleKey = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      if (receiptMode) {
        setReceiptMode(false);
        setSales([]);
        setSelectedProduct(null);
        setQuery('');
        setShowSearchButton(false);
        setHighlightedIndex(-1);
        setCanRefocus(true);
      } else {
        navigate(-1);
      }
    } else if (e.key === ' ' && receiptMode) {
      e.preventDefault();
      window.print();
    } else if (
      e.key === ' ' &&
      selectedProduct &&
      !receiptMode &&
      sales.length === 0 &&
      showSearchButton
    ) {
      e.preventDefault();
      searchButtonRef.current?.click();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const max = selectedProduct ? sales.length : suggestions.length;
      setHighlightedIndex((prev) => (max > 0 ? (prev + 1) % max : -1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const max = selectedProduct ? sales.length : suggestions.length;
      setHighlightedIndex((prev) => (max > 0 ? (prev - 1 + max) % max : -1));
    } else if (e.key === 'Enter' || e.key === ' ') {
      if (highlightedIndex >= 0) {
        e.preventDefault();
        if (!selectedProduct && suggestions.length > 0) {
          handleProductSelect(suggestions[highlightedIndex]);
        } else if (selectedProduct && sales.length > 0) {
          handleSaleClick(sales[highlightedIndex].id);
        }
      }
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKey as any);
    return () => window.removeEventListener('keydown', handleKey as any);
  }, [suggestions, sales, highlightedIndex, selectedProduct, receiptMode, showSearchButton]);

  const fetchSuggestions = async () => {
    if (!query) {
      setSuggestions([]);
      return;
    }
    try {
      const res = await API.get<Product[]>(`/products/products/search`, {
        params: { query },
      });
      setSuggestions(res.data);
      setHighlightedIndex(-1);
    } catch (err) {
      console.error('❌ Failed to fetch suggestions:', err);
      setSuggestions([]);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, [query]);

  const fetchSales = async () => {
    if (!selectedProduct) return;
    setShowSearchButton(true);
    try {
      const res = await API.get<Sale[]>(`/sales/sales/by-product`, {
        params: { query: selectedProduct.name },
      });
      setSales(res.data);
      setHighlightedIndex(0);
    } catch (err) {
      console.error('❌ Failed to fetch sales:', err);
      setSales([]);
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setSelectedProduct(null);
    setSales([]);
    setShowSearchButton(false);
    setHighlightedIndex(-1);
    setCanRefocus(true);
  };

  const handleProductSelect = (product: Product) => {
    setSelectedProduct(product);
    setQuery('');
    setSuggestions([]);
    setHighlightedIndex(-1);
    setCanRefocus(false);
  };

  const handleSaleClick = (saleId?: number) => {
    if (!saleId) return;
    navigate(`/receipt/sale/${saleId}`);
    setReceiptMode(true);
  };

  return (
    <motion.div
      className="p-8 max-w-3xl mx-auto"
      variants={fade}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <h1 className="text-3xl font-bold text-center mb-4">🔍 Search Receipts by Product</h1>
      <div className="flex justify-center mb-4">
        <input
          type="text"
          ref={inputRef}
          value={query}
          onChange={handleInputChange}
          placeholder="Search or Scan Product"
          className="border border-gray-300 rounded px-3 py-2 w-80 font-mono text-lg"
        />
      </div>

      {suggestions.length > 0 && !selectedProduct && (
        <motion.ul
          className="border border-gray-300 rounded max-w-md mx-auto bg-white list-none"
          variants={pop}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          {suggestions.map((product, index) => (
            <li
              key={product.id}
              onClick={() => handleProductSelect(product)}
              className={`px-4 py-2 cursor-pointer font-mono text-lg text-center ${
                index === highlightedIndex ? 'bg-gray-200' : ''
              }`}
            >
              {product.name} ({product.sku})
            </li>
          ))}
        </motion.ul>
      )}

      {selectedProduct && (
        <motion.div
          className="max-w-md mx-auto mt-4"
          variants={pop}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          <div className="bg-white p-3 rounded text-center shadow text-lg font-mono">
            {selectedProduct.name} ({selectedProduct.sku})
          </div>
          <button
            ref={searchButtonRef}
            onClick={fetchSales}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded w-full"
          >
            🔍 Search Receipts
          </button>
        </motion.div>
      )}

      {selectedProduct && sales.length > 0 && (
        <motion.div
          className="max-w-md mx-auto mt-6"
          variants={pop}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          <h3 className="text-lg font-semibold mb-2">
            Receipts for <strong>{selectedProduct.name}</strong>:
          </h3>
          <ul>
            {sales.map((sale, index) => (
              <li
                key={sale.id}
                onClick={() => handleSaleClick(sale.id)}
                className={`px-4 py-2 cursor-pointer rounded font-mono ${
                  index === highlightedIndex ? 'bg-gray-200' : ''
                }`}
              >
                <strong>Sale #{sale.id}</strong> ·{' '}
                {format(new Date(sale.timestamp), 'MM/dd/yyyy, h:mm a')}
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {selectedProduct && sales.length === 0 && showSearchButton && (
        <p className="text-center text-gray-600 mt-4">
          No matching receipts found for{' '}
          <strong>{selectedProduct.name}</strong>.
        </p>
      )}
    </motion.div>
  );
};

export default SearchReceiptsByProduct;
