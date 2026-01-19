"use client";

import { useState } from "react";

export default function LanguageSelector() {
  const [language, setLanguage] = useState("en");

  return (
    <div className="mb-4 text-sm">
      <label htmlFor="language" className="mr-2 font-medium">
        Language:
      </label>
      <select
        id="language"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="border p-1 rounded"
      >
        <option value="en">English</option>
        <option value="fr">Français</option>
        <option value="es">Español</option>
        <option value="de">Deutsch</option>
        <option value="zh">中文</option>
      </select>
    </div>
  );
}
