import { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import API from '../services/api'; // ✅ custom axios instance with /api prefix

interface CashierSession {
  cashier_name?: string;
  opened_at?: string;
  closed_at?: string;
  cash_difference?: number | string;
  is_over_short?: boolean;
}

interface TopSeller {
  name?: string;
  units_sold: number;
}

interface ZReportData {
  total_sales: number;
  total_cash: number;
  total_card: number;
  total_returns: number;
  sessions: CashierSession[];
  top_sellers: TopSeller[];
}

export default function ManagerZReport() {
  const [reportDate, setReportDate] = useState(() =>
    format(new Date(), 'yyyy-MM-dd')
  );
  const [report, setReport] = useState<ZReportData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await API.get(`/manager_closeout/zreport`, {
        params: { report_date: reportDate },
      });
      setReport(res.data);
    } catch (err) {
      console.error('❌ Failed to fetch report', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [reportDate]);

  const downloadCSV = () => {
    const url = API.getUri({
      url: '/manager_closeout/zreport/export',
      params: { report_date: reportDate },
    });
    window.open(url, '_blank');
  };

  const downloadPDF = () => {
    const url = API.getUri({
      url: '/manager_closeout/zreport/pdf',
      params: { report_date: reportDate },
    });
    window.open(url, '_blank');
  };

  return (
    <div className="p-4 max-w-5xl mx-auto font-mono">
      <h1 className="text-2xl font-bold mb-4">Manager Z-Report</h1>

      <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <label className="flex items-center gap-2">
          <span className="font-medium">Select Date:</span>
          <input
            type="date"
            value={reportDate}
            onChange={(e) => setReportDate(e.target.value)}
            className="border rounded px-2 py-1"
          />
        </label>

        <div className="flex gap-2">
          <button
            onClick={downloadCSV}
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
          >
            Download CSV
          </button>
          <button
            onClick={downloadPDF}
            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
          >
            Download PDF
          </button>
        </div>
      </div>

      {loading && <p>Loading report...</p>}

      {report && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <KPI label="Total Sales" value={`$${report.total_sales.toFixed(2)}`} />
            <KPI label="Cash" value={`$${report.total_cash.toFixed(2)}`} />
            <KPI label="Card" value={`$${report.total_card.toFixed(2)}`} />
            <KPI label="Returns" value={`$${report.total_returns.toFixed(2)}`} />
          </div>

          <div>
            <h2 className="font-semibold text-lg mb-2">Cashier Sessions</h2>
            <table className="w-full border text-sm">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border px-2 py-1">Cashier</th>
                  <th className="border px-2 py-1">Opened</th>
                  <th className="border px-2 py-1">Closed</th>
                  <th className="border px-2 py-1">Diff</th>
                  <th className="border px-2 py-1">Over/Short</th>
                </tr>
              </thead>
              <tbody>
                {report.sessions.map((s, idx) => (
                  <tr key={idx}>
                    <td className="border px-2 py-1">{s.cashier_name || '—'}</td>
                    <td className="border px-2 py-1">
                      {s.opened_at ? format(parseISO(s.opened_at), 'PPP p') : '—'}
                    </td>
                    <td className="border px-2 py-1">
                      {s.closed_at ? format(parseISO(s.closed_at), 'PPP p') : '—'}
                    </td>
                    <td className="border px-2 py-1">
                      ${parseFloat(String(s.cash_difference || 0)).toFixed(2)}
                    </td>
                    <td className="border px-2 py-1">
                      {s.is_over_short ? 'YES' : 'NO'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
            <h2 className="font-semibold text-lg mb-2">Top Sellers</h2>
            <ul className="list-disc ml-5 text-sm">
              {report.top_sellers.map((p, idx) => (
                <li key={idx}>
                  {p.name || 'Unnamed Product'} — {p.units_sold} sold
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

interface KPIProps {
  label: string;
  value: string;
}

function KPI({ label, value }: KPIProps) {
  return (
    <div className="bg-gray-50 border p-3 rounded shadow text-center">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
