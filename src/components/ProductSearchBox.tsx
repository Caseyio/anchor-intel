// src/components/ProductSearchBox.tsx
import React from 'react'

type Props = {
  search: string
  setSearch: (val: string) => void
  searchRef: React.MutableRefObject<HTMLInputElement | null>
}

const ProductSearchBox: React.FC<Props> = ({ search, setSearch, searchRef }) => {
  return (
    <input
      ref={searchRef}
      type="text"
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      className="w-full px-3 py-2 border rounded focus:outline-none focus:ring focus:ring-slate-300"
      placeholder="Scan or search products..."
    />
  )
}

export default ProductSearchBox
