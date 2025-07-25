// src/components/ProductSuggestions.tsx
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fade } from './modalVariants';
import type { ProductOut } from '@/schemas/product';

type Props = {
  products?: ProductOut[];
  onSelect: (product: ProductOut) => void;
  search: string;
  setSearch: (val: string) => void;
  searchRef: React.MutableRefObject<HTMLInputElement | null>;
};

const ProductSuggestions: React.FC<Props> = ({
  products = [],
  onSelect,
  search,
  setSearch,
  searchRef,
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [hideSuggestions, setHideSuggestions] = useState(false);
  const visibleProducts = products.slice(0, 5);

  useEffect(() => {
    if (hideSuggestions) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!visibleProducts.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % visibleProducts.length);
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev === 0 ? visibleProducts.length - 1 : prev - 1
        );
      }

      if (e.key === ' ') {
        e.preventDefault();
        const selected = visibleProducts[selectedIndex];
        if (selected) {
          onSelect(selected);
          setSearch('');
          setHideSuggestions(true);
          searchRef.current?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [visibleProducts, selectedIndex, onSelect, setSearch, searchRef, hideSuggestions]);

  useEffect(() => {
    setSelectedIndex(0);
    setHideSuggestions(false);
  }, [search]);

  if (!visibleProducts.length || hideSuggestions) return null;

  return (
    <div className="bg-white shadow border rounded mb-4">
      <AnimatePresence>
        {visibleProducts.map((product, index) => (
          <motion.div
            key={product.id}
            onClick={() => {
              onSelect(product);
              setSearch('');
              setHideSuggestions(true);
              searchRef.current?.focus();
            }}
            className={`p-2 cursor-pointer flex justify-between transition-colors ${
              index === selectedIndex
                ? 'bg-muted text-foreground'
                : 'hover:bg-muted/50'
            }`}
            variants={fade}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <span>{product.name}</span>
            <span>${product.price.toFixed(2)}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ProductSuggestions;
