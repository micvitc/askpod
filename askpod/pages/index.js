// pages/index.js
import UploadPdf from "../components/UploadPdf";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <UploadPdf />
    </div>
  );
}
