import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { fade } from '../components/modalVariants';

interface CashConfirmModalProps {
  onComplete: () => void;
  onCancel: () => void;
  onChangeMethod: () => void;
}

const CashConfirmModal: React.FC<CashConfirmModalProps> = ({
  onComplete,
  onCancel,
  onChangeMethod,
}) => {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onChangeMethod();
      } else if (e.key === ' ') {
        e.preventDefault();
        onComplete();
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onComplete, onCancel, onChangeMethod]);

  return createPortal(
    <motion.div
      key="cash-confirm-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      variants={fade}
      initial="hidden"
      animate="visible"
      exit="hidden"
    >
      <div className="bg-white p-6 rounded shadow-lg text-center max-w-sm w-full">
        <h2 className="text-xl font-bold mb-4">Confirm Cash Payment</h2>
        <button
          onClick={onComplete}
          className="bg-green-600 text-white px-4 py-2 rounded mr-2"
        >
          ✅ Sale Complete (Space)
        </button>
        <button
          onClick={onCancel}
          className="bg-gray-400 text-white px-4 py-2 rounded mr-2"
        >
          ❌ Cancel Sale
        </button>
        <button
          onClick={onChangeMethod}
          className="mt-4 text-sm text-blue-600"
        >
          🔁 Change Payment Method (Esc)
        </button>
      </div>
    </motion.div>,
    document.getElementById('modal-root') as HTMLElement
  );
};

export default CashConfirmModal;
