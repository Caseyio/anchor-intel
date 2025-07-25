import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';

import POS from './pages/POS';
import CashierReceipt from './components/CashierReceipt';
import CustomerReceipt from './components/CustomerReceipt';
import RecentSales from './pages/RecentSales';
import ReturnManual from './pages/ReturnManual';
import { AppShell } from './components/layout/AppShell';
import ReturnFromSale from './pages/ReturnFromSale';
import SearchReceipts from './pages/SearchReceipts';
import SearchReceiptsByProduct from './pages/SearchReceiptsByProduct';
import ReceiptPage from './pages/ReceiptPage';
import CashierCloseout from './pages/CashierCloseout'
import ManagerCloseout from './pages/ManagerCloseout'
import Analytics from './pages/Analytics'
import AnalyticsV2 from './pages/AnalyticsV2'


function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />

          <Route
            element={
              <ProtectedRoute>
                <AppShell>
                  <Outlet />
                </AppShell>

              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/pos" element={<POS />} />
            <Route path="/receipt/cashier" element={<CashierReceipt />} />
            <Route path="/receipt/customer" element={<CustomerReceipt />} />
            <Route path="/sales/recent" element={<RecentSales />} />
            <Route path="/return-sale" element={<ReturnFromSale />} />
            <Route path="/return" element={<ReturnFromSale />} />
            <Route path="/return-manual" element={<ReturnManual />} />
            <Route path="/receipt/search" element={<SearchReceipts />} />
            <Route path="/receipt/search-product" element={<SearchReceiptsByProduct />} />
            <Route path="/receipt/sale/:saleId" element={<ReceiptPage />} />
            <Route path="/receipt/last" element={<CashierReceipt />} />
            <Route path="/cashier-closeout" element={<CashierCloseout />} />
            <Route path="/manager-closeout" element={<ManagerCloseout />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/analyticsv2" element={<AnalyticsV2 />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
