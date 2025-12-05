import React, { useEffect, useState } from "react";

function DailySpend() {
  const [spends, setSpends] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/daily-spend/")
      .then((res) => res.json())
      .then((data) => setSpends(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div>
      <h2>Brand Spend Amounts</h2>
      <ul>
        {spends.map((spend) => (
          <li key={spend.BRAND_ID}>
            {spend.BRAND_NAME} - {spend.SPEND_AMOUNT}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DailySpend;
