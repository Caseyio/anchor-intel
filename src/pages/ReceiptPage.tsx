import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SaleOut, validateSaleOut } from '../schemas'; // ✅ zod + type safety
import API from '../services/api'; // ✅ custom axios instance
import ReceiptComponent from '../components/ReceiptComponent';

const ReceiptPage = () => {
  const { saleId } = useParams<{ saleId: string }>();
  const [sale, setSale] = useState<SaleOut | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSale = async () => {
      try {
        const res = await API.get(`/sales/sales/${saleId}`);
        const parsed = validateSaleOut(res.data);
        if (!parsed) {
          setError('❌ Invalid receipt format.');
          return;
        }
        setSale(parsed);
        setError('');
      } catch (err) {
        console.error('❌ Failed to fetch sale:', err);
        setError('Failed to load receipt.');
        setSale(null);
      }
    };

    fetchSale();
  }, [saleId]);

  if (error) {
    return (
      <div className="text-center mt-8 text-sm text-red-600">
        {error}
      </div>
    );
  }

  if (!sale) {
    return (
      <div className="text-center mt-8 text-sm text-gray-500">
        Loading receipt...
      </div>
    );
  }

  return <ReceiptComponent sale={sale} onBack={() => navigate(-1)} />;
};

export default ReceiptPage;
