import { useEffect, useState } from "react";
import "./App.css";
import { api, getDeviceId } from "./api";
import type { Health } from "./types";

function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [savedCount, setSavedCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .health()
      .then(setHealth)
      .catch((err: Error) => setError(err.message));

    // Tests that the X-Device-Id header is accepted
    api
      .listMedicines()
      .then((data) => setSavedCount(data.medicines.length))
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main>
      <h1>MediClear</h1>
      {error && <p>❌ {error}</p>}
      {!error && !health && <p>Checking connection…</p>}
      {health && (
        <p>
          ✅ Backend is {health.status}: {health.drugs} medicines,{" "}
          {health.brands} brands loaded.
        </p>
      )}
      {savedCount !== null && (
        <p>Saved medicines on this device: {savedCount}</p>
      )}
      <p>Device ID: {getDeviceId()}</p>
    </main>
  );
}

export default App;
