import UploadPdf from "../components/UploadPdf";
import Navbar from "../components/Navbar";
import { parseCookies } from "nookies";

export default function Home({ user }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      <div className="flex items-center justify-center py-8">
        <UploadPdf />
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