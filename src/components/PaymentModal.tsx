import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { fade } from '../components/modalVariants';

type PaymentModalProps = {
  onConfirm: (method: 'card') => void;
  onCancel: () => void;
  onCash: () => void;
};

const PaymentModal = ({ onConfirm, onCancel, onCash }: PaymentModalProps) => {
  useEffect(() => {
    const esc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    };
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', esc);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', esc);
    };
  }, [onCancel]);

  const modalRoot = document.getElementById('modal-root');
  if (!modalRoot) return null;

  return createPortal(
    <motion.div
      key="modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      variants={fade}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="bg-white p-6 rounded shadow-lg text-center max-w-sm w-full">
        <h2 className="text-xl font-bold mb-4">Payment Method</h2>

        <button
          onClick={onCash}
          className="bg-green-600 text-white px-4 py-2 rounded mr-2"
        >
          💵 Cash (Shift)
        </button>

        <button
          onClick={() => onConfirm('card')}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          💳 Card (Space)
        </button>

        <button
          onClick={onCancel}
          className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400 mt-4"
        >
          ❌ Cancel (Esc)
        </button>
      </div>
    </motion.div>,
    modalRoot
  );
};

export default PaymentModal;
