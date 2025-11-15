"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const QRCodeReact = dynamic(() => import("qrcode.react"), { ssr: false });

export function QRCode() {
  const [url, setUrl] = useState<string>("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      setUrl(`${window.location.origin}/mobile`);
    }
  }, []);

  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-300">
        Join as a Driver
      </h2>
      {url ? (
        <QRCodeReact value={url} size={160} />
      ) : (
        <div className="h-[160px] w-[160px] animate-pulse rounded-md bg-slate-800" />
      )}
      <p className="mt-3 text-center text-xs text-slate-400">
        Scan this QR code on your phone to open the mobile driver view.
      </p>
    </div>
  );
}

export default QRCode;
