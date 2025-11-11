import React, { useEffect, useState } from "react";

function BrandList() {
  const [brands, setBrands] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/brands/")
      .then((res) => res.json())
      .then((data) => setBrands(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div>
      <h2>Brands</h2>
      <ul>
        {brands.map((brand) => (
          <li key={brand.BRAND_ID}>
            {brand.BRAND_NAME} - {brand.INDUSTRY_NAME}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BrandList;
