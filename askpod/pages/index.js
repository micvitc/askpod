//// filepath: /home/ameen/projects/MIC/askpod/askpod/pages/index.js
import UploadPdf from "../components/UploadPdf";
import Navbar from "../components/Navbar";
import Sidebar from "@/components/Sidebar";
import Chat from "@/components/Chat";
import { parseCookies } from "nookies";

export default function Home({ user }) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar user={user} />
      <div className="flex flex-1">
        {/* Left Sidebar: List sessions */}
        <aside className="w-80 bg-white border-r p-4 flex flex-col">
          <Sidebar />
        </aside>
        {/* Middle Content: Chat interface */}
        <main className="flex-1 p-4 flex flex-col">
          <div className="flex-1">
            <Chat />
          </div>
        </main>
        {/* Right Sidebar: Upload PDF to create a new session */}
        <aside className="w-80 bg-white border-l p-4 flex flex-col justify-end">
          <UploadPdf />
        </aside>
      </div>
    </div>
  );
}

export async function getServerSideProps(context) {
  const { token } = parseCookies(context);

  // If token is not available, redirect to login
  if (!token) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }

  // Validate the token via the FastAPI endpoint
  const res = await fetch("http://localhost:8000/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });

  // If token is invalid or expired, redirect to login
  if (res.status !== 200) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }

  const user = await res.json();

  return {
    props: { user },
  };
}