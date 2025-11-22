import React, { useState, useEffect } from "react";

function SummaryStats() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Format numbers with commas and 2 decimals
  const formatCurrency = (num) => {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const formatInteger = (num) => {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString();
  };

  useEffect(() => {
    fetch("http://localhost:5001/summary/")
      .then((response) => response.json())
      .then((data) => {
        setSummary(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Error fetching summary stats");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading summary statistics...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      {/* Overall Stats */}
      <h2>Overall Spend Statistics</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Total Spend</td>
            <td>${formatCurrency(summary?.overall_stats?.total_spend)}</td>
          </tr>
          <tr>
            <td>Average Transaction</td>
            <td>${formatCurrency(summary?.overall_stats?.avg_transaction_amount)}</td>
          </tr>
          <tr>
            <td>Max Spend</td>
            <td>${formatCurrency(summary?.overall_stats?.max_spend)}</td>
          </tr>
          <tr>
            <td>Min Spend</td>
            <td>${formatCurrency(summary?.overall_stats?.min_spend)}</td>
          </tr>
          <tr>
            <td>Number of Transactions</td>
            <td>{formatInteger(summary?.overall_stats?.num_transactions)}</td>
          </tr>
        </tbody>
      </table>

      {/* Top Brands */}
      <h2>Top Brands by Spend</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Brand</th>
            <th>Total Spend</th>
            <th>Average Spend</th>
            <th>Transactions</th>
          </tr>
        </thead>
        <tbody>
          {summary?.top_brands?.map((brand) => (
            <tr key={brand.brand_name}>
              <td>{brand.brand_name}</td>
              <td>${formatCurrency(brand.total_spend)}</td>
              <td>${formatCurrency(brand.avg_spend)}</td>
              <td>{formatInteger(brand.num_transactions)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Spend by Industry */}
      <h2>Spend by Industry</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Industry</th>
            <th>Total Spend</th>
          </tr>
        </thead>
        <tbody>
          {summary?.spend_by_industry?.map((row) => (
            <tr key={row.industry_name}>
              <td>{row.industry_name}</td>
              <td>${formatCurrency(row.total_spend)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Spend by State */}
      <h2>Spend by State</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>State</th>
            <th>Total Spend</th>
          </tr>
        </thead>
        <tbody>
          {summary?.spend_by_state?.map((row) => (
            <tr key={row.state_abbr}>
              <td>{row.state_abbr}</td>
              <td>${formatCurrency(row.total_spend)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Transaction Count by Industry */}
      <h2>Transaction Count by Industry</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Industry</th>
            <th>Transaction Count</th>
          </tr>
        </thead>
        <tbody>
          {summary?.tx_count_by_industry?.map((row) => (
            <tr key={row.industry_name}>
              <td>{row.industry_name}</td>
              <td>{formatInteger(row.transaction_count)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SummaryStats;
